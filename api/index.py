from __future__ import annotations

import base64
import json
import tempfile
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from certidoes import (
    CndEstadualSC, CndFederal, CndMunicipalBetha, CndMunicipalFlorianopolis,
    Cndt, CrfFgts, CertidaoFalencia, DividaAtivaPgeSC, MUNICIPIOS_BETHA,
)
from certidoes.utils import validar_documento


ALLOWED = {"federal", "estadual", "cndt", "fgts", "pge", "municipal", "pmf", "falencia"}


def make_fetcher(tipo, documento, cpf_solicitante, municipio, pasta):
    if tipo == "federal": return CndFederal(documento, str(pasta))
    if tipo == "estadual": return CndEstadualSC(documento, cpf_solicitante, str(pasta))
    if tipo == "cndt": return Cndt(documento, str(pasta))
    if tipo == "fgts": return CrfFgts(documento, str(pasta))
    if tipo == "pge": return DividaAtivaPgeSC(documento, str(pasta))
    if tipo == "municipal": return CndMunicipalBetha(documento, municipio, str(pasta))
    if tipo == "pmf": return CndMunicipalFlorianopolis(documento, str(pasta))
    if tipo == "falencia": return CertidaoFalencia(documento, str(pasta))
    raise ValueError(f"Certidão inválida: {tipo}")


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self): self._send(204, {})
    def do_GET(self): self._send(200, {"ok": True, "service": "certidoes-sc", "message": "API online"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 32_000: return self._send(413, {"error": "Requisição muito grande."})
            data = json.loads(self.rfile.read(length) or b"{}")
            ok, documento = validar_documento(str(data.get("documento", "")))
            if not ok: return self._send(400, {"error": documento})
            cpf = str(data.get("cpf_solicitante", ""))
            municipio = str(data.get("municipio", "joinville"))
            selecionadas = data.get("certidoes") or ["federal", "estadual", "cndt", "fgts"]
            if not isinstance(selecionadas, list) or not selecionadas: return self._send(400, {"error": "Selecione pelo menos uma certidão."})
            invalidas = [x for x in selecionadas if x not in ALLOWED]
            if invalidas: return self._send(400, {"error": "Certidão inválida: " + ", ".join(invalidas)})
            if "municipal" in selecionadas and municipio not in MUNICIPIOS_BETHA:
                return self._send(400, {"error": "Selecione um município Betha válido."})
            resultados = []
            with tempfile.TemporaryDirectory(prefix="certidoes-sc-") as temp:
                pasta = Path(temp)
                for tipo in selecionadas:
                    try:
                        resultado = make_fetcher(tipo, documento, cpf, municipio, pasta).buscar()
                    except Exception as exc:
                        resultado = {"certidao": tipo, "status": "ERRO", "erro": str(exc)}
                    arquivo = resultado.get("arquivo")
                    if arquivo and Path(arquivo).exists():
                        path = Path(arquivo)
                        resultado["download"] = {"nome": path.name, "conteudo_base64": base64.b64encode(path.read_bytes()).decode("ascii")}
                    resultado.pop("arquivo", None)
                    resultados.append(resultado)
            return self._send(200, {"documento": documento, "resultados": resultados})
        except json.JSONDecodeError: return self._send(400, {"error": "JSON inválido."})
        except Exception as exc: return self._send(500, {"error": f"Erro interno: {exc}"})

    def log_message(self, format, *args): return
