# Resultados da avaliação

Gerado automaticamente por `avaliacao/avaliar.py` em 2026-11-27 13:32 (Google Colab, CPU).

Perguntas: 22 (18 com resposta na base, 4 sem resposta).

## Comparação das configurações de recuperação

| Modelo | Chunk/overlap | Nº trechos | P@1 | P@3 | P@5 | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---|---|---|---|---|---|---|---|
| paraphrase-multilingual-MiniLM-L12-v2 | 300/60 | 217 | 38.9% | 29.6% | 22.2% | 38.9% | 72.2% | 83.3% | 0.562 |
| paraphrase-multilingual-MiniLM-L12-v2 | 600/100 | 110 | 50.0% | 25.9% | 18.9% | 50.0% | 66.7% | 72.2% | 0.569 |
| paraphrase-multilingual-MiniLM-L12-v2 | 1000/150 | 62 | 50.0% | 25.9% | 17.8% | 50.0% | 66.7% | 66.7% | 0.565 |
| multilingual-e5-small | 300/60 | 217 | 44.4% | 29.6% | 20.0% | 44.4% | 77.8% | 83.3% | 0.613 |
| multilingual-e5-small | 600/100 | 110 | 66.7% | 46.3% | 27.8% | 66.7% | 88.9% | 88.9% | 0.759 |
| multilingual-e5-small | 1000/150 | 62 | 72.2% | 44.4% | 26.7% | 72.2% | 88.9% | 88.9% | 0.796 |

Obs.: como a maioria das perguntas tem só 1 trecho relevante, o P@3 máximo possível fica perto de 33%. Por isso o Hit@k e o MRR ajudam a comparar as configurações.

**Configuração escolhida (maior MRR; empate → maior Hit@3):** multilingual-e5-small, chunk 1000, overlap 150.

## Limiar de similaridade

Limiar usado: **0.4** (padrão antigo, antes da escolha). Limiar sugerido pelos dados: **0.89** (acurácia balanceada 84.7%).

(A tabela de similaridades por pergunta e a lista de falhas estão em `resultados.md`, que foi gerado com o limiar final 0.89. Com o limiar 0.4, as 4 perguntas sem resposta passavam do limiar: P19 0.868, P20 0.900, P21 0.848, P22 0.889.)
