# Relatório – Assistente RAG da Central de Ajuda da Sympla

**Disciplina:** Tecnologias Emergentes – PUC-Campinas · **Atividade 4**
**Dupla:** Lucas ______ e ______ · **Data:** novembro de 2026

> Todos os números deste relatório vêm de uma execução real no Google Colab (CPU, 27/11/2026) com `bash avaliacao/rodar_tudo.sh`. As saídas completas estão em `avaliacao/resultados/`.

## 1. Problema e usuário

A Sympla é uma das maiores plataformas brasileiras de venda de ingressos e inscrições para eventos. Quem compra um ingresso costuma ter dúvidas repetitivas: prazo para cancelar, como funciona o reembolso em cada forma de pagamento, troca de titularidade, taxas, meia-entrada, parcelamento. As respostas existem na Central de Ajuda, mas estão espalhadas em dezenas de artigos, e o comprador precisa achar o artigo certo.

**Usuário:** o comprador de ingressos (e, secundariamente, a equipe de atendimento, que pode usar o assistente para responder chamados mais rápido).

**Por que RAG:** um LLM sozinho não conhece as regras atuais da Sympla e tende a inventar prazos e valores (por exemplo, "reembolso em 30 dias" ou "troca até 48 h antes"). O RAG busca primeiro os trechos certos da Central de Ajuda e manda o LLM responder só com eles, citando a fonte. Quando a base não tem a resposta, o sistema diz que não encontrou.

**Valor para o negócio:** menos chamados repetitivos no atendimento (o próprio artigo "Como falar com a Sympla" fala em retorno de até 1 dia útil, enquanto o assistente responde na hora), respostas consistentes com a política oficial e menor risco de informação errada sobre direitos do consumidor (prazo de arrependimento do CDC, reembolso).

## 2. Base de documentos

- **18 artigos públicos** da Central de Ajuda da Sympla (ajuda.sympla.com.br), em Markdown, na pasta `docs/`.
- Cada arquivo tem um cabeçalho com **título, URL de origem, data de atualização do artigo e data de acesso (13/11/2026)**.
- Coleta feita pela API pública da Central de Ajuda (Zendesk), convertendo o HTML em texto. Foram removidos elementos de navegação ("Esse artigo foi útil?", "Artigos relacionados"). O artigo de meia-entrada foi reduzido à parte nacional e a uma seleção das leis estaduais, por ser muito longo.
- Não há dados pessoais nem documentos confidenciais; os únicos contatos citados são canais públicos de atendimento.
- Temas cobertos: cancelamento e reembolso (5 artigos), reembolso por forma de pagamento, taxas, troca de titularidade, Seguro Reembolso Garantido, formas de pagamento, parcelamento, acesso aos ingressos, evento adiado/cancelado, exclusão de conta, canais de atendimento, compra por terceiros, como comprar e meia-entrada.

A lista completa com links está no README.

## 3. Arquitetura

```mermaid
flowchart LR
    subgraph Ingestão
        D[18 artigos .md<br/>título, URL, data] --> C[Chunking<br/>1000 car. / overlap 150]
        C --> E1[Embeddings<br/>multilingual-e5-small]
        E1 --> V[(Chroma<br/>cosseno)]
    end
    subgraph Consulta
        P[Pergunta do usuário] --> E2[Embedding da pergunta]
        E2 --> R{Top-k = 3<br/>similaridade ≥ 0,89?}
        V --> R
        R -- não --> N[“Não encontrei essa informação<br/>nos documentos da Sympla.”]
        R -- sim --> PR[Prompt: responder só com o contexto,<br/>citar a fonte, admitir quando não sabe]
        PR --> L[LLM aberto<br/>Ollama qwen2.5:3b ou Qwen2.5-1.5B no Colab]
        L --> A[Resposta + fontes]
    end
```

Fluxo: os documentos são divididos em trechos, cada trecho vira um vetor e é guardado no Chroma. Na consulta, a pergunta vira um vetor, o Chroma devolve os 3 trechos mais parecidos e os que ficam abaixo do limiar são descartados. Se nenhum sobra, o sistema responde que não encontrou **sem chamar o LLM** (economiza tempo e elimina a chance de alucinação). Se sobra algum, o LLM recebe os trechos com a fonte de cada um.

Interfaces: linha de comando (`perguntar.py`), app web em Gradio (`app.py`) e notebook do Colab.

## 4. Escolhas técnicas e justificativas

### 4.1 Modelo de embeddings
Comparamos dois modelos gratuitos e multilíngues, ambos pequenos o bastante para rodar em CPU no Colab gratuito:

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensões, treinado para paráfrases em mais de 50 idiomas);
- `intfloat/multilingual-e5-small` (384 dimensões, treinado para busca: pergunta → passagem). O código adiciona automaticamente os prefixos `query:` e `passage:` que a família E5 exige.

| Modelo | Chunk | P@3 | Hit@3 | MRR |
|---|---|---|---|---|
| MiniLM-L12 | 300 / 60 | 29,6% | 72,2% | 0,562 |
| MiniLM-L12 | 600 / 100 | 25,9% | 66,7% | 0,569 |
| MiniLM-L12 | 1000 / 150 | 25,9% | 66,7% | 0,565 |
| **e5-small** | 300 / 60 | 29,6% | 77,8% | 0,613 |
| **e5-small** | 600 / 100 | **46,3%** | **88,9%** | 0,759 |
| **e5-small** | **1000 / 150** | 44,4% | **88,9%** | **0,796** |

(Métricas calculadas sobre as 18 perguntas que têm resposta na base.)

**Escolha: `multilingual-e5-small`.** Ele ganhou em todas as configurações de chunk. A diferença faz sentido: o MiniLM foi treinado para medir se duas frases dizem a mesma coisa, enquanto o E5 foi treinado justamente para ligar uma pergunta curta a um trecho que a responde, que é o caso do RAG. Com o MiniLM em chunks de 600 ou 1000, em um terço das perguntas nenhum dos 3 trechos recuperados continha a resposta.

### 4.2 Banco vetorial
Chroma: roda embutido no Python, sem servidor, persiste em disco e suporta distância de cosseno. Para 18 documentos (~110 trechos) é mais que suficiente.

### 4.3 Chunking e tamanho do trecho
O texto é dividido por parágrafos e agrupado até o tamanho-alvo; parágrafos maiores são quebrados por linha, frase e, em último caso, palavra. Cada trecho começa com o final do anterior (sobreposição), para não perder uma regra que caia na fronteira. O título do artigo e a seção são colocados na frente do texto **só no embedding**, o que ajuda trechos curtos ("Não. A troca é desabilitada 24 horas antes...") a serem achados.

Foram testados três tamanhos (sobreposição de ~15–20%):

| Configuração | Nº de trechos | Tamanho médio |
|---|---|---|
| 300 car. / overlap 60 | 217 | 247 car. |
| 600 car. / overlap 100 | 110 | 466 car. |
| 1000 car. / overlap 150 | 62 | 789 car. |

Resultado com o modelo escolhido (e5-small), incluindo k = 1 e k = 5:

| Chunk | Hit@1 | Hit@3 | Hit@5 | P@3 | MRR |
|---|---|---|---|---|---|
| 300 / 60 | 44,4% | 77,8% | 83,3% | 29,6% | 0,613 |
| 600 / 100 | 66,7% | 88,9% | 88,9% | 46,3% | 0,759 |
| 1000 / 150 | **72,2%** | 88,9% | 88,9% | 44,4% | **0,796** |

**Escolha: 1000 caracteres com sobreposição de 150.** Os trechos de 300 caracteres foram claramente piores (Hit@3 de 77,8%): nas FAQs da Sympla a pergunta e a resposta muitas vezes ficam em trechos diferentes, e o trecho recuperado "parece" certo mas não contém a regra. Entre 600 e 1000 o Hit@3 empatou (16 de 18 perguntas), e o 600 teve P@3 um pouco maior porque a mesma regra aparece em mais de um trecho com sobreposição. Ficamos com 1000 porque teve o **maior MRR (0,796)** e o maior Hit@1 (72,2% contra 66,7%): o trecho certo aparece mais vezes na 1ª posição, que é o que mais pesa para um LLM pequeno, que tende a se apoiar no primeiro trecho do contexto. O custo é um prompt maior (3 × ~800 caracteres), que o Qwen 1,5B/3B comporta sem problema. Com 62 trechos no total, a base continua pequena e a busca é instantânea.

### 4.4 Valor de k e limiar
- **k = 3**: vários temas aparecem em mais de um artigo (o prazo de 7 dias está em 4 artigos), então trazer 3 trechos aumenta a chance de o certo estar presente, sem encher o prompt de um modelo pequeno.
- **Limiar de similaridade**: o script testa limiares de 0,20 a 0,95 e escolhe o que melhor separa perguntas com resposta das sem resposta (acurácia balanceada). O limiar escolhido foi **0,89** (acurácia balanceada de 84,7%).

  | Similaridade do 1º trecho | Mínima | Máxima |
  |---|---|---|
  | 18 perguntas com resposta | 0,887 (P06) | 0,935 (P17) |
  | 4 perguntas sem resposta | 0,848 (P21) | 0,900 (P20) |

  Com 0,89, 17 das 18 perguntas com resposta passam e 3 das 4 sem resposta são barradas antes do LLM (P19, P21 e P22). Não existe limiar perfeito, porque as faixas se sobrepõem: P20 ("quanto custa a taxa em reais?") tem 0,900, mais que várias perguntas legítimas, já que o artigo de taxas fala exatamente de taxa de serviço, só que sem valores. Um ponto importante: o E5 gera similaridades comprimidas numa faixa estreita (quase tudo entre 0,85 e 0,94), por isso o limiar fica alto e qualquer diferença de 0,01 muda o resultado. Com o limiar inicial de 0,40 (pensado para o MiniLM), as 4 perguntas sem resposta passariam. O limiar é a primeira barreira contra perguntas fora da base; a segunda é o prompt, que manda o LLM recusar quando o contexto não responde.

### 4.5 LLM e prompt
- **Local:** Ollama com `qwen2.5:3b` (roda em CPU com ~4 GB de RAM).
- **Colab:** `Qwen/Qwen2.5-1.5B-Instruct` via transformers. Na nossa execução não havia GPU disponível no Colab gratuito, então tudo rodou em CPU (de 33 s a 140 s por resposta; com GPU T4 seriam poucos segundos).
- A família Qwen2.5 foi escolhida por ser aberta, ter bom desempenho em português e seguir bem instruções em tamanhos pequenos. Temperatura baixa (0,1 / greedy) para respostas estáveis.
- O prompt de sistema exige: (1) responder só com o contexto, sem inventar valores ou prazos; (2) citar a fonte no formato `Fonte: título (arquivo, data)`; (3) responder exatamente "Não encontrei essa informação nos documentos da Sympla." quando o contexto não tiver a resposta; (4) português, no máximo 4 frases.

## 5. Avaliação

### 5.1 Metodologia
- **22 perguntas de teste** (`avaliacao/perguntas_teste.json`): 18 com resposta na base e **4 sem resposta** (telefone do SAC da Sympla, valor em reais da taxa de serviço, CEO da Sympla, bilheteria física).
- Para cada pergunta foi registrada a **frase de evidência** do documento que a responde. Um trecho recuperado é relevante se contém essa frase, o que torna o gabarito independente do tamanho do chunk.
- Métricas: **precision@k** (fração dos k trechos que são relevantes), **hit@k** (pelo menos um relevante no top-k) e **MRR** (posição do primeiro relevante). Como a maioria das perguntas tem um único trecho relevante, o P@3 máximo fica perto de 33%; por isso Hit@k e MRR complementam a análise.
- Perguntas sem resposta: verifica-se se o limiar descarta todos os trechos e, com `--gerar`, se o LLM responde que não encontrou.

### 5.2 Resultados
**Recuperação** (e5-small, chunk 1000/150, k = 3, 18 perguntas com resposta): P@1 72,2%, P@3 44,4%, P@5 26,7%, Hit@1 72,2%, **Hit@3 88,9%**, Hit@5 88,9%, **MRR 0,796**. A tabela completa com os dois modelos e os três tamanhos de chunk está na seção 4.1 e em `avaliacao/resultados/comparacao_embeddings.md`.

**Geração** (Qwen2.5-1.5B-Instruct, limiar 0,89, 22 perguntas). O script marca automaticamente se o sistema respondeu quando devia e recusou quando devia: **19/22**. Conferindo cada resposta contra a resposta esperada:

| Resultado | Perguntas | Qtd. |
|---|---|---|
| Correta e completa | P01, P02, P05, P07, P09, P11, P12, P13, P14, P15, P16, P17, P18 | 13 |
| Correta, mas incompleta | P04 (omitiu que a devolução automática no Pix vale só até 90 dias da compra) | 1 |
| **Errada (alucinação)** | P03 | 1 |
| **Recusa indevida** (havia resposta) | P06 (limiar), P08 e P10 (trecho certo não recuperado) | 3 |
| Recusa correta (sem resposta na base) | P19, P21, P22 (pelo limiar, sem chamar o LLM) e P20 (o LLM recusou) | 4 |

Ou seja, **18 de 22 (82%) comportamentos corretos** na conferência manual (o automático contou 19 porque não percebe que a resposta da P03 está errada) e **nenhuma alucinação nas perguntas sem resposta**. O erro mais comum do sistema é ser conservador demais (recusar), o que é preferível a inventar.

Sobre a citação de fontes: o sistema sempre mostra os trechos recuperados (título, arquivo e data) junto com a resposta, mas o LLM só escreveu a linha "Fonte: …" pedida no prompt em 3 das 15 respostas (P04, P14 e P18). Um modelo de 1,5B não segue todas as regras do prompt com consistência; por isso a lista de fontes é montada pelo código, e não pelo LLM.

### 5.3 Análise de três erros

**Erro 1: P03 "Consigo cancelar meu pedido pelo aplicativo da Sympla?" (recuperação errada que virou alucinação).**
A resposta certa está no artigo 01: "O cancelamento deve ser feito pelo site da Sympla. A função não está disponível no aplicativo." Mas o top-3 trouxe dois trechos do artigo 05 (*política de cancelamento de pedidos*, escrito para o **organizador**) e um trecho do artigo 01 sem essa frase. Os três trechos falam muito de "cancelamento de pedidos", então a similaridade foi alta (0,910) e passou do limiar. O LLM respondeu "Sim" e descreveu o caminho do painel do organizador ("Painel do evento", "Políticas do evento") como se fosse o app do comprador. Causa: o embedding captou o tema ("cancelar pedido"), mas não o detalhe que decide a resposta ("aplicativo"), e a base mistura artigos para comprador e para organizador. Correções: adicionar o público do artigo (comprador/organizador) nos metadados e filtrar por ele; usar um reranker (cross-encoder) depois do top-k; ou reforçar no prompt que o modelo deve responder "não sei" quando o contexto não mencionar o termo-chave da pergunta.

**Erro 2: P08 "A Sympla cobra alguma coisa para trocar a titularidade?" (trecho certo fora do top-3).**
A resposta está no fim do artigo 07: "Gratuidade: não existe nenhum custo adicional cobrado pela Sympla para realização de trocas de titularidade." O sistema recuperou os trechos #00, #01 e #02 do mesmo artigo (início do texto, sobre prazos e passo a passo), todos com similaridade alta (0,921), mas nenhum com a regra. O LLM, corretamente, disse que não encontrou, então não alucinou, mas deixou de responder algo que estava na base. Causa: com o título do artigo colocado na frente de todo trecho, os trechos do mesmo artigo ficam muito parecidos entre si, e o "desempate" é feito por palavras genéricas; a pergunta usa "cobra" e o texto usa "custo adicional" e "Gratuidade". A P10 (limite de R$ 10.000 do seguro) falhou pelo mesmo motivo: o 1º trecho foi a introdução do artigo do seguro. Correções: aumentar k para 5 quando os 3 primeiros vierem do mesmo artigo; busca híbrida (BM25 + embeddings), que acharia "custo"/"cobra"; ou chunks por seção/pergunta da FAQ.

**Erro 3: P06 "Qual a diferença entre a taxa de serviço e a taxa de processamento?" (limiar rígido demais).**
O artigo 06 explica as duas taxas, e o trecho certo foi recuperado em 2º lugar, mas a similaridade do melhor trecho foi 0,887, logo abaixo do limiar de 0,89. O sistema recusou sem nem chamar o LLM. Causa: o limiar foi escolhido para barrar as perguntas sem resposta, e a P22 (bilheteria física, 0,889) e a P20 (taxa em reais, 0,900) ficam na mesma faixa de similaridade das perguntas legítimas. Baixar o limiar para 0,88 salvaria a P06, mas deixaria passar a P22 e passaria a depender só do prompt para recusar. Correções: em vez de recusar direto abaixo do limiar, mandar ao LLM com uma instrução mais rígida (zona cinzenta entre 0,86 e 0,89); calibrar o limiar com mais perguntas de teste; ou usar o score de um reranker, que costuma separar melhor "relacionado" de "responde".

## 6. Limitações e riscos

- **Base pequena e datada:** 18 artigos copiados em 13/11/2026. Se a Sympla mudar uma política, o assistente fica desatualizado até reindexar. Em produção seria preciso sincronizar com a API da Central de Ajuda periodicamente.
- **Políticas que dependem do evento:** muitas regras são definidas pelo organizador (política de cancelamento, troca de titularidade). O assistente só conhece a regra geral e deve orientar o usuário a conferir a página do evento.
- **Alucinação residual:** mesmo com o prompt, um LLM pequeno pode misturar trechos ou inventar detalhes. A citação de fonte permite conferir.
- **Assuntos jurídicos:** respostas sobre CDC e meia-entrada não substituem orientação jurídica; leis regionais foram resumidas.
- **Limiar fixo:** um único limiar não serve igualmente para todas as perguntas; perguntas curtas tendem a ter similaridade mais baixa.
- **Avaliação limitada:** 22 perguntas escritas pela própria dupla, com risco de viés (as perguntas usam termos parecidos com os do texto).
- **Uso da marca:** projeto acadêmico, não oficial; os textos são da Sympla e foram usados só para estudo.

## 7. Divisão do trabalho na dupla

*(A dupla deve conferir e ajustar esta divisão.)*

| Integrante | Responsabilidades |
|---|---|
| Lucas | coleta e preparação dos documentos, chunking e índice, avaliação e análise de erros |
| Colega | prompt e integração com o LLM (Ollama/Colab), interfaces (CLI e Gradio), relatório e demonstração |

## 8. Como reproduzir

Ver o passo a passo no `README.md` (Colab ou local com Ollama).
