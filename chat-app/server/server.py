#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
White Chat Server — perfis, chat e sinalizacao de lives (somente stdlib).
Uso: python3 server.py [porta]
Abra http://IP:PORTA no navegador (web com chat + live) e use o app Android.
"""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ_PERFIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis.json")

LOCK = threading.Lock()
SEQUENCIA = 0
ROOMS = {}          # sala -> [mensagem]
SINAIS = {}         # sala -> [sinal] (sinalizacao de live)
PERFIS = {}         # username -> {name, bio, criado}


def _carregar_perfis():
    global PERFIS
    try:
        with open(ARQ_PERFIS, "r", encoding="utf-8") as f:
            PERFIS = json.load(f)
    except Exception:
        PERFIS = {}


def _salvar_perfis():
    try:
        with open(ARQ_PERFIS, "w", encoding="utf-8") as f:
            json.dump(PERFIS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _enviar(room, user, text):
    global SEQUENCIA
    with LOCK:
        SEQUENCIA += 1
        m = {"id": SEQUENCIA, "user": user[:30], "text": text[:1000],
             "ts": time.strftime("%H:%M:%S")}
        ROOMS.setdefault(room, []).append(m)
        ROOMS[room] = ROOMS[room][-200:]
        return m


def _novas(room, depois):
    with LOCK:
        return [m for m in ROOMS.get(room, []) if m["id"] > depois]


def _add_sinal(room, de, tipo, payload):
    global SEQUENCIA
    with LOCK:
        SEQUENCIA += 1
        s = {"id": SEQUENCIA, "de": de[:40], "tipo": tipo[:20], "payload": payload}
        SINAIS.setdefault(room, []).append(s)
        SINAIS[room] = SINAIS[room][-500:]
        return s


def _sinais_novos(room, depois):
    with LOCK:
        return [s for s in SINAIS.get(room, []) if s["id"] > depois]


def _long_poll(funcao, room, depois, segundos=15):
    fim = time.time() + segundos
    while time.time() < fim:
        itens = funcao(room, depois)
        if itens:
            return itens
        time.sleep(0.5)
    return []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _headers(self, code=200, tipo="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", tipo)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._headers()

    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)
        if p.path in ("/", "/index.html"):
            try:
                with open(os.path.join(BASE, "web", "index.html"), "rb") as f:
                    self._html(f.read())
            except OSError:
                self._json({"erro": "pagina nao encontrada"}, 404)
            return
        if p.path == "/messages":
            room = q.get("room", ["geral"])[0][:50]
            depois = int(q.get("after", ["0"])[0] or 0)
            self._json(_long_poll(_novas, room, depois))
            return
        if p.path == "/api/signal":
            room = q.get("room", [""])[0][:50]
            depois = int(q.get("after", ["0"])[0] or 0)
            if not room:
                self._json({"erro": "sala de sinalizacao obrigatoria"}, 400)
                return
            self._json(_long_poll(_sinais_novos, room, depois))
            return
        if p.path == "/api/profile":
            user = q.get("username", [""])[0][:30]
            self._json({"ok": True, "perfil": PERFIS.get(user)})
            return
        if p.path == "/api/profiles":
            lista = [{"username": u, "name": v.get("name", u), "bio": v.get("bio", "")}
                     for u, v in PERFIS.items()]
            self._json({"ok": True, "perfis": lista})
            return
        self._json({"erro": "rota desconhecida"}, 404)

    def do_POST(self):
        p = urlparse(self.path)
        tam = int(self.headers.get("Content-Length", 0))
        try:
            dados = json.loads(self.rfile.read(tam).decode("utf-8"))
        except Exception:
            self._json({"erro": "json invalido"}, 400)
            return
        if p.path == "/send":
            room = str(dados.get("room", "geral"))[:50]
            user = str(dados.get("user", "anonimo"))[:30] or "anonimo"
            text = str(dados.get("text", ""))[:1000]
            if not text.strip():
                self._json({"erro": "mensagem vazia"}, 400)
                return
            m = _enviar(room, user, text)
            self._json({"ok": True, "id": m["id"]})
            return
        if p.path == "/api/profile":
            user = str(dados.get("username", ""))[:30]
            name = str(dados.get("name", user))[:50]
            bio = str(dados.get("bio", ""))[:300]
            if not user.strip():
                self._json({"erro": "username obrigatorio"}, 400)
                return
            PERFIS[user] = {"name": name, "bio": bio, "criado": time.strftime("%Y-%m-%d %H:%M")}
            _salvar_perfis()
            self._json({"ok": True, "perfil": PERFIS[user]})
            return
        if p.path == "/api/signal":
            room = str(dados.get("room", ""))[:50]
            de = str(dados.get("from", "anonimo"))[:40]
            tipo = str(dados.get("type", "msg"))[:20]
            payload = dados.get("payload")
            if not room:
                self._json({"erro": "sala de sinalizacao obrigatoria"}, 400)
                return
            self._json({"ok": True, "id": _add_sinal(room, de, tipo, payload)["id"]})
            return
        self._json({"erro": "rota desconhecida"}, 404)


def main():
    import sys
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    _carregar_perfis()
    srv = ThreadingHTTPServer(("0.0.0.0", porta), Handler)
    print("White Chat rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
    srv.serve_forever()


if __name__ == "__main__":
    main()
