"""App web simples (Gradio) para a demonstração.

Uso:  python app.py            (abre em http://localhost:7860)
No Colab, use `python app.py --share` para gerar um link público temporário.
"""
import argparse

import gradio as gr

from src import config
from src.rag import SistemaRAG


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--llm", choices=["ollama", "hf"], default=config.BACKEND_LLM)
    p.add_argument("--share", action="store_true")
    a = p.parse_args()
    rag = SistemaRAG(backend_llm=a.llm)

    def responder(pergunta):
        r = rag.responder(pergunta)
        linhas = [f"| {t.similaridade:.2f} | {t.citacao()} | {t.metadados.get('secao', '')} |" for t in r.trechos]
        tabela = ("| Similaridade | Fonte | Seção |\n|---|---|---|\n" + "\n".join(linhas)) if linhas else \
            f"Nenhum trecho passou do limiar de similaridade ({rag.limiar})."
        return r.texto, tabela

    with gr.Blocks(title="Assistente Sympla (RAG)") as demo:
        gr.Markdown("# 🎟️ Assistente da Central de Ajuda da Sympla\nPergunte sobre cancelamento, reembolso, troca de titularidade, pagamento, meia-entrada e mais. Projeto acadêmico, sem vínculo com a Sympla.")
        entrada = gr.Textbox(label="Sua pergunta", placeholder="Ex.: Posso cancelar só um ingresso do pedido?")
        botao = gr.Button("Perguntar", variant="primary")
        resposta = gr.Markdown(label="Resposta")
        fontes = gr.Markdown(label="Trechos recuperados")
        gr.Examples(["Qual é o prazo para cancelar a compra de um ingresso e ter direito ao reembolso?",
                     "Paguei com Pix e cancelei a compra. Em quanto tempo recebo o dinheiro de volta?",
                     "Até quando posso trocar o nome do titular do ingresso?",
                     "Existe limite de ingressos de meia-entrada para idosos?",
                     "Quem é o CEO da Sympla?",
                     "Qual é o número de telefone do SAC da Sympla?"], entrada)
        botao.click(responder, entrada, [resposta, fontes])
        entrada.submit(responder, entrada, [resposta, fontes])
    demo.launch(share=a.share)


if __name__ == "__main__":
    main()
