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
                "Type": "Cpf" if self.tipo == "cpf" else "Cnpj",
                "Value": self.documento,
            },
            "CpfSolicitante": {
                "Type": "Cpf",
                "Value": self.cpf_solicitante,
            },
        }
        try:
            response = requests.post(self.URL, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            result_code = data.get("ResultCode")
            result_data = data.get("Data") or {}
            arquivo = result_data.get("ArquivoCndPdf") or {}
            pdf = arquivo.get("Dados") or data.get("Pdf") or data.get("pdf")
            if not pdf:
                self.salvar_debug("04_CND_Estadual_SC_resposta.json", response.text)
                mensagens = data.get("Messages") or data.get("Message") or "A SEF-SC não retornou o PDF."
                return self.resultado("SEM_PDF", result_code=result_code, tipo_resultado=result_data.get("Tipo") or data.get("Tipo"), detalhe=str(mensagens))
            destino = self.salvar_pdf(extrair_pdf_base64(pdf), "04_CND_Estadual_SC.pdf")
            tipo_resultado = result_data.get("Tipo") or data.get("Tipo", "Desconhecido")
            status = "OK" if tipo_resultado in ("Negativa", "PositivaComEfeitoDeNegativa") else "IRREGULAR"
            return self.resultado(status, destino, tipo_resultado=tipo_resultado, numero=result_data.get("Numero"), validade=result_data.get("DataValidade"))
        except Exception as exc:
            return self.resultado("ERRO", erro=str(exc))
