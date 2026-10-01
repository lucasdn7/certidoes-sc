from __future__ import annotations

import requests

from .base import CertidaoFetcher
from .utils import extrair_pdf_base64


class CndEstadualSC(CertidaoFetcher):
    nome = "CND Estadual SC (SEF-SC)"
    validade_dias = 180
    URL = "https://sat.sef.sc.gov.br/api/cnd/Certidao/Gerar"

    def __init__(self, documento: str, cpf_solicitante: str, output_dir: str = "output"):
        super().__init__(documento, output_dir)
        self.cpf_solicitante = "".join(ch for ch in (cpf_solicitante or "") if ch.isdigit())

    def buscar(self) -> dict:
        if len(self.cpf_solicitante) != 11:
            return self.resultado("CONFIGURACAO_INCOMPLETA", erro="CPF do solicitante da SEF-SC deve ter 11 dígitos.")
        payload = {
            "Identificacao": {
                "Tipo": "Cpf" if self.tipo == "cpf" else "Cnpj",
                "Numero": self.documento,
            },
            "CpfSolicitante": self.cpf_solicitante,
        }
        try:
            response = requests.post(self.URL, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            pdf = data.get("Pdf") or data.get("pdf")
            if not pdf:
                self.salvar_debug("04_CND_Estadual_SC_resposta.json", response.text)
                return self.resultado("SEM_PDF", tipo_resultado=data.get("Tipo"), detalhe="A SEF-SC não retornou o campo Pdf.")
            destino = self.salvar_pdf(extrair_pdf_base64(pdf), "04_CND_Estadual_SC.pdf")
            tipo_resultado = data.get("Tipo", "Desconhecido")
            status = "OK" if tipo_resultado in ("Negativa", "PositivaComEfeitoDeNegativa") else "IRREGULAR"
            return self.resultado(status, destino, tipo_resultado=tipo_resultado)
        except Exception as exc:
            return self.resultado("ERRO", erro=str(exc))
