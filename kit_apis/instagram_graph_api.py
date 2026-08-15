#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Graph API (white) — SOMENTE conta própria.
Requisitos: app Meta (developers.facebook.com) + token de acesso do USUÁRIO com
permissão instagram_basic,instagram_content_publish. Siga o LEIA-ME.txt.

Uso: IG_TOKEN=seu_token python3 instagram_graph_api.py me
     IG_TOKEN=seu_token IG_USER=id_da_conta python3 instagram_graph_api.py media
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://graph.instagram.com/v21.0"


def get(caminho, params):
    url = BASE + caminho + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    token = os.environ.get("IG_TOKEN", "")
    if not token:
        print("Faltou IG_TOKEN (token da SUA conta via Meta for Developers). Veja LEIA-ME.txt.")
        sys.exit(1)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    if cmd == "me":
        print(json.dumps(get("/me", {"fields": "id,username,account_type,media_count", "access_token": token}), ensure_ascii=False, indent=2))
    elif cmd == "media":
        user = os.environ.get("IG_USER", "")
        if not user:
            print("Defina IG_USER (seu id do Instagram).")
            sys.exit(1)
        print(json.dumps(get("/" + user + "/media", {"fields": "id,caption,media_type,permalink,timestamp", "access_token": token}), ensure_ascii=False, indent=2))
    else:
        print("Comandos: me | media")


if __name__ == "__main__":
    main()
