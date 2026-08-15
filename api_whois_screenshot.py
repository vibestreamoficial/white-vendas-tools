#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API WHOIS + SCREENSHOT (white/OSINT defensivo) — dados publicos de dominio.
CLI:  python3 api_whois_screenshot.py exemplo.com [--print]
HTTP: python3 api_whois_screenshot.py --server 8003
   GET http://IP:8003/api/whois?dominio=exemplo.com
Fonte: RDAP publico (rdap.org) — sem banco de dados local.
Screenshot: usa selenium se instalado (pip install selenium webdriver-manager).
"""
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def whois(dominio):
    dominio = (dominio or "").strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    if not dominio:
        return {"ok": False, "erro": "dominio obrigatorio"}
    url = "https://rdap.org/domain/" + dominio
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"ok": False, "dominio": dominio, "erro": "RDAP: " + str(e.code)}
    except Exception as e:
        return {"ok": False, "dominio": dominio, "erro": str(e)}
    entidades = d.get("entities", [])
    nomes = []
    for ent in entidades:
        v = ent.get("vcardArray", [[]])
        if len(v) > 1:
            for item in v[1]:
                if item and item[0] == "fn" and len(item) > 3:
                    nomes.append(item[3])
    eventos = {}
    for ev in d.get("events", []):
        eventos[ev.get("eventAction", "")] = ev.get("eventDate", "")
    return {
        "ok": True,
        "dominio": dominio,
        "criacao": eventos.get("registration"),
        "atualizacao": eventos.get("last changed"),
        "expiracao": eventos.get("expiration"),
        "registrador": (d.get("entities") or [{}])[0].get("handle", "n/d"),
        "titulares": nomes[:3],
        "status": d.get("status", []),
        "dnssec": d.get("secureDNS", {}).get("delegationSigned", "n/d"),
    }


def screenshot(dominio, caminho="screenshot.png"):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        return {"ok": False, "erro": "selenium nao instalado (pip install selenium webdriver-manager)"}
    opcoes = Options()
    opcoes.add_argument("--headless")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--window-size=1280,900")
    try:
        drv = webdriver.Chrome(options=opcoes)
        drv.get("https://" + dominio)
        drv.save_screenshot(caminho)
        drv.quit()
        return {"ok": True, "arquivo": caminho}
    except Exception as e:
        return {"ok": False, "erro": str(e)}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/api/whois":
            q = parse_qs(p.query)
            body = json.dumps({"ok": True, "resultado": whois(q.get("dominio", [""])[0])}, ensure_ascii=False).encode()
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
            porta = 8003
        print("API WHOIS rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
        ThreadingHTTPServer(("0.0.0.0", porta), Handler).serve_forever()
    if len(sys.argv) < 2:
        print("Uso: python3 api_whois_screenshot.py exemplo.com [--print]")
        sys.exit(1)
    res = whois(sys.argv[1])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if "--print" in sys.argv:
        print(json.dumps(screenshot(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
