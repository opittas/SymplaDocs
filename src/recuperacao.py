"""Recuperação: busca dos k trechos mais próximos com limiar de similaridade."""
from __future__ import annotations

from dataclasses import dataclass

from .indice import Embedder


@dataclass
class Resultado:
    id: str
    texto: str
    similaridade: float
    metadados: dict

    def citacao(self) -> str:
        m = self.metadados
        return f"{m['titulo']} ({m['arquivo']}, {m['data']})"


def buscar(colecao, embedder: Embedder, pergunta: str, k: int, limiar: float | None = None) -> list[Resultado]:
    """Retorna os k trechos mais similares à pergunta. Se `limiar` for informado,
    descarta os trechos com similaridade de cosseno abaixo dele."""
    vetor = embedder.codificar([pergunta], consulta=True)[0]
    r = colecao.query(query_embeddings=[vetor.tolist()], n_results=k,
                      include=["documents", "metadatas", "distances"])
    resultados = [
        Resultado(id=i, texto=d, similaridade=round(1 - dist, 4), metadados=m)
        for i, d, m, dist in zip(r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]
    if limiar is not None:
        resultados = [x for x in resultados if x.similaridade >= limiar]
    return resultados
