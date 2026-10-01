from __future__ import annotations

from .base import CertidaoFetcher


MUNICIPIOS_BETHA = {
    "joinville": ("Joinville", "https://joinville.betha.cloud/tributario/"),
    "blumenau": ("Blumenau", "https://blumenau.betha.cloud/tributario/"),
    "criciuma": ("Criciúma", "https://criciuma.betha.cloud/tributario/"),
    "chapeco": ("Chapecó", "https://chapeco.betha.cloud/tributario/"),
    "itajai": ("Itajaí", "https://itajai.betha.cloud/tributario/"),
    "jaragua": ("Jaraguá do Sul", "https://jaragua.betha.cloud/tributario/"),
    "palhoca": ("Palhoça", "https://palhoca.betha.cloud/tributario/"),
    "saojose": ("São José", "https://saojose.betha.cloud/tributario/"),
    "lages": ("Lages", "https://lages.betha.cloud/tributario/"),
    "balneariocamboriu": ("Balneário Camboriú", "https://balneariocamboriu.betha.cloud/tributario/"),
    "tubarao": ("Tubarão", "https://tubarao.betha.cloud/tributario/"),
}


class PortalManualFetcher(CertidaoFetcher):
    validade_dias = 0

    def __init__(self, documento: str, nome: str, portal_url: str, motivo: str, output_dir: str = "output"):
        super().__init__(documento, output_dir)
        self.nome = nome
        self.portal_url = portal_url
        self.motivo = motivo

    def buscar(self) -> dict:
        return self.resultado("ACAO_MANUAL", portal_url=self.portal_url, detalhe=self.motivo)


class CndFederal(PortalManualFetcher):
    def __init__(self, documento: str, output_dir: str = "output"):
        super().__init__(
            documento,
            "CND Federal (RFB + PGFN)",
            "https://servicos.receitafederal.gov.br/servico/certidoes/",
            "A emissão pode exigir CAPTCHA, autenticação gov.br ou certificado digital. Use o portal oficial para concluir.",
            output_dir,
        )
        self.validade_dias = 180


class DividaAtivaPgeSC(PortalManualFetcher):
    def __init__(self, documento: str, output_dir: str = "output"):
        super().__init__(
            documento,
            "Dívida Ativa Estadual SC (PGE-SC)",
            "https://www.pge.sc.gov.br/divida-ativa/",
            "Módulo opcional: a CND SEF-SC normalmente cobre a regularidade estadual; confirme a exigência no edital.",
            output_dir,
        )


class CndMunicipalBetha(PortalManualFetcher):
    def __init__(self, documento: str, municipio: str, output_dir: str = "output"):
        nome, url = MUNICIPIOS_BETHA.get(municipio, (municipio, ""))
        super().__init__(
            documento,
            f"CND Municipal — {nome}",
            url,
            "O fluxo Betha varia por município e pode exigir sessão ou CAPTCHA. Abra o portal para emitir e baixar.",
            output_dir,
        )
        self.municipio = municipio
        self.validade_dias = 60


class CndMunicipalFlorianopolis(PortalManualFetcher):
    def __init__(self, documento: str, output_dir: str = "output"):
        super().__init__(
            documento,
            "CND Municipal — Florianópolis (PMF)",
            "https://nfps-e.pmf.sc.gov.br",
            "A PMF utiliza sistema próprio e pode exigir certificado digital A1. Emita pelo portal oficial.",
            output_dir,
        )
        self.validade_dias = 60


class CertidaoFalencia(PortalManualFetcher):
    def __init__(self, documento: str, output_dir: str = "output"):
        super().__init__(
            documento,
            "Falência e Recuperação Judicial (TJ-SC)",
            "https://certidoes.tjsc.jus.br/",
            "A emissão depende da comarca sede e do distribuidor judicial. Selecione a comarca no portal do TJ-SC.",
            output_dir,
        )
