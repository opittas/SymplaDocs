"""Leitura dos documentos e divisão em trechos (chunking) com sobreposição."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Documento:
    arquivo: str
    titulo: str
    fonte: str
    data: str
    texto: str


@dataclass
class Trecho:
    id: str
    texto: str            # texto original do trecho (mostrado ao LLM e ao usuário)
    texto_indexado: str   # texto com título/seção na frente (usado no embedding)
    metadados: dict = field(default_factory=dict)


def carregar_documentos(pasta: Path) -> list[Documento]:
    """Lê todos os .md/.txt da pasta. Cada arquivo tem um cabeçalho YAML com titulo, fonte e data."""
    docs = []
    for caminho in sorted(list(pasta.glob("*.md")) + list(pasta.glob("*.txt"))):
        bruto = caminho.read_text(encoding="utf-8")
        meta, corpo = {}, bruto
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", bruto, flags=re.S)
        if m:
            meta = yaml.safe_load(m.group(1)) or {}
            corpo = m.group(2)
        docs.append(
            Documento(
                arquivo=caminho.name,
                titulo=str(meta.get("titulo", caminho.stem)),
                fonte=str(meta.get("fonte", "desconhecida")),
                data=str(meta.get("data", "sem data")),
                texto=corpo.strip(),
            )
        )
    return docs


def _blocos_por_secao(texto: str) -> list[tuple[str, str]]:
    """Separa o markdown em parágrafos, guardando a seção (## título) de cada um."""
    secao = ""
    blocos = []
    for paragrafo in re.split(r"\n\s*\n", texto):
        paragrafo = paragrafo.strip()
        if not paragrafo:
            continue
        cab = re.match(r"^(#{1,6})\s+(.*)$", paragrafo.splitlines()[0])
        if cab:
            secao = cab.group(2).strip()
            resto = "\n".join(paragrafo.splitlines()[1:]).strip()
            if not resto:
                continue
            paragrafo = resto
        blocos.append((secao, paragrafo))
    return blocos


def _quebrar_longo(texto: str, tamanho: int) -> list[str]:
    """Quebra um parágrafo maior que o tamanho: primeiro por linhas (itens de
    lista, linhas de tabela), depois por frases e, em último caso, por palavras."""
    unidades: list[tuple[str, str]] = []  # (separador, texto)
    for linha in texto.splitlines():
        if len(linha) <= tamanho:
            unidades.append(("\n", linha))
            continue
        for j, frase in enumerate(re.split(r"(?<=[.!?;])\s+", linha)):
            sep = "\n" if j == 0 else " "
            if len(frase) <= tamanho:
                unidades.append((sep, frase))
            else:
                for k, palavra in enumerate(frase.split()):
                    unidades.append((sep if k == 0 else " ", palavra))
    partes, atual = [], ""
    for sep, u in unidades:
        if atual and len(atual) + len(u) + 1 > tamanho:
            partes.append(atual)
            atual = ""
        atual = f"{atual}{sep}{u}" if atual else u
    if atual:
        partes.append(atual)
    return partes


def _cauda(texto: str, n: int) -> str:
    """Últimos n caracteres do texto, começando no início de uma palavra."""
    if n <= 0 or len(texto) <= n:
        return texto if n > 0 else ""
    cauda = texto[-n:]
    espaco = cauda.find(" ")
    return cauda[espaco + 1:] if espaco != -1 else cauda


def dividir_em_trechos(doc: Documento, tamanho: int, sobreposicao: int) -> list[Trecho]:
    """Agrupa parágrafos até `tamanho` caracteres; cada trecho começa com os
    últimos `sobreposicao` caracteres do trecho anterior (sobreposição)."""
    unidades: list[tuple[str, str]] = []
    for secao, par in _blocos_por_secao(doc.texto):
        if len(par) > tamanho:
            unidades += [(secao, p) for p in _quebrar_longo(par, tamanho)]
        else:
            unidades.append((secao, par))

    grupos: list[tuple[str, str]] = []
    secao_atual, atual = "", ""
    for secao, par in unidades:
        if atual and len(atual) + len(par) + 2 > tamanho:
            grupos.append((secao_atual, atual))
            atual = _cauda(atual, sobreposicao)
            secao_atual = secao
        if not atual:
            secao_atual = secao
        atual = f"{atual}\n\n{par}".strip()
    if atual:
        grupos.append((secao_atual, atual))

    trechos = []
    for i, (secao, texto) in enumerate(grupos):
        cabecalho = doc.titulo + (f" – {secao}" if secao and secao != doc.titulo else "")
        trechos.append(
            Trecho(
                id=f"{Path(doc.arquivo).stem}#{i:02d}",
                texto=texto,
                texto_indexado=f"{cabecalho}\n{texto}",
                metadados={
                    "arquivo": doc.arquivo,
                    "titulo": doc.titulo,
                    "secao": secao,
                    "fonte": doc.fonte,
                    "data": doc.data,
                    "posicao": i,
                },
            )
        )
    return trechos


def gerar_trechos(pasta: Path, tamanho: int, sobreposicao: int) -> list[Trecho]:
    trechos = []
    for doc in carregar_documentos(pasta):
        trechos += dividir_em_trechos(doc, tamanho, sobreposicao)
    return trechos
