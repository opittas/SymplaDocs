"""Avaliação do sistema RAG.

Mede a recuperação para cada configuração de chunk (e, opcionalmente, para mais
de um modelo de embeddings) usando as perguntas de teste com o trecho correto
conhecido. Um trecho recuperado é considerado RELEVANTE se contém alguma das
"evidencias" da pergunta (frase exata do documento). Assim o gabarito não
depende de como cada tamanho de chunk cortou o texto.

Métricas (só perguntas com resposta na base):
  - precision@k: fração dos k trechos recuperados que são relevantes (média).
  - hit@k: fração das perguntas com pelo menos 1 trecho relevante no top-k.
  - MRR: média de 1/posição do primeiro trecho relevante.
Para as perguntas SEM resposta, verifica se o limiar de similaridade descarta
todos os trechos (o sistema então responde que não encontrou).

Uso:
    python avaliacao/avaliar.py                       # todos os tamanhos de chunk
    python avaliacao/avaliar.py --gerar --llm hf      # também gera as respostas com o LLM
    python avaliacao/avaliar.py --embeddings A B      # compara modelos de embeddings
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config  # noqa: E402
from src.indice import Embedder, construir_indice  # noqa: E402
from src.recuperacao import buscar  # noqa: E402

PASTA = Path(__file__).resolve().parent
KS = [1, 3, 5]


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().lower()


def relevante(texto: str, evidencias: list[str]) -> bool:
    t = norm(texto)
    return any(norm(e) in t for e in evidencias)


def avaliar_config(perguntas, embedder, tamanho, sobreposicao, limiar):
    col = construir_indice(config.PASTA_DOCS, config.PASTA_CHROMA, embedder, tamanho, sobreposicao)
    linhas = []
    for p in perguntas:
        res = buscar(col, embedder, p["pergunta"], max(KS))
        rel = [relevante(r.texto, p["evidencias"]) for r in res] if p["tem_resposta"] else []
        linhas.append({
            "id": p["id"], "pergunta": p["pergunta"], "tem_resposta": p["tem_resposta"],
            "top1_sim": res[0].similaridade if res else 0.0,
            "recuperados": [{"id": r.id, "sim": r.similaridade, "relevante": (rel[i] if rel else False)}
                            for i, r in enumerate(res)],
            "relevantes": rel,
        })
    com = [l for l in linhas if l["tem_resposta"]]
    sem = [l for l in linhas if not l["tem_resposta"]]
    m = {"chunk": tamanho, "overlap": sobreposicao, "n_trechos": col.count(), "modelo": embedder.nome}
    for k in KS:
        m[f"precision@{k}"] = sum(sum(l["relevantes"][:k]) / k for l in com) / len(com)
        m[f"hit@{k}"] = sum(any(l["relevantes"][:k]) for l in com) / len(com)
    m["mrr"] = sum(next((1 / (i + 1) for i, r in enumerate(l["relevantes"]) if r), 0) for l in com) / len(com)
    m["sem_resposta_recusadas"] = sum(l["top1_sim"] < limiar for l in sem)
    m["com_resposta_aceitas"] = sum(l["top1_sim"] >= limiar for l in com)
    return m, linhas


def sugerir_limiar(linhas):
    """Testa limiares de 0.20 a 0.80 e escolhe o que melhor separa perguntas com e
    sem resposta (acurácia balanceada; empate -> menor limiar, para recusar menos)."""
    com = [l["top1_sim"] for l in linhas if l["tem_resposta"]]
    sem = [l["top1_sim"] for l in linhas if not l["tem_resposta"]]
    melhor = None
    for i in range(20, 81):
        t = i / 100
        acc = (sum(s >= t for s in com) / len(com) + sum(s < t for s in sem) / len(sem)) / 2
        if melhor is None or acc > melhor[1]:
            melhor = (t, acc)
    return melhor


def gerar_respostas(perguntas, args, tamanho, sobreposicao, limiar, k):
    from src.rag import SistemaRAG

    rag = SistemaRAG(args.embeddings[0], tamanho, sobreposicao, k, limiar, args.llm)
    saida = []
    for p in perguntas:
        t0 = time.time()
        r = rag.responder(p["pergunta"])
        recusou = "não encontrei" in r.texto.lower()
        saida.append({
            "id": p["id"], "pergunta": p["pergunta"], "tem_resposta": p["tem_resposta"],
            "resposta": r.texto, "esperada": p["resposta_esperada"],
            "fontes": [t.citacao() for t in r.trechos],
            "citou_fonte": "fonte" in r.texto.lower(), "recusou": recusou,
            "comportamento_ok": (not recusou) if p["tem_resposta"] else recusou,
            "segundos": round(time.time() - t0, 1),
        })
        print(f"  {p['id']}: {'ok' if saida[-1]['comportamento_ok'] else 'VERIFICAR'}")
    return saida


def pct(x):
    return f"{100 * x:.1f}%"


def relatorio_md(metricas, detalhes, escolha, limiar_sug, respostas, k):
    L = ["# Resultados da avaliação", "",
         f"Gerado automaticamente por `avaliacao/avaliar.py` em {time.strftime('%Y-%m-%d %H:%M')}.", ""]
    n_com = sum(l["tem_resposta"] for l in next(iter(detalhes.values())))
    n_sem = len(next(iter(detalhes.values()))) - n_com
    L += [f"Perguntas: {n_com + n_sem} ({n_com} com resposta na base, {n_sem} sem resposta).", "",
          "## Comparação das configurações de recuperação", "",
          "| Modelo | Chunk/overlap | Nº trechos | P@1 | P@3 | P@5 | Hit@1 | Hit@3 | Hit@5 | MRR |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for m in metricas:
        L.append(f"| {m['modelo'].split('/')[-1]} | {m['chunk']}/{m['overlap']} | {m['n_trechos']} | "
                 f"{pct(m['precision@1'])} | {pct(m['precision@3'])} | {pct(m['precision@5'])} | "
                 f"{pct(m['hit@1'])} | {pct(m['hit@3'])} | {pct(m['hit@5'])} | {m['mrr']:.3f} |")
    L += ["", "Obs.: como a maioria das perguntas tem só 1 trecho relevante, o P@3 máximo possível fica perto de 33%. "
          "Por isso o Hit@k e o MRR ajudam a comparar as configurações.", "",
          f"**Configuração escolhida (maior MRR; empate → maior Hit@{k}):** "
          f"{escolha['modelo'].split('/')[-1]}, chunk {escolha['chunk']}, overlap {escolha['overlap']}.", "",
          "## Limiar de similaridade", "",
          f"Limiar usado: **{config.LIMIAR_SIMILARIDADE}**. Limiar sugerido pelos dados: **{limiar_sug[0]:.2f}** "
          f"(acurácia balanceada {pct(limiar_sug[1])}).", "",
          "| Pergunta | Tem resposta? | Similaridade do 1º trecho | 1º trecho é relevante? |", "|---|---|---|---|"]
    chave = (escolha["modelo"], escolha["chunk"], escolha["overlap"])
    for l in detalhes[chave]:
        rel = ("sim" if l["relevantes"][0] else "não") if l["tem_resposta"] else "—"
        L.append(f"| {l['id']} {l['pergunta']} | {'sim' if l['tem_resposta'] else 'não'} | {l['top1_sim']:.3f} | {rel} |")
    L += ["", "## Falhas de recuperação na configuração escolhida (candidatas à análise de erros)", ""]
    falhas = []
    for l in detalhes[chave]:
        if l["tem_resposta"] and not any(l["relevantes"][:k]):
            falhas.append(f"- **{l['id']}** ({l['pergunta']}): nenhum trecho relevante no top-{k}. "
                          f"Recuperados: {', '.join(r['id'] for r in l['recuperados'][:k])}.")
        elif l["tem_resposta"] and not l["relevantes"][0]:
            falhas.append(f"- **{l['id']}** ({l['pergunta']}): trecho relevante não ficou em 1º lugar "
                          f"(1º: {l['recuperados'][0]['id']}).")
        elif l["tem_resposta"] and l["top1_sim"] < config.LIMIAR_SIMILARIDADE:
            falhas.append(f"- **{l['id']}** ({l['pergunta']}): trecho certo recuperado, mas abaixo do limiar "
                          f"({l['top1_sim']:.3f}); o sistema diria que não sabe.")
        elif not l["tem_resposta"] and l["top1_sim"] >= config.LIMIAR_SIMILARIDADE:
            falhas.append(f"- **{l['id']}** ({l['pergunta']}): sem resposta na base, mas o trecho "
                          f"{l['recuperados'][0]['id']} passou do limiar ({l['top1_sim']:.3f}); o LLM precisa recusar.")
    L += falhas or ["Nenhuma falha de recuperação."]
    if respostas:
        ok = sum(r["comportamento_ok"] for r in respostas)
        L += ["", "## Respostas geradas pelo LLM", "",
              f"Comportamento esperado (responder quando há resposta / recusar quando não há): **{ok}/{len(respostas)}**. "
              "A exatidão do conteúdo deve ser conferida manualmente comparando com a resposta esperada.", ""]
        for r in respostas:
            L += [f"### {r['id']} – {r['pergunta']}", "", f"**Resposta do sistema:** {r['resposta']}", "",
                  f"**Esperada:** {r['esperada']}", "",
                  f"Fontes recuperadas: {'; '.join(r['fontes']) or 'nenhuma'} · tempo: {r['segundos']} s", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embeddings", nargs="+", default=[config.MODELO_EMBEDDINGS])
    ap.add_argument("--k", type=int, default=config.TOP_K)
    ap.add_argument("--limiar", type=float, default=config.LIMIAR_SIMILARIDADE)
    ap.add_argument("--gerar", action="store_true", help="gera respostas com o LLM na configuração escolhida")
    ap.add_argument("--llm", choices=["ollama", "hf"], default=config.BACKEND_LLM)
    args = ap.parse_args()
    config.LIMIAR_SIMILARIDADE = args.limiar

    perguntas = json.loads((PASTA / "perguntas_teste.json").read_text(encoding="utf-8"))
    metricas, detalhes = [], {}
    for modelo in args.embeddings:
        emb = Embedder(modelo)
        for tamanho, sobreposicao in config.CONFIGS_CHUNK:
            print(f"Avaliando {modelo} | chunk {tamanho} / overlap {sobreposicao} ...")
            m, linhas = avaliar_config(perguntas, emb, tamanho, sobreposicao, args.limiar)
            metricas.append(m)
            detalhes[(modelo, tamanho, sobreposicao)] = linhas
            print(f"   P@{args.k}={pct(m[f'precision@{args.k}'])}  Hit@{args.k}={pct(m[f'hit@{args.k}'])}  MRR={m['mrr']:.3f}")

    escolha = max(metricas, key=lambda m: (round(m["mrr"], 3), m[f"hit@{args.k}"]))
    chave = (escolha["modelo"], escolha["chunk"], escolha["overlap"])
    limiar_sug = sugerir_limiar(detalhes[chave])
    respostas = None
    if args.gerar:
        print("Gerando respostas com o LLM ...")
        respostas = gerar_respostas(perguntas, args, escolha["chunk"], escolha["overlap"], args.limiar, args.k)

    destino = PASTA / "resultados"
    destino.mkdir(exist_ok=True)
    (destino / "resultados.json").write_text(json.dumps(
        {"metricas": metricas, "escolha": escolha, "limiar_sugerido": limiar_sug,
         "detalhes": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in detalhes.items()}, "respostas": respostas},
        ensure_ascii=False, indent=2), encoding="utf-8")
    (destino / "resultados.md").write_text(
        relatorio_md(metricas, detalhes, escolha, limiar_sug, respostas, args.k), encoding="utf-8")
    print(f"\nEscolhida: chunk {escolha['chunk']}/{escolha['overlap']} | limiar sugerido {limiar_sug[0]:.2f}")
    print(f"Relatório salvo em {destino / 'resultados.md'}")


if __name__ == "__main__":
    main()
