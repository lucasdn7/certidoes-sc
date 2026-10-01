from __future__ import annotations

import base64
import binascii
import re
from pathlib import Path
from urllib.parse import urljoin


def limpar_documento(documento: str) -> str:
    return re.sub(r"\D", "", documento or "")


def validar_documento(documento: str) -> tuple[bool, str]:
    numero = limpar_documento(documento)
    if len(numero) not in (11, 14):
        return False, "Informe um CPF com 11 dígitos ou CNPJ com 14 dígitos."
    if len(set(numero)) == 1:
        return False, "O documento informado não parece válido."
    return True, numero


def url_absoluta(base_url: str, href: str) -> str:
    return urljoin(base_url, href)


def extrair_pdf_base64(valor: str) -> bytes:
    texto = (valor or "").strip()
    if "," in texto and texto.lower().startswith("data:"):
        texto = texto.split(",", 1)[1]
    try:
        return base64.b64decode(texto, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("A resposta não contém um Base64 de PDF válido.") from exc


def resposta_e_pdf(response) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    return "application/pdf" in content_type or response.content.startswith(b"%PDF")


def salvar_pdf_bytes(pasta: Path, nome: str, conteudo: bytes) -> Path:
    if not conteudo.startswith(b"%PDF"):
        raise ValueError("O conteúdo recebido não é um PDF.")
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome
    destino.write_bytes(conteudo)
    return destino
