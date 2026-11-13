"""Interface de linha de comando do assistente da Grão Norte.

Uso:
    python perguntar.py                            # modo interativo
    python perguntar.py "Qual o prazo de troca?"   # uma pergunta só
    python perguntar.py --llm hf                   # usa transformers em vez do Ollama
    python perguntar.py --sem-llm                  # mostra só os trechos recuperados
"""
import argparse

from src import config
from src.rag import SistemaRAG


def mostrar(resposta, detalhes: bool):
    print("\n" + resposta.texto)
    if detalhes:
        if resposta.trechos:
            print("\nTrechos usados:")
            for t in resposta.trechos:
                print(f"  - [{t.similaridade:.2f}] {t.id} | {t.citacao()}")
        else:
            print(f"\n(nenhum trecho acima do limiar de similaridade {config.LIMIAR_SIMILARIDADE})")
    print()


def main():
    p = argparse.ArgumentParser(description="Pergunte sobre as políticas da Grão Norte")
    p.add_argument("pergunta", nargs="*")
    p.add_argument("--chunk", type=int, default=config.TAMANHO_CHUNK)
    p.add_argument("--overlap", type=int, default=config.SOBREPOSICAO)
    p.add_argument("--k", type=int, default=config.TOP_K)
    p.add_argument("--limiar", type=float, default=config.LIMIAR_SIMILARIDADE)
    p.add_argument("--llm", choices=["ollama", "hf"], default=config.BACKEND_LLM)
    p.add_argument("--sem-llm", action="store_true")
    p.add_argument("--embeddings", default=config.MODELO_EMBEDDINGS)
    p.add_argument("-q", "--quieto", action="store_true", help="não mostra os trechos recuperados")
    a = p.parse_args()

    config.LIMIAR_SIMILARIDADE = a.limiar
    rag = SistemaRAG(a.embeddings, a.chunk, a.overlap, a.k, a.limiar, None if a.sem_llm else a.llm)

    if a.pergunta:
        mostrar(rag.responder(" ".join(a.pergunta)), not a.quieto)
        return
    print("Assistente Grão Norte ☕  (digite 'sair' para encerrar)\n")
    while True:
        try:
            pergunta = input("Pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if pergunta:
            mostrar(rag.responder(pergunta), not a.quieto)


if __name__ == "__main__":
    main()
