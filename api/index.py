from __future__ import annotations

import base64
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from certidoes import CndEstadualSC, Cndt, CrfFgts
from certidoes.utils import validar_documento


FETCHERS = {
    "estadual": lambda documento, cpf, pasta: CndEstadualSC(documento, cpf, str(pasta)).buscar(),
    "cndt": lambda documento, cpf, pasta: Cndt(documento, str(pasta)).buscar(),
    "fgts": lambda documento, cpf, pasta: CrfFgts(documento, str(pasta)).buscar(),
}


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

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        self._send(200, {"ok": True, "service": "certidoes-sc", "message": "API online"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 32_000:
                return self._send(413, {"error": "Requisição muito grande."})
            data = json.loads(self.rfile.read(length) or b"{}")
            ok, documento = validar_documento(str(data.get("documento", "")))
            if not ok:
                return self._send(400, {"error": documento})
            cpf_solicitante = str(data.get("cpf_solicitante", ""))
            selecionadas = data.get("certidoes") or ["estadual", "cndt", "fgts"]
            if not isinstance(selecionadas, list) or not selecionadas:
                return self._send(400, {"error": "Selecione pelo menos uma certidão."})
            invalidas = [item for item in selecionadas if item not in FETCHERS]
            if invalidas:
                return self._send(400, {"error": "Certidão inválida: " + ", ".join(invalidas)})

            resultados = []
            with tempfile.TemporaryDirectory(prefix="certidoes-sc-") as temp:
                pasta = Path(temp)
                for tipo in selecionadas:
                    try:
                        resultado = FETCHERS[tipo](documento, cpf_solicitante, pasta)
                    except Exception as exc:
                        resultado = {"certidao": tipo, "status": "ERRO", "erro": str(exc)}
                    arquivo = resultado.get("arquivo")
                    if arquivo and Path(arquivo).exists():
                        path = Path(arquivo)
                        resultado["download"] = {
                            "nome": path.name,
                            "conteudo_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
                        }
                    resultado.pop("arquivo", None)
                    resultados.append(resultado)
            return self._send(200, {"documento": documento, "resultados": resultados})
        except json.JSONDecodeError:
            return self._send(400, {"error": "JSON inválido."})
        except Exception as exc:
            return self._send(500, {"error": f"Erro interno: {exc}"})

    def log_message(self, format, *args):
        # Evita registrar documentos completos nos logs públicos da função.
        return
