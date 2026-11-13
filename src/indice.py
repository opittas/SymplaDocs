"""Embeddings e banco vetorial (Chroma)."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from . import config
from .documentos import Trecho, gerar_trechos


class Embedder:
    """Gera embeddings normalizados com um modelo do sentence-transformers.

    Modelos da família E5 (ex.: intfloat/multilingual-e5-small) exigem os
    prefixos "query: " e "passage: "; isso é tratado automaticamente.
    """

    def __init__(self, nome_modelo: str):
        self.nome = nome_modelo
        if nome_modelo == "teste-tfidf":
            # Apenas para testes automáticos sem internet. NÃO é usado no trabalho.
            from sklearn.feature_extraction.text import HashingVectorizer

            self._hv = HashingVectorizer(analyzer="char_wb", ngram_range=(3, 5), n_features=2**14)
            self._modelo = None
        else:
            from sentence_transformers import SentenceTransformer

            self._modelo = SentenceTransformer(nome_modelo)
        self._e5 = "e5" in nome_modelo.lower()

    def codificar(self, textos: list[str], consulta: bool = False) -> np.ndarray:
        if self._e5:
            prefixo = "query: " if consulta else "passage: "
            textos = [prefixo + t for t in textos]
        if self._modelo is None:
            v = self._hv.transform(textos).toarray()
            return v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-9, None)
        return self._modelo.encode(textos, normalize_embeddings=True, show_progress_bar=False)


def nome_colecao(modelo: str, tamanho: int, sobreposicao: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", modelo.lower().split("/")[-1]).strip("-")[:30]
    neg = re.sub(r"[^a-z0-9]+", "-", config.NOME_NEGOCIO.lower()).strip("-")[:20] or "rag"
    return f"{neg}-{slug}-c{tamanho}-o{sobreposicao}"


def _cliente(pasta_chroma: Path):
    import chromadb
    from chromadb.config import Settings

    return chromadb.PersistentClient(path=str(pasta_chroma), settings=Settings(anonymized_telemetry=False))


def construir_indice(pasta_docs: Path, pasta_chroma: Path, embedder: Embedder,
                     tamanho: int, sobreposicao: int):
    """Divide os documentos, gera embeddings e grava tudo numa coleção do Chroma.
    A coleção usa distância de cosseno; similaridade = 1 - distância."""
    trechos: list[Trecho] = gerar_trechos(pasta_docs, tamanho, sobreposicao)
    cliente = _cliente(pasta_chroma)
    nome = nome_colecao(embedder.nome, tamanho, sobreposicao)
    try:
        cliente.delete_collection(nome)
    except Exception:
        pass
    col = cliente.create_collection(nome, metadata={"hnsw:space": "cosine"})
    vetores = embedder.codificar([t.texto_indexado for t in trechos])
    col.add(
        ids=[t.id for t in trechos],
        documents=[t.texto for t in trechos],
        embeddings=[v.tolist() for v in vetores],
        metadatas=[t.metadados for t in trechos],
    )
    return col


def abrir_indice(pasta_chroma: Path, embedder: Embedder, tamanho: int, sobreposicao: int,
                 pasta_docs: Path | None = None):
    """Abre a coleção; se ainda não existir e pasta_docs for informada, constrói."""
    cliente = _cliente(pasta_chroma)
    nome = nome_colecao(embedder.nome, tamanho, sobreposicao)
    try:
        col = cliente.get_collection(nome)
        if col.count() > 0:
            return col
    except Exception:
        pass
    if pasta_docs is None:
        raise RuntimeError(f"Índice '{nome}' não encontrado. Rode: python indexar.py")
    return construir_indice(pasta_docs, pasta_chroma, embedder, tamanho, sobreposicao)
