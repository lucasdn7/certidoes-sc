from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .utils import limpar_documento


class CertidaoFetcher:
    nome = "Certidão"
    validade_dias = 180

    def __init__(self, documento: str, output_dir: str = "output"):
        self.documento = limpar_documento(documento)
        self.tipo = "cpf" if len(self.documento) == 11 else "cnpj"
        self.output_dir = (
            Path(output_dir)
            / self.documento
            / datetime.now().strftime("%Y-%m-%d")
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def salvar_pdf(self, conteudo: bytes, nome_arquivo: str) -> Path:
        if not conteudo.startswith(b"%PDF"):
            raise ValueError("O conteúdo recebido não é um PDF válido.")
        caminho = self.output_dir / nome_arquivo
        caminho.write_bytes(conteudo)
        return caminho

    def resultado(self, status: str, arquivo: Path | None = None, **extra) -> dict:
        dados = {
            "certidao": self.nome,
            "documento": self.documento,
            "status": status,
            "arquivo": str(arquivo) if arquivo else None,
            "validade_dias": self.validade_dias,
        }
        dados.update(extra)
        return dados

    def salvar_debug(self, nome: str, conteudo: str | bytes) -> Path:
        destino = self.output_dir / nome
        if isinstance(conteudo, bytes):
            destino.write_bytes(conteudo)
        else:
            destino.write_text(conteudo, encoding="utf-8", errors="replace")
        return destino

    def buscar(self) -> dict:
        raise NotImplementedError
