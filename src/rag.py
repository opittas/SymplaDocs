"""Pipeline completo: pergunta -> recuperação -> geração -> resposta com fontes."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import config
from .geracao import criar_gerador, montar_mensagens
from .indice import Embedder, abrir_indice
from .recuperacao import Resultado, buscar


@dataclass
class Resposta:
    pergunta: str
    texto: str
    trechos: list[Resultado] = field(default_factory=list)
    encontrou_contexto: bool = True


class SistemaRAG:
    def __init__(self, modelo_embeddings: str = config.MODELO_EMBEDDINGS,
                 tamanho: int = config.TAMANHO_CHUNK, sobreposicao: int = config.SOBREPOSICAO,
                 k: int = config.TOP_K, limiar: float = config.LIMIAR_SIMILARIDADE,
                 backend_llm: str | None = config.BACKEND_LLM):
        self.k, self.limiar = k, limiar
        self.embedder = Embedder(modelo_embeddings)
        self.colecao = abrir_indice(config.PASTA_CHROMA, self.embedder, tamanho, sobreposicao,
                                    pasta_docs=config.PASTA_DOCS)
        self.gerador = criar_gerador(backend_llm) if backend_llm else None

    def recuperar(self, pergunta: str) -> list[Resultado]:
        return buscar(self.colecao, self.embedder, pergunta, self.k, self.limiar)

    def responder(self, pergunta: str) -> Resposta:
        trechos = self.recuperar(pergunta)
        # Nenhum trecho acima do limiar: nem chama o LLM, responde que não sabe.
        if not trechos:
            return Resposta(pergunta, config.RESPOSTA_SEM_CONTEXTO, [], encontrou_contexto=False)
        if self.gerador is None:
            return Resposta(pergunta, "(geração desativada; veja os trechos recuperados)", trechos)
        texto = self.gerador.gerar(montar_mensagens(pergunta, trechos))
        return Resposta(pergunta, texto, trechos)
