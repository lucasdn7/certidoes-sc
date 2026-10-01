from pathlib import Path

from certidoes.base import CertidaoFetcher
from certidoes.utils import limpar_documento, validar_documento


def test_limpar_documento():
    assert limpar_documento("12.345.678/0001-95") == "12345678000195"


def test_validar_documentos():
    assert validar_documento("123.456.789-01")[0]
    assert validar_documento("12.345.678/0001-95")[0]
    assert not validar_documento("123")[0]


def test_saida(tmp_path: Path):
    fetcher = CertidaoFetcher("12.345.678/0001-95", str(tmp_path))
    assert fetcher.output_dir.name
    destino = fetcher.salvar_pdf(b"%PDF-1.4\nmock", "teste.pdf")
    assert destino.exists()
