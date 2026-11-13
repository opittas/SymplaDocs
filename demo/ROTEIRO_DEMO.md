# Roteiro da demonstração (~8 minutos)

## 1. Problema (1 min)
- "Quem compra ingresso na Sympla tem sempre as mesmas dúvidas: posso cancelar? quando recebo o dinheiro? posso passar o ingresso para outra pessoa?"
- As respostas estão espalhadas em dezenas de artigos da Central de Ajuda.
- Um LLM sozinho inventa prazos. Mostrar (opcional): perguntar a um chatbot genérico "Qual o prazo para trocar a titularidade na Sympla?".

## 2. Solução (1,5 min)
- Mostrar o diagrama da arquitetura do relatório.
- 18 artigos públicos → chunks de 600 caracteres → embeddings multilíngues → Chroma → top-3 com limiar → LLM aberto (Qwen) com prompt restrito.

## 3. Sistema funcionando (3 min)
Abrir o app (`python app.py` ou `python app.py --llm hf --share` no Colab) e fazer, nesta ordem:

| # | Pergunta | O que mostrar |
|---|---|---|
| 1 | Qual é o prazo para cancelar a compra de um ingresso e ter direito ao reembolso? | resposta com 7 dias e a fonte citada |
| 2 | Paguei com Pix e cancelei a compra. Em quanto tempo recebo o dinheiro de volta? | regra específica do Pix (90 dias / 7 dias) |
| 3 | Até quando posso trocar o nome do titular do ingresso? | sinônimo ("nome do titular" × "titularidade") funcionando |
| 4 | Existe limite de ingressos de meia-entrada para idosos? | resposta tirada de um artigo longo |
| 5 | Quem é o CEO da Sympla? | **sistema admite que não sabe** (nenhum trecho passa do limiar) |
| 6 | Qual é o número de telefone do SAC da Sympla? | pergunta difícil: a base tem telefones da Zurich, não da Sympla; o sistema não deve confundir |

Mostrar a tabela de trechos recuperados com a similaridade e a fonte.

## 4. Resultados e aprendizados (2 min)
- Tabela comparando os chunks de 300, 600 e 1000 (P@3, Hit@3, MRR) e por que escolhemos o tamanho.
- Taxa de recusa correta nas perguntas sem resposta.
- Um dos três erros analisados, com a causa e o que faríamos para corrigir.
- Aprendizados: o limiar e o prompt são complementares; a qualidade da base importa mais que o tamanho do modelo; avaliar com gabarito de trecho deixa a comparação objetiva.

## 5. Perguntas (0,5 min)

### Plano B
Se a internet ou a GPU falharem: rodar `python perguntar.py --sem-llm "pergunta"` (mostra só a recuperação) ou ter prints/vídeo das respostas gravados antes.
