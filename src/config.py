"""Configurações centrais do sistema RAG.

Todos os valores podem ser sobrescritos por variáveis de ambiente ou pelos
argumentos de linha de comando dos scripts.
"""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Nome do negócio fictício (usado no prompt e nas mensagens).
NOME_NEGOCIO = os.getenv("RAG_NEGOCIO", "Sympla")
DESCRICAO_NEGOCIO = os.getenv(
    "RAG_DESCRICAO", "plataforma brasileira de venda de ingressos e inscrições para eventos"
)
PASTA_DOCS = RAIZ / "docs"
PASTA_CHROMA = Path(os.getenv("RAG_CHROMA_DIR", RAIZ / "chroma_db"))

# Modelo de embeddings multilíngue e gratuito (sentence-transformers / Hugging Face).
MODELO_EMBEDDINGS = os.getenv(
    "RAG_EMBEDDINGS", "intfloat/multilingual-e5-small"
)

# Chunking: tamanho em caracteres e sobreposição. Tamanhos testados na avaliação.
TAMANHO_CHUNK = int(os.getenv("RAG_CHUNK", 1000))
SOBREPOSICAO = int(os.getenv("RAG_OVERLAP", 150))
CONFIGS_CHUNK = [(300, 60), (600, 100), (1000, 150)]

# Recuperação: k trechos mais próximos e limiar mínimo de similaridade (cosseno).
TOP_K = int(os.getenv("RAG_TOP_K", 3))
LIMIAR_SIMILARIDADE = float(os.getenv("RAG_LIMIAR", 0.89))

# Geração: "ollama" (local) ou "hf" (transformers, ideal para o Google Colab).
BACKEND_LLM = os.getenv("RAG_LLM", "ollama")
MODELO_OLLAMA = os.getenv("RAG_MODELO_OLLAMA", "qwen2.5:3b")
URL_OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODELO_HF = os.getenv("RAG_MODELO_HF", "Qwen/Qwen2.5-1.5B-Instruct")

RESPOSTA_SEM_CONTEXTO = f"Não encontrei essa informação nos documentos da {NOME_NEGOCIO}."
