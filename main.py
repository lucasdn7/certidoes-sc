from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

from certidoes import CndEstadualSC, Cndt, CrfFgts
from certidoes.utils import validar_documento


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Certidões SC — Protótipo")
        self.geometry("780x560")
        self.minsize(700, 480)
        self.events = queue.Queue()
        self.running = False
        self._build_ui()
        self.after(100, self._consume_events)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Emissão de certidões — SC", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Protótipo local: CND Estadual SC, CNDT e CRF/FGTS", foreground="#555").pack(anchor="w", pady=(2, 16))

        form = ttk.LabelFrame(frame, text="Dados da consulta", padding=12)
        form.pack(fill="x")
        ttk.Label(form, text="CPF ou CNPJ:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        self.documento = tk.StringVar()
        ttk.Entry(form, textvariable=self.documento, width=30).grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(form, text="CPF do solicitante SEF-SC:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        self.cpf_solicitante = tk.StringVar()
        ttk.Entry(form, textvariable=self.cpf_solicitante, width=30, show="*").grid(row=1, column=1, sticky="w", pady=5)
        ttk.Label(form, text="Obrigatório para a CND Estadual SC", foreground="#777").grid(row=1, column=2, sticky="w", padx=8)

        checks = ttk.LabelFrame(frame, text="Certidões a emitir", padding=10)
        checks.pack(fill="x", pady=12)
        self.opt_sc = tk.BooleanVar(value=True)
        self.opt_cndt = tk.BooleanVar(value=True)
        self.opt_crf = tk.BooleanVar(value=True)
        ttk.Checkbutton(checks, text="CND Estadual SC", variable=self.opt_sc).pack(side="left", padx=(0, 18))
        ttk.Checkbutton(checks, text="CNDT (TST)", variable=self.opt_cndt).pack(side="left", padx=(0, 18))
        ttk.Checkbutton(checks, text="CRF/FGTS (CNPJ)", variable=self.opt_crf).pack(side="left")

        self.start_button = ttk.Button(frame, text="Emitir e baixar certidões", command=self.start)
        self.start_button.pack(anchor="w", pady=(0, 12))
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x")
        self.status = ttk.Label(frame, text="Pronto.", foreground="#444")
        self.status.pack(anchor="w", pady=(6, 6))
        self.log = tk.Text(frame, height=18, wrap="word", state="disabled", background="#f7f7f7")
        self.log.pack(fill="both", expand=True)

    def write_log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        if self.running:
            return
        ok, documento = validar_documento(self.documento.get())
        if not ok:
            messagebox.showerror("Documento inválido", documento)
            return
        if not any((self.opt_sc.get(), self.opt_cndt.get(), self.opt_crf.get())):
            messagebox.showwarning("Seleção vazia", "Selecione pelo menos uma certidão.")
            return
        self.running = True
        self.start_button.configure(state="disabled")
        self.progress.start(10)
        self.write_log(f"\nConsulta iniciada para {documento} em {datetime.now():%d/%m/%Y %H:%M:%S}")
        cpf_solicitante = self.cpf_solicitante.get()
        selecoes = (self.opt_sc.get(), self.opt_cndt.get(), self.opt_crf.get())
        threading.Thread(target=self._worker, args=(documento, cpf_solicitante, selecoes), daemon=True).start()

    def _worker(self, documento: str, cpf_solicitante: str, selecoes: tuple[bool, bool, bool]):
        resultados = []
        tarefas = []
        opt_sc, opt_cndt, opt_crf = selecoes
        if opt_sc:
            tarefas.append(("CND Estadual SC", lambda: CndEstadualSC(documento, cpf_solicitante).buscar()))
        if opt_cndt:
            tarefas.append(("CNDT", lambda: Cndt(documento).buscar()))
        if opt_crf:
            tarefas.append(("CRF/FGTS", lambda: CrfFgts(documento).buscar()))
        for nome, tarefa in tarefas:
            self.events.put(("log", f"→ Processando {nome}..."))
            try:
                resultado = tarefa()
            except Exception as exc:
                resultado = {"certidao": nome, "status": "ERRO", "erro": str(exc)}
            resultados.append(resultado)
            self.events.put(("log", self._format_result(resultado)))
        pasta = Path("output") / documento / datetime.now().strftime("%Y-%m-%d")
        pasta.mkdir(parents=True, exist_ok=True)
        log_path = pasta / "log.json"
        log_path.write_text(json.dumps({"documento": documento, "data": datetime.now().isoformat(), "resultados": resultados}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.events.put(("done", str(log_path)))

    @staticmethod
    def _format_result(result: dict) -> str:
        status = result.get("status", "?")
        arquivo = result.get("arquivo")
        detalhe = result.get("erro") or result.get("detalhe") or ""
        return f"  {result.get('certidao')}: {status}" + (f" — {arquivo}" if arquivo else "") + (f" — {detalhe}" if detalhe else "")

    def _consume_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.write_log(value)
                else:
                    self.write_log(f"Log salvo em: {value}")
                    self.write_log("Consulta concluída. PDFs, quando obtidos, estão na pasta output.")
                    self.status.configure(text="Concluído.")
                    self.running = False
                    self.start_button.configure(state="normal")
                    self.progress.stop()
        except queue.Empty:
            pass
        self.after(100, self._consume_events)


if __name__ == "__main__":
    App().mainloop()
