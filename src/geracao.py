"""Geração da resposta com um LLM aberto (Ollama local ou transformers no Colab)."""
from __future__ import annotations

from . import config
from .recuperacao import Resultado

PROMPT_SISTEMA = f"""Você é um assistente (projeto acadêmico, não oficial) que tira dúvidas sobre a {config.NOME_NEGOCIO}, {config.DESCRICAO_NEGOCIO}, usando artigos públicos da Central de Ajuda.
Regras obrigatórias:
1. Responda SOMENTE com base nos trechos do CONTEXTO abaixo. Não use conhecimento externo e não invente valores, prazos ou regras.
2. Ao final da resposta, cite a(s) fonte(s) usada(s) no formato: Fonte: <título do documento> (<arquivo>, <data>).
3. Se o contexto não tiver a informação pedida, responda exatamente: "{config.RESPOSTA_SEM_CONTEXTO}" e não cite fonte.
4. Responda em português do Brasil, de forma curta e direta (no máximo 4 frases)."""


def montar_contexto(trechos: list[Resultado]) -> str:
    partes = []
    for i, t in enumerate(trechos, 1):
        partes.append(f"[Trecho {i}] Fonte: {t.citacao()}\n{t.texto}")
    return "\n\n".join(partes)


def montar_mensagens(pergunta: str, trechos: list[Resultado]) -> list[dict]:
    usuario = f"CONTEXTO:\n{montar_contexto(trechos)}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA:"
    return [{"role": "system", "content": PROMPT_SISTEMA}, {"role": "user", "content": usuario}]


class GeradorOllama:
    def __init__(self, modelo: str = config.MODELO_OLLAMA, url: str = config.URL_OLLAMA):
        self.modelo, self.url = modelo, url.rstrip("/")

    def gerar(self, mensagens: list[dict]) -> str:
        import requests

        r = requests.post(
            f"{self.url}/api/chat",
            json={"model": self.modelo, "messages": mensagens, "stream": False,
                  "options": {"temperature": 0.1, "num_predict": 300}},
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()


class GeradorHF:
    """Roda o LLM com a biblioteca transformers (GPU do Colab, se houver)."""

    def __init__(self, modelo: str = config.MODELO_HF):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tok = AutoTokenizer.from_pretrained(modelo)
        usa_gpu = torch.cuda.is_available()
        self.modelo = AutoModelForCausalLM.from_pretrained(
            modelo, torch_dtype=torch.float16 if usa_gpu else torch.float32,
            device_map="auto" if usa_gpu else None,
        )

    def gerar(self, mensagens: list[dict]) -> str:
        entrada = self.tok.apply_chat_template(mensagens, add_generation_prompt=True, return_tensors="pt")
        entrada = entrada.to(self.modelo.device)
        saida = self.modelo.generate(entrada, max_new_tokens=300, do_sample=False,
                                     pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(saida[0][entrada.shape[-1]:], skip_special_tokens=True).strip()


def criar_gerador(backend: str = config.BACKEND_LLM):
    if backend == "ollama":
        return GeradorOllama()
    if backend == "hf":
        return GeradorHF()
    raise ValueError(f"Backend de LLM desconhecido: {backend} (use 'ollama' ou 'hf')")
