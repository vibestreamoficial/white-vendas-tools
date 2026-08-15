#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram starter (white) — modelo para revender/instalar.
Uso: python3 telegram_bot_starter.py SEU_TOKEN_AQUI
Como pegar o token: fale com @BotFather no Telegram → /newbot → copie o token.
"""
import json
import sys
import time
import urllib.request

API = "https://api.telegram.org"


def chamar(method, dados=None):
    url = API + "/bot" + TOKEN + "/" + method
    data = json.dumps(dados or {}).encode() if dados else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def responder(chat_id, texto):
    chamar("sendMessage", {"chat_id": chat_id, "text": texto})


def tratar(m):
    chat = m.get("chat", {}).get("id")
    texto = (m.get("text") or "").strip().lower()
    if not chat:
        return
    if texto in ("/start", "/ajuda", "/help"):
        responder(chat, "👋 Bot online!\nComandos: /start • /info • /regras\nResposta automática ativa.")
    elif texto == "/info":
        responder(chat, "🤖 Bot educacional white hat.\nCódigo aberto e auditável.")
    elif texto == "/regras":
        responder(chat, "📜 Sem spam, sem golpe, sem conteúdo ilegal.")
    elif texto:
        responder(chat, "Você disse: " + texto)


def main():
    global TOKEN
    if len(sys.argv) < 2:
        print("Uso: python3 telegram_bot_starter.py SEU_TOKEN")
        sys.exit(1)
    TOKEN = sys.argv[1]
    offset = 0
    print("Bot rodando... (Ctrl+C para parar)")
    while True:
        try:
            r = chamar("getUpdates", {"offset": offset, "timeout": 30})
            for up in r.get("result", []):
                offset = up["update_id"] + 1
                if up.get("message"):
                    tratar(up["message"])
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Erro:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
