#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
White Chat Server — feed de videos, lives, DMs, perfis e painel admin (somente stdlib).
Uso: python3 server.py [porta]
Abra http://IP:PORTA no navegador (SPA React) e use o app Android.
"""

import base64
import json
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(BASE, "web", "dist")
UPLOADS = os.path.join(BASE, "web", "uploads")
DIR = os.path.dirname(os.path.abspath(__file__))
ARQ = lambda n: os.path.join(DIR, n)

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
ADMIN_TOKEN = "wcadm-2026"

LOCK = threading.Lock()
SEQUENCIA = 0
ROOMS = {}
SINAIS = {}
PERFIS = {}
POSTS = []
REPORTS = []
LIVES = {}
CONFIG = {"server": "http://192.168.0.10:8000"}
DM_INDEX = {}
USERS_EXTRA = []

SEED_USERS = [
    {"username": "ana", "name": "Ana Souza", "bio": "💖 vida, dança e trend", "status": "ativo", "criado": "2026-08-01"},
    {"username": "leo_dev", "name": "Leo", "bio": "🚀 hacker do bem • dev", "status": "ativo", "criado": "2026-08-02"},
    {"username": "maria", "name": "Maria Lima", "bio": "🎵 música e arte", "status": "ativo", "criado": "2026-08-03"},
    {"username": "joao", "name": "João Pedro", "bio": "🎮 gamer", "status": "ativo", "criado": "2026-08-04"},
    {"username": "bia", "name": "Bia Costa", "bio": "✨ lifestyle", "status": "ativo", "criado": "2026-08-05"},
    {"username": "kaua", "name": "Kauã", "bio": "🔥 treinos", "status": "ativo", "criado": "2026-08-06"}
]

GRADS = [["#1a0533", "#FE2C55"], ["#03212b", "#25F4EE"], ["#2b0517", "#7c3aed"],
         ["#1c1c00", "#f59e0b"], ["#001f14", "#10b981"], ["#0b1030", "#3b82f6"]]
EMOJIS = ["💃", "🔥", "🎵", "⚡", "💥", "👾", "✨", "🎸"]


def _carregar():
    global PERFIS, POSTS, REPORTS, LIVES, CONFIG, DM_INDEX, USERS_EXTRA
    for n, alvo in [("perfis.json", "PERFIS"), ("posts.json", "POSTS"), ("reports.json", "REPORTS"),
                    ("lives.json", "LIVES"), ("config.json", "CONFIG"), ("dm.json", "DM_INDEX"),
                    ("users.json", "USERS_EXTRA")]:
        try:
            with open(ARQ(n), "r", encoding="utf-8") as f:
                globals()[alvo] = json.load(f)
        except Exception:
            pass


def _salvar(nome, dados):
    try:
        with open(ARQ(nome), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _novo_id():
    global SEQUENCIA
    SEQUENCIA += 1
    return SEQUENCIA


def _enviar(room, user, text):
    with LOCK:
        m = {"id": _novo_id(), "user": user[:30], "text": text[:1000],
             "ts": time.strftime("%H:%M:%S")}
        ROOMS.setdefault(room, []).append(m)
        ROOMS[room] = ROOMS[room][-200:]
        return m


def _novas(room, depois):
    with LOCK:
        return [m for m in ROOMS.get(room, []) if m["id"] > depois]


def _add_sinal(room, de, tipo, payload):
    with LOCK:
        s = {"id": _novo_id(), "de": de[:40], "tipo": tipo[:20], "payload": payload}
        SINAIS.setdefault(room, []).append(s)
        SINAIS[room] = SINAIS[room][-500:]
        if room.startswith("live:") and tipo == "join" and room[5:] in LIVES:
            LIVES[room[5:]]["viewers"] += 1
            _salvar("lives.json", LIVES)
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


def _usuarios():
    mapa = {}
    for u, v in PERFIS.items():
        p = dict(v)
        p.setdefault("username", u)
        p.setdefault("name", v.get("name", u))
        p.setdefault("status", "ativo")
        mapa[u] = p
    for u in SEED_USERS + USERS_EXTRA:
        if u["username"] not in mapa:
            mapa[u["username"]] = u
    return list(mapa.values())


def _eh_admin(h):
    auth = h.headers.get("Authorization", "")
    return auth == "Bearer " + ADMIN_TOKEN


def _resposta_nao_autorizado(h):
    h._json({"erro": "nao autorizado"}, 401)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _headers(self, code=200, tipo="application/json; charset=utf-8", tam=0):
        self.send_response(code)
        self.send_header("Content-Type", tipo)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(tam))
        self.end_headers()

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self._headers(code, tam=len(data))
        self.wfile.write(data)

    def _arquivo(self, caminho, tipo, code=200):
        try:
            with open(caminho, "rb") as f:
                dados = f.read()
            self._headers(code, tipo=tipo, tam=len(dados))
            self.wfile.write(dados)
            return True
        except OSError:
            return False

    def do_OPTIONS(self):
        self._headers()

    def _servir_spa(self):
        caminho = urlparse(self.path).path
        if caminho == "/":
            caminho = "/index.html"
        if caminho.startswith("/uploads/"):
            alvo = os.path.join(UPLOADS, caminho[len("/uploads/"):])
            if self._arquivo(alvo, self._tipo(alvo)):
                return
        alvo = os.path.realpath(os.path.join(DIST, caminho.lstrip("/")))
        if os.path.realpath(DIST) + os.sep in alvo + os.sep and os.path.isfile(alvo):
            if self._arquivo(alvo, self._tipo(alvo)):
                return
        idx = os.path.join(DIST, "index.html")
        if not self._arquivo(idx, "text/html; charset=utf-8"):
            self._json({"erro": "build do app nao encontrado (rode npm run build)"}, 404)

    @staticmethod
    def _tipo(p):
        e = p.rsplit(".", 1)[-1].lower()
        return {"js": "application/javascript", "css": "text/css", "html": "text/html; charset=utf-8",
                "json": "application/json", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml", "mp4": "video/mp4",
                "webm": "video/webm", "ico": "image/x-icon", "woff2": "font/woff2"}.get(e, "application/octet-stream")

    # ---------------- GET ----------------
    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)
        if p.path in ("/", "/index.html") or not p.path.startswith("/api/"):
            self._servir_spa()
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
                self._json({"erro": "sala obrigatoria"}, 400)
                return
            self._json(_long_poll(_sinais_novos, room, depois))
            return
        if p.path == "/api/profile":
            user = q.get("username", [""])[0][:30]
            self._json({"ok": True, "perfil": PERFIS.get(user)})
            return
        if p.path == "/api/profiles":
            self._json({"ok": True, "perfis": [{"username": u["username"], "name": u.get("name", u["username"]), "bio": u.get("bio", "")} for u in _usuarios()]})
            return
        if p.path == "/api/posts":
            alvo = q.get("status", ["aprovado"])[0]
            status = {"approved": "aprovado", "pending": "pendente", "rejected": "reprovado"}.get(alvo, alvo)
            autor = q.get("author", [""])[0]
            lista = POSTS if status == "all" else [x for x in POSTS if x["status"] == status]
            if autor:
                lista = [x for x in lista if x["author"] == autor]
            ordem = sorted(lista, key=lambda x: (x.get("fixado", False), x["id"]), reverse=True)
            self._json({"ok": True, "posts": ordem})
            return
        if p.path == "/api/lives":
            agora = time.time()
            ativas = [v for v in LIVES.values() if agora - v["last_seen"] < 90]
            self._json({"ok": True, "lives": sorted(ativas, key=lambda x: x["viewers"], reverse=True)})
            return
        if p.path == "/api/conversas":
            user = q.get("user", [""])[0][:30]
            if not user:
                self._json({"ok": True, "conversas": []})
                return
            convs = []
            for room, c in DM_INDEX.get(user, {}).items():
                outro = c["other"]
                perfil = PERFIS.get(outro, {})
                convs.append({"user": outro, "name": perfil.get("name", outro),
                              "last": c.get("last", ""), "hora": c.get("ts", ""), "unread": c.get("unread", 0)})
            self._json({"ok": True, "conversas": sorted(convs, key=lambda x: x.get("hora", ""), reverse=True)})
            return
        if p.path == "/api/reports":
            self._json({"ok": True, "reports": sorted(REPORTS, key=lambda x: x.get("id", 0), reverse=True)})
            return
        if p.path == "/api/admin/stats":
            if not _eh_admin(self):
                return _resposta_nao_autorizado(self)
            agora = time.time()
            hoje = time.strftime("%Y-%m-%d")
            ativas = sum(1 for v in LIVES.values() if agora - v["last_seen"] < 90)
            pendentes = sum(1 for r in REPORTS if r.get("status") == "pendente")
            self._json({"ok": True, "stats": {
                "usuarios": len(_usuarios()),
                "postsHoje": sum(1 for x in POSTS if x.get("data", "").startswith(hoje)),
                "lives": ativas,
                "denuncias": pendentes}})
            return
        if p.path == "/api/users":
            if not _eh_admin(self):
                return _resposta_nao_autorizado(self)
            self._json({"ok": True, "users": _usuarios()})
            return
        if p.path == "/api/config":
            self._json({"ok": True, "config": CONFIG})
            return
        self._json({"erro": "rota desconhecida"}, 404)

    # ---------------- POST ----------------
    def do_POST(self):
        p = urlparse(self.path)
        tam = int(self.headers.get("Content-Length", 0))
        try:
            raw = self.rfile.read(tam).decode("utf-8") if tam > 0 else ""
            dados = json.loads(raw) if raw.strip() else {}
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
            self._json({"ok": True, "id": _enviar(room, user, text)["id"]})
            return
        if p.path == "/api/dm":
            de = str(dados.get("de", ""))[:30]
            para = str(dados.get("para", ""))[:30]
            text = str(dados.get("text", ""))[:1000]
            if not de or not para or not text.strip():
                self._json({"erro": "de/para/texto obrigatorios"}, 400)
                return
            room = "dm:" + ":".join(sorted([de, para]))
            m = _enviar(room, de, text)
            for u in (de, para):
                outro = para if u == de else de
                idx = DM_INDEX.setdefault(u, {})
                c = idx.setdefault(room, {"other": outro, "unread": 0})
                c["last"] = text
                c["ts"] = m["ts"]
                if u == para:
                    c["unread"] = c.get("unread", 0) + 1
            _salvar("dm.json", DM_INDEX)
            self._json({"ok": True, "id": m["id"]})
            return
        if p.path == "/api/dm/read":
            user = str(dados.get("user", ""))[:30]
            room = str(dados.get("room", ""))[:60]
            if user in DM_INDEX and room in DM_INDEX[user]:
                DM_INDEX[user][room]["unread"] = 0
                _salvar("dm.json", DM_INDEX)
            self._json({"ok": True})
            return
        if p.path == "/api/profile":
            user = str(dados.get("username", ""))[:30]
            name = str(dados.get("name", user))[:50]
            bio = str(dados.get("bio", ""))[:300]
            avatar = str(dados.get("avatar", ""))[:200000]
            if not user.strip():
                self._json({"erro": "username obrigatorio"}, 400)
                return
            perfil = {"username": user, "name": name, "bio": bio, "avatar": avatar,
                      "criado": PERFIS.get(user, {}).get("criado", time.strftime("%Y-%m-%d %H:%M"))}
            PERFIS[user] = perfil
            _salvar("perfis.json", PERFIS)
            self._json({"ok": True, "perfil": perfil})
            return
        if p.path == "/api/signal":
            room = str(dados.get("room", ""))[:50]
            de = str(dados.get("from", "anonimo"))[:40]
            tipo = str(dados.get("type", "msg"))[:20]
            payload = dados.get("payload")
            if not room:
                self._json({"erro": "sala obrigatoria"}, 400)
                return
            self._json({"ok": True, "id": _add_sinal(room, de, tipo, payload)["id"]})
            return
        if p.path == "/api/lives":
            canal = str(dados.get("canal", ""))[:50]
            user = str(dados.get("user", "anonimo"))[:30]
            ligar = bool(dados.get("on", True))
            if not canal:
                self._json({"erro": "canal obrigatorio"}, 400)
                return
            if ligar:
                if canal not in LIVES:
                    LIVES[canal] = {"canal": canal, "user": user, "viewers": random.randint(150, 4200),
                                    "inicio": time.strftime("%H:%M"), "last_seen": time.time()}
                else:
                    LIVES[canal]["last_seen"] = time.time()
                    LIVES[canal]["user"] = user
            else:
                LIVES.pop(canal, None)
            _salvar("lives.json", LIVES)
            self._json({"ok": True})
            return
        if p.path == "/api/posts":
            autor = str(dados.get("author", ""))[:30] or "anonimo"
            autor_nome = str(dados.get("autorNome", autor))[:50]
            legenda = str(dados.get("legenda", ""))[:150]
            musica = str(dados.get("musica", "som original"))[:80]
            media_url = ""
            if dados.get("mediaB64"):
                try:
                    os.makedirs(UPLOADS, exist_ok=True)
                    ext = "mp4" if str(dados.get("mediaType", "")).startswith("video") else "jpg"
                    nome = "m" + str(int(time.time() * 1000)) + "." + ext
                    with open(os.path.join(UPLOADS, nome), "wb") as f:
                        f.write(base64.b64decode(str(dados.get("mediaB64")).split(",")[-1]))
                    media_url = "/uploads/" + nome
                except Exception:
                    pass
            with LOCK:
                post = {"id": _novo_id(), "author": autor, "autorNome": autor_nome, "legenda": legenda,
                        "musica": musica, "likes": 0, "comentarios": 0, "compartilhamentos": 0,
                        "gradient": random.choice(GRADS), "emoji": random.choice(EMOJIS),
                        "status": "pendente", "fixado": False,
                        "data": time.strftime("%Y-%m-%d"), "views": 0, "mediaUrl": media_url}
                POSTS.append(post)
                _salvar("posts.json", POSTS)
            self._json({"ok": True, "post": post})
            return
        if p.path == "/api/reports":
            if not _eh_admin(self):
                return _resposta_nao_autorizado(self)
            r = {"id": _novo_id(), "post": str(dados.get("post", ""))[:60], "autor": str(dados.get("autor", ""))[:30],
                 "motivo": str(dados.get("motivo", ""))[:200], "data": time.strftime("%Y-%m-%d"), "status": "pendente"}
            REPORTS.append(r)
            _salvar("reports.json", REPORTS)
            self._json({"ok": True, "report": r})
            return
        if p.path == "/api/admin/login":
            if str(dados.get("user", "")) == ADMIN_USER and str(dados.get("password", "")) == ADMIN_PASS:
                self._json({"ok": True, "token": ADMIN_TOKEN})
            else:
                self._json({"ok": False, "erro": "credenciais invalidas"}, 401)
            return
        if p.path == "/api/config":
            if not _eh_admin(self):
                return _resposta_nao_autorizado(self)
            CONFIG["server"] = str(dados.get("server", CONFIG.get("server", "")))[:200]
            _salvar("config.json", CONFIG)
            self._json({"ok": True, "config": CONFIG})
            return

        # rotas admin com parametros no path
        partes = p.path.split("/")
        if len(partes) == 5 and partes[1] == "api":
            if partes[2] == "posts":
                try:
                    pid = int(partes[3])
                except ValueError:
                    self._json({"erro": "id invalido"}, 400)
                    return
                acao = partes[4]
                post = next((x for x in POSTS if x["id"] == pid), None)
                if not post:
                    self._json({"erro": "post nao encontrado"}, 404)
                    return
                if acao == "like":
                    post["likes"] += 1
                    _salvar("posts.json", POSTS)
                    self._json({"ok": True, "likes": post["likes"]})
                    return
                if not _eh_admin(self):
                    return _resposta_nao_autorizado(self)
                if acao == "approve":
                    post["status"] = "aprovado"
                elif acao == "reject":
                    post["status"] = "reprovado"
                elif acao == "pin":
                    post["fixado"] = not post.get("fixado", False)
                elif acao == "delete":
                    POSTS.remove(post)
                else:
                    self._json({"erro": "acao desconhecida"}, 400)
                    return
                _salvar("posts.json", POSTS)
                self._json({"ok": True, "post": post})
                return
            if not _eh_admin(self):
                return _resposta_nao_autorizado(self)
            if partes[2] == "users":
                u = partes[3]
                acao = partes[4]
                for alvo in (SEED_USERS, USERS_EXTRA):
                    for usr in alvo:
                        if usr["username"] == u:
                            if acao == "ban":
                                usr["status"] = "banido"
                            elif acao == "unban":
                                usr["status"] = "ativo"
                            elif acao == "delete":
                                alvo.remove(usr)
                            _salvar("users.json", USERS_EXTRA)
                            self._json({"ok": True, "msg": "acao aplicada"})
                            return
                self._json({"erro": "usuario nao encontrado"}, 404)
                return
            if partes[2] == "reports":
                try:
                    rid = int(partes[3])
                except ValueError:
                    self._json({"erro": "id invalido"}, 400)
                    return
                if partes[4] == "resolve":
                    for r in REPORTS:
                        if r["id"] == rid:
                            r["status"] = "resolvido"
                            _salvar("reports.json", REPORTS)
                            self._json({"ok": True, "report": r})
                            return
                self._json({"erro": "denuncia nao encontrada"}, 404)
                return
        self._json({"erro": "rota desconhecida"}, 404)


def main():
    import sys
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.makedirs(UPLOADS, exist_ok=True)
    _carregar()
    srv = ThreadingHTTPServer(("0.0.0.0", porta), Handler)
    print("White Chat rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
    srv.serve_forever()


if __name__ == "__main__":
    main()
