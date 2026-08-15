#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API DE SENHAS (white) — gerador de senhas fortes + checker de forca.
CLI:  python3 api_senhas.py gerar 16 | python3 api_senhas.py forca 'SuaSenha'
HTTP: python3 api_senhas.py --server 8002
   GET http://IP:8002/api/senha/gerar?len=16
   GET http://IP:8002/api/senha/forca?senha=Abc123!
"""
import json
import re
import secrets
import string
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def gerar(tamanho=16):
    pool = string.ascii_letters + string.digits + "!@#$%&*+-_=?"
    senha = [secrets.choice(string.ascii_uppercase), secrets.choice(string.ascii_lowercase),
             secrets.choice(string.digits), secrets.choice("!@#$%&*+-_=?")]
    while len(senha) < max(8, min(tamanho, 64)):
        senha.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(senha)
    return "".join(senha)


def forca(senha):
    nota = 0
    if len(senha) >= 8:
        nota += 1
    if len(senha) >= 12:
        nota += 1
    if re.search(r"[a-z]", senha):
        nota += 1
    if re.search(r"[A-Z]", senha):
        nota += 1
    if re.search(r"[0-9]", senha):
        nota += 1
    if re.search(r"[^a-zA-Z0-9]", senha):
        nota += 1
    nomes = {1: "MUITO FRACA", 2: "FRACA", 3: "MEDIA", 4: "BOA", 5: "FORTE", 6: "MUITO FORTE"}
    return {"forca": nomes.get(nota, "FRACA"), "pontos": nota, "tamanho": len(senha)}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)
        if p.path == "/api/senha/gerar":
            try:
                n = int(q.get("len", ["16"])[0])
            except ValueError:
                n = 16
            body = json.dumps({"ok": True, "senha": gerar(n)}).encode()
        elif p.path == "/api/senha/forca":
            body = json.dumps({"ok": True, "resultado": forca(q.get("senha", [""])[0])}, ensure_ascii=False).encode()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass


def main():
    if "--server" in sys.argv:
        try:
            porta = int(sys.argv[sys.argv.index("--server") + 1])
        except (ValueError, IndexError):
            porta = 8002
        print("API de Senhas rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
        ThreadingHTTPServer(("0.0.0.0", porta), Handler).serve_forever()
    if len(sys.argv) < 2:
        print("Uso: python3 api_senhas.py gerar 16 | forca 'Senha'")
        sys.exit(1)
    if sys.argv[1] == "gerar":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 16
        print(json.dumps({"senha": gerar(n)}))
    elif sys.argv[1] == "forca":
        s = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(forca(s), ensure_ascii=False))


if __name__ == "__main__":
    main()
