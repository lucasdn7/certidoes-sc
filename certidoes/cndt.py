from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from .base import CertidaoFetcher
from .utils import resposta_e_pdf, url_absoluta


class Cndt(CertidaoFetcher):
    nome = "CNDT (TST)"
    validade_dias = 180
    URL = "https://cndt-certidao.tst.jus.br/gerarCertidao"
    PORTAL_URL = "https://cndt-certidao.tst.jus.br/gerarCertidao"

    def buscar(self) -> dict:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CertidoesSC/0.1)"})
        try:
            response = session.get(self.URL, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.find("form")
            if not form:
                self.salvar_debug("02_CNDT_debug.html", response.text)
                return self.resultado("ACAO_MANUAL", portal_url=self.PORTAL_URL, detalhe="O portal da CNDT não disponibilizou um formulário automatizável.")
            if soup.find(string=lambda text: text and "caracteres exibidos" in text.lower()):
                return self.resultado("ACAO_MANUAL", portal_url=self.PORTAL_URL, detalhe="O portal exige CAPTCHA. Abra o portal oficial para concluir a emissão.")
            action = url_absoluta(response.url, form.get("action") or response.url)
            data = {field.get("name"): field.get("value", "") for field in form.find_all("input", attrs={"name": True})}
            campo = next((name for name in data if name.lower() in {"nrinscricao", "numero", "cpfcnpj", "documento"}), None)
            if not campo:
                campo = "nrInscricao"
            data[campo] = self.documento
            enviado = session.post(action, data=data, timeout=30)
            enviado.raise_for_status()
            if resposta_e_pdf(enviado):
                destino = self.salvar_pdf(enviado.content, "02_CNDT.pdf")
                return self.resultado("OK", destino)
            soup = BeautifulSoup(enviado.text, "html.parser")
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            pdf_link = next((href for href in links if "pdf" in href.lower() or "certidao" in href.lower()), None)
            if pdf_link:
                pdf_response = session.get(url_absoluta(enviado.url, pdf_link), timeout=30)
                if resposta_e_pdf(pdf_response):
                    destino = self.salvar_pdf(pdf_response.content, "02_CNDT.pdf")
                    return self.resultado("OK", destino)
            self.salvar_debug("02_CNDT_debug.html", enviado.text)
            return self.resultado("VERIFICAR_MANUALMENTE", detalhe="A resposta não trouxe PDF; HTML salvo para diagnóstico.")
        except Exception as exc:
            return self.resultado("ERRO", erro=str(exc))
