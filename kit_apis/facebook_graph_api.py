#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Graph API (white) — SOMENTE sua página/conta.
Requisitos: token de página (developers.facebook.com/tools/explorer) + id da página.

Uso: FB_TOKEN=seu_token FB_PAGE=id_da_pagina python3 facebook_graph_api.py post "Minha mensagem"
     FB_TOKEN=seu_token FB_PAGE=id_da_pagina python3 facebook_graph_api.py info
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://graph.facebook.com/v21.0"


def get(caminho, params):
    url = BASE + caminho + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    token = os.environ.get("FB_TOKEN", "")
    pagina = os.environ.get("FB_PAGE", "")
    if not token or not pagina:
        print("Faltou FB_TOKEN e/ou FB_PAGE (sua página). Veja LEIA-ME.txt.")
        sys.exit(1)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "info":
        print(json.dumps(get("/" + pagina, {"fields": "name,id,followers_count", "access_token": token}), ensure_ascii=False, indent=2))
    elif cmd == "post":
        msg = " ".join(sys.argv[2:])
        if not msg:
            print("Uso: facebook_graph_api.py post 'sua mensagem'")
            sys.exit(1)
        import urllib.request as u
        data = urllib.parse.urlencode({"message": msg, "access_token": token}).encode()
        req = u.Request(BASE + "/" + pagina + "/feed", data=data)
        with u.urlopen(req, timeout=20) as r:
            print(json.dumps(json.loads(r.read().decode()), ensure_ascii=False, indent=2))
    else:
        print("Comandos: info | post 'mensagem'")


if __name__ == "__main__":
    main()
