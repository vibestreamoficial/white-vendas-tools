#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API MONITOR DE DOMINIO (white) — avisa se o dominio caiu, SSL venceu ou site fora do ar.
Uso CLI:  python3 monitor_dominio.py exemplo.com
Uso loop: python3 monitor_dominio.py exemplo.com --loop 60 --alertas alertas.txt
Uso HTTP: python3 monitor_dominio.py --server 8000
   GET http://IP:8000/api/monitor?dominio=exemplo.com
"""
import datetime
import json
import socket
import ssl
import sys
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def checar(dominio):
    dominio = (dominio or "").strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    if not dominio:
        return {"ok": False, "erro": "dominio obrigatorio"}
    r = {"dominio": dominio, "horario": datetime.datetime.now().isoformat(timespec="seconds")}
    # 1) DNS / queda
    try:
        socket.getaddrinfo(dominio, 443)
        r["dns"] = "ok"
    except Exception:
        r["dns"] = "FALHOU (dominio nao resolve)"
    # 2) HTTPS / status HTTP
    try:
        with urllib.request.urlopen("https://" + dominio, timeout=10) as resp:
            r["http"] = resp.status
    except urllib.error.HTTPError as e:
        r["http"] = e.code
    except Exception as e:
        r["http"] = "erro: " + str(e)
    # 3) SSL / expiracao
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((dominio, 443), timeout=10) as s:
            with ctx.wrap_socket(s, server_hostname=dominio) as tls:
                cert = tls.getpeercert()
                exp = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                dias = (exp - datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)).days
                r["ssl_validade"] = exp.strftime("%Y-%m-%d")
                r["ssl_dias_restantes"] = dias
                r["ssl_status"] = "ok" if dias > 30 else ("ATENCAO" if dias > 7 else "VENCE LOGO")
    except Exception as e:
        r["ssl_status"] = "erro: " + str(e)
    return r


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/api/monitor":
            q = parse_qs(p.query)
            body = json.dumps({"ok": True, "resultado": checar(q.get("dominio", [""])[0])}, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a):
        pass


def main():
    if "--server" in sys.argv:
        try:
            porta = int(sys.argv[sys.argv.index("--server") + 1])
        except (ValueError, IndexError):
            porta = 8001
        print("Monitor de Dominio rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
        ThreadingHTTPServer(("0.0.0.0", porta), Handler).serve_forever()
    if len(sys.argv) < 2:
        print("Uso: python3 monitor_dominio.py exemplo.com [--loop SEGUNDOS]")
        sys.exit(1)
    dominio = sys.argv[1]
    intervalo = int(sys.argv[sys.argv.index("--loop") + 1]) if "--loop" in sys.argv else 0
    while True:
        res = checar(dominio)
        print(json.dumps(res, ensure_ascii=False))
        if not intervalo:
            break
        time.sleep(intervalo)


if __name__ == "__main__":
    main()
