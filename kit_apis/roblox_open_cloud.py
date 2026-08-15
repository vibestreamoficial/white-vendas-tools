#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roblox Open Cloud API (white) — SEU usuário/SEU jogo.
Requisitos: API Key criada em create.roblox.com/dashboard/credentials
(dica: coluna "API Key" com escopo universe-api e users-api).

Uso: RBX_KEY=suakey python3 roblox_open_cloud.py user 123456
     RBX_KEY=suakey python3 roblox_open_cloud.py stats 654321
"""
import json
import os
import sys
import urllib.request

H = {"x-api-key": ""}


def get(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    chave = os.environ.get("RBX_KEY", "")
    if not chave:
        print("Faltou RBX_KEY (API Key da SUA conta Roblox). Veja LEIA-ME.txt.")
        sys.exit(1)
    H["x-api-key"] = chave
    if len(sys.argv) < 3:
        print("Uso: roblox_open_cloud.py user SEU_ID | stats SEU_UNIVERSE_ID")
        sys.exit(1)
    cmd, alvo = sys.argv[1], sys.argv[2]
    if cmd == "user":
        print(json.dumps(get("https://apis.roblox.com/cloud/v2/users/" + alvo), ensure_ascii=False, indent=2))
    elif cmd == "stats":
        print(json.dumps(get("https://apis.roblox.com/universes/v1/" + alvo + "/stats"), ensure_ascii=False, indent=2))
    else:
        print("Comandos: user | stats")


if __name__ == "__main__":
    main()
