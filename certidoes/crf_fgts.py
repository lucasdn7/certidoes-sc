from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from .base import CertidaoFetcher
from .utils import resposta_e_pdf, url_absoluta


class CrfFgts(CertidaoFetcher):
    nome = "CRF/FGTS (Caixa)"
    validade_dias = 30
    URL = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
    PORTAL_URL = "https://consulta-crf.caixa.gov.br/"

    def buscar(self) -> dict:
        if self.tipo != "cnpj":
            return self.resultado("NAO_APLICAVEL", detalhe="Nesta versão, o CRF/FGTS é tentado apenas para CNPJ.")
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CertidoesSC/0.1)"})
        try:
            response = session.get(self.URL, timeout=30)
            if response.status_code in (401, 403):
                return self.resultado("ACAO_MANUAL", portal_url=self.PORTAL_URL, detalhe="A Caixa bloqueou a consulta automatizada. Abra o portal oficial para emitir o CRF.")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            if not form:
                self.salvar_debug("03_CRF_FGTS_debug.html", response.text)
                return self.resultado("VERIFICAR_MANUALMENTE", detalhe="Formulário da Caixa não localizado; HTML salvo.")
            action = url_absoluta(response.url, form.get("action") or response.url)
            data = {field.get("name"): field.get("value", "") for field in form.find_all("input", attrs={"name": True})}
            campo = next((name for name in data if any(term in name.lower() for term in ("cnpj", "inscricao", "empregador"))), None)
            if not campo:
                campo = "cnpj"
            data[campo] = self.documento
            enviado = session.post(action, data=data, timeout=30)
            enviado.raise_for_status()
            if resposta_e_pdf(enviado):
                destino = self.salvar_pdf(enviado.content, "03_CRF_FGTS.pdf")
                return self.resultado("OK", destino)
            soup = BeautifulSoup(enviado.text, "html.parser")
            pdf_link = next((a.get("href") for a in soup.find_all("a", href=True) if "pdf" in a.get("href", "").lower() or "certificado" in a.get_text(" ", strip=True).lower()), None)
            if pdf_link:
                pdf_response = session.get(url_absoluta(enviado.url, pdf_link), timeout=30)
                if resposta_e_pdf(pdf_response):
                    destino = self.salvar_pdf(pdf_response.content, "03_CRF_FGTS.pdf")
                    return self.resultado("OK", destino)
            self.salvar_debug("03_CRF_FGTS_debug.html", enviado.text)
            return self.resultado("VERIFICAR_MANUALMENTE", detalhe="A resposta não trouxe PDF; HTML salvo para diagnóstico.")
        except Exception as exc:
            return self.resultado("ACAO_MANUAL", portal_url=self.PORTAL_URL, detalhe=f"O portal da Caixa não aceitou a consulta automatizada: {exc}")
