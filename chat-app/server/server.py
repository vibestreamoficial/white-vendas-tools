#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de chat simples (somente biblioteca padrao).
Roda no PC, Kali ou Termux. Uso: python3 server.py [porta]
Abra http://IP_DA_MAQUINA:PORTA no navegador de qualquer aparelho.
"""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
ROOMS = {}
LOCK = threading.Lock()
SEQUENCIA = 0


def _novas(room, depois):
    return [m for m in ROOMS.get(room, []) if m["id"] > depois]


def _enviar(room, user, text):
    global SEQUENCIA
    with LOCK:
        SEQUENCIA += 1
        m = {"id": SEQUENCIA, "user": user[:30], "text": text[:500],
             "ts": time.strftime("%H:%M:%S")}
        ROOMS.setdefault(room, []).append(m)
        ROOMS[room] = ROOMS[room][-200:]
        return m


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        p = urlparse(self.path)
        if p.path in ("/", "/index.html"):
            try:
                with open(os.path.join(BASE, "web", "index.html"), "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except OSError:
                self._json({"erro": "pagina nao encontrada"}, 404)
                return
        if p.path == "/messages":
            q = parse_qs(p.query)
            room = q.get("room", ["geral"])[0][:50]
            depois = int(q.get("after", ["0"])[0] or 0)
            # long-poll: aguarda ate 15s por mensagem nova
            fim = time.time() + 15
            while time.time() < fim:
                lista = _novas(room, depois)
                if lista:
                    self._json(lista)
                    return
                time.sleep(0.5)
            self._json([])
            return
        self._json({"erro": "rota desconhecida"}, 404)

    def do_POST(self):
        p = urlparse(self.path)
        if p.path == "/send":
            tam = int(self.headers.get("Content-Length", 0))
            try:
                dados = json.loads(self.rfile.read(tam).decode("utf-8"))
            except Exception:
                self._json({"erro": "json invalido"}, 400)
                return
            room = str(dados.get("room", "geral"))[:50]
            user = str(dados.get("user", "anonimo"))[:30] or "anonimo"
            text = str(dados.get("text", ""))[:500]
            if not text.strip():
                self._json({"erro": "mensagem vazia"}, 400)
                return
            m = _enviar(room, user, text)
            self._json({"ok": True, "id": m["id"]})
            return
        self._json({"erro": "rota desconhecida"}, 404)


def main():
    import sys
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("0.0.0.0", porta), Handler)
    print("Chat rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
    srv.serve_forever()


if __name__ == "__main__":
    main()
