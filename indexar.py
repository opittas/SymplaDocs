"""Constrói os índices vetoriais no Chroma.

Uso:
    python indexar.py                 # índice com a configuração padrão (1000/150)
    python indexar.py --todos         # índices para todos os tamanhos testados
"""
import argparse

from src import config
from src.indice import Embedder, construir_indice


def main():
    p = argparse.ArgumentParser(description="Indexa os documentos da Sympla no Chroma")
    p.add_argument("--chunk", type=int, default=config.TAMANHO_CHUNK)
    p.add_argument("--overlap", type=int, default=config.SOBREPOSICAO)
    p.add_argument("--todos", action="store_true", help="indexa todas as configurações de CONFIGS_CHUNK")
    p.add_argument("--embeddings", default=config.MODELO_EMBEDDINGS)
    a = p.parse_args()

    embedder = Embedder(a.embeddings)
    configs = config.CONFIGS_CHUNK if a.todos else [(a.chunk, a.overlap)]
    for tamanho, sobreposicao in configs:
        col = construir_indice(config.PASTA_DOCS, config.PASTA_CHROMA, embedder, tamanho, sobreposicao)
        print(f"Coleção {col.name}: {col.count()} trechos indexados")


if __name__ == "__main__":
    main()
