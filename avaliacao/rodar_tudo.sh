#!/usr/bin/env bash
# Roda a avaliação completa (usado no Google Colab com GPU).
# Uso: bash avaliacao/rodar_tudo.sh
set -e
cd "$(dirname "$0")/.."
pip install -q sentence-transformers chromadb pyyaml accelerate
export RAG_LLM=hf
R=avaliacao/resultados
mkdir -p $R

echo "== 1) Comparação de modelos de embeddings x tamanhos de chunk =="
python avaliacao/avaliar.py --embeddings \
  sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 intfloat/multilingual-e5-small
cp $R/resultados.md $R/comparacao_embeddings.md
cp $R/resultados.json $R/comparacao_embeddings.json

echo "== 2) Modelo padrão: escolhe chunk e limiar =="
python avaliacao/avaliar.py
LIMIAR=$(python -c "import json;print(round(json.load(open('$R/resultados.json'))['limiar_sugerido'][0],2))")
echo "Limiar sugerido: $LIMIAR"

echo "== 3) Avaliação completa com o LLM (limiar $LIMIAR) =="
python avaliacao/avaliar.py --gerar --llm hf --limiar $LIMIAR

echo "=====RESULTADOS_COMPARACAO====="
sed -n '1,/## Limiar/p' $R/comparacao_embeddings.md
echo "=====RESULTADOS_FINAIS====="
cat $R/resultados.md
