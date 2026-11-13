# Assistente RAG da Central de Ajuda da Sympla

Trabalho da **Atividade 4 – Tecnologias Emergentes (PUC-Campinas)**. Sistema RAG (Retrieval-Augmented Generation) que responde perguntas de compradores de ingressos usando apenas artigos públicos da Central de Ajuda da Sympla, cita a fonte de cada resposta e diz quando não encontrou a informação.

> Projeto acadêmico, sem vínculo com a Sympla. Os documentos são páginas públicas da Central de Ajuda, copiadas em 13/11/2026 apenas para fins educacionais.

## Como funciona

```
docs/*.md ──► chunking (600 car., overlap 100) ──► embeddings multilíngues ──► Chroma
                                                                                 │
pergunta ──► embedding ──► top-k (k=3) por similaridade de cosseno ──► limiar ───┤
                                                                                 ▼
                           nenhum trecho acima do limiar? ──► "Não encontrei essa informação..."
                           senão ──► prompt (só contexto + citar fonte) ──► LLM aberto ──► resposta + fontes
```

| Etapa | Escolha |
|---|---|
| Documentos | 18 artigos da Central de Ajuda da Sympla em Markdown, com URL e data (`docs/`) |
| Chunking | por parágrafos, 600 caracteres com 100 de sobreposição; título e seção vão junto no embedding |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (gratuito, multilíngue) |
| Banco vetorial | Chroma (persistente, distância de cosseno) |
| Recuperação | top-k = 3 com limiar mínimo de similaridade (padrão 0,40; calibrado na avaliação) |
| LLM | Ollama local (`qwen2.5:3b`) ou `Qwen/Qwen2.5-1.5B-Instruct` via transformers no Google Colab |
| Interfaces | linha de comando (`perguntar.py`), app web Gradio (`app.py`) e notebook do Colab |

## Estrutura

```
docs/                     18 artigos públicos da Sympla (front matter com título, URL e datas)
src/
  config.py               parâmetros (modelo, chunk, k, limiar, LLM)
  documentos.py           leitura dos documentos e chunking com sobreposição
  indice.py               embeddings + Chroma
  recuperacao.py          busca top-k com limiar
  geracao.py              prompt e backends do LLM (Ollama / transformers)
  rag.py                  pipeline completo
indexar.py                cria os índices
perguntar.py              interface de linha de comando
app.py                    app web (Gradio) para a demonstração
avaliacao/
  perguntas_teste.json    22 perguntas de teste (18 com resposta, 4 sem resposta)
  avaliar.py              precision@k, hit@k, MRR, comparação de chunks e limiar
  resultados/             saída da avaliação (gerada ao rodar)
notebooks/RAG_Colab.ipynb roda tudo no Google Colab
relatorio/RELATORIO.md    relatório do trabalho
demo/ROTEIRO_DEMO.md      roteiro da apresentação
```

## Passo a passo

### Opção A – Google Colab (mais fácil, não precisa instalar nada)

1. Abra `notebooks/RAG_Colab.ipynb` no Colab (Arquivo > Fazer upload de notebook, ou "Abrir no GitHub").
2. Ative a GPU: Ambiente de execução > Alterar tipo > **T4 GPU**.
3. Ajuste a URL do repositório na primeira célula (ou envie o `.zip` do projeto).
4. Execute as células em ordem. A avaliação gera `avaliacao/resultados/resultados.md`.

### Opção B – Local com Ollama

Requisitos: Python 3.10+ e [Ollama](https://ollama.com) instalado.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

ollama pull qwen2.5:3b             # LLM aberto, roda em CPU (~2 GB)

python indexar.py --todos          # cria os índices (baixa o modelo de embeddings na 1ª vez)
python perguntar.py                # modo interativo
python perguntar.py "Posso cancelar só um ingresso do pedido?"
python app.py                      # app web em http://localhost:7860
```

Sem GPU nem Ollama, dá para testar só a recuperação: `python perguntar.py --sem-llm "pergunta"`.

### Avaliação

```bash
python avaliacao/avaliar.py                    # compara chunks de 300, 600 e 1000 caracteres
python avaliacao/avaliar.py --gerar            # também gera e confere as respostas do LLM
python avaliacao/avaliar.py --limiar 0.45      # testa outro limiar
python avaliacao/avaliar.py --embeddings sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 intfloat/multilingual-e5-small
```

Um trecho recuperado conta como **relevante** quando contém a frase de evidência registrada na pergunta de teste (campo `evidencias`). Assim o gabarito vale para qualquer tamanho de chunk.

## Configuração

Tudo pode ser alterado por variável de ambiente ou argumento de linha de comando:

| Variável | Padrão | O que é |
|---|---|---|
| `RAG_EMBEDDINGS` | paraphrase-multilingual-MiniLM-L12-v2 | modelo de embeddings |
| `RAG_CHUNK` / `RAG_OVERLAP` | 600 / 100 | tamanho do trecho e sobreposição (caracteres) |
| `RAG_TOP_K` | 3 | quantos trechos recuperar |
| `RAG_LIMIAR` | 0.40 | similaridade mínima para usar um trecho |
| `RAG_LLM` | ollama | `ollama` ou `hf` |
| `RAG_MODELO_OLLAMA` | qwen2.5:3b | modelo do Ollama |
| `RAG_MODELO_HF` | Qwen/Qwen2.5-1.5B-Instruct | modelo do transformers |

## Base de documentos

| # | Documento | Fonte | Atualizado em |
|---|---|---|---|
| 1 | Como cancelar ingressos e solicitar reembolso | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/6484108930580-Como-cancelar-ingressos-e-solicitar-reembolso) | 2026-11-13 |
| 2 | Como funciona o reembolso do meu pedido? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/6479364031252-Como-funciona-o-reembolso-do-meu-pedido) | 2026-11-13 |
| 3 | Posso cancelar uma compra de um evento online ou presencial? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360032895972-Posso-cancelar-uma-compra-de-um-evento-online-ou-presencial) | 2026-11-10 |
| 4 | Qual a política de reembolso da Sympla? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360017915192-Qual-a-pol%C3%ADtica-de-reembolso-da-Sympla) | 2026-11-11 |
| 5 | Como funciona a política de cancelamento de pedidos nos eventos publicados na Sympla? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360032841691-Como-funciona-a-pol%C3%ADtica-de-cancelamento-de-pedidos-nos-eventos-publicados-na-Sympla) | 2026-11-11 |
| 6 | Entendendo as taxas na compra de ingressos | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/30314422252436-Entendendo-as-taxas-na-compra-de-ingressos) | 2026-11-05 |
| 7 | Como trocar a titularidade do ingresso | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360000383866-Como-trocar-a-titularidade-do-ingresso) | 2026-11-07 |
| 8 | Seguro Reembolso Garantido: mais segurança para sua compra! | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/16782106896788-Seguro-Reembolso-Garantido-mais-seguran%C3%A7a-para-sua-compra) | 2026-11-11 |
| 9 | Quais são as formas de pagamento disponíveis? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/204767745-Quais-s%C3%A3o-as-formas-de-pagamento-dispon%C3%ADveis) | 2026-10-28 |
| 10 | Posso parcelar meu pagamento com cartão de crédito? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360001083203-Posso-parcelar-meu-pagamento-com-cart%C3%A3o-de-cr%C3%A9dito) | 2026-11-01 |
| 11 | Como acessar meus ingressos | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/115005427246-Como-acessar-meus-ingressos) | 2026-11-12 |
| 12 | Meu evento foi adiado. O que devo fazer? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360040582872-Meu-evento-foi-adiado-O-que-devo-fazer) | 2026-11-04 |
| 13 | Meu evento foi cancelado. O que devo fazer? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/115005565026-Meu-evento-foi-cancelado-O-que-devo-fazer) | 2026-11-10 |
| 14 | Como excluir minha conta da plataforma Sympla? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/33875336274836-Como-excluir-minha-conta-da-plataforma-Sympla) | 2026-11-01 |
| 15 | Como falar com a Sympla? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/10520960293012-Como-falar-com-a-Sympla) | 2026-11-13 |
| 16 | Posso comprar ingressos por terceiros fora da plataforma Sympla? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/8840604775828-Posso-comprar-ingressos-por-terceiros-fora-da-plataforma-Sympla) | 2026-10-22 |
| 17 | Como comprar ingressos? | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/213638506-Como-comprar-ingressos) | 2026-11-09 |
| 18 | Meia-entrada: confira tudo o que você precisa saber para produzir seu evento | [link](https://ajuda.sympla.com.br/hc/pt-br/articles/360026413972-Meia-entrada-confira-tudo-o-que-voc%C3%AA-precisa-saber-para-produzir-seu-evento) | 2026-11-12 |

Todos os documentos foram acessados em 13/11/2026 pela API pública da Central de Ajuda (Zendesk) da Sympla. Não há dados pessoais.
