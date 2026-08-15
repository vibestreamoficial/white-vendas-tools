#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram - Criador de Tópicos em Grupos
Comando: /criartopico <nome do topico>
Somente administradores do grupo podem criar topicos.
Funciona apenas em grupos com "Topicos" ativados (Forum).
Uso no Termux:
  pkg install python -y
  python telegram_topics_bot.py
"""

import json
import os
import re
import secrets
import time
import urllib.parse
import urllib.request

# Troque pelo token do seu bot, se precisar
import os
TOKEN = os.environ.get("BOT_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")
API = "https://api.telegram.org/bot{}".format(TOKEN)

ADMIN_STATUS = {"creator", "administrator"}

# ===== AREA VIP =====
# Coloque seu ID do Telegram aqui (pegue em @userinfobot) para poder
# gerar codigos de acesso com /gerarcodigo.
OWNER_ID = 8974625644
# ID usado pelo Telegram quando um admin posta anonimamente no grupo
ANON_ADMIN_ID = 1087968824

CODES_FILE = "codes.json"
VIP_FILE = "vip.json"
VIP_SEED_CODE = "01G5K6P8"  # codigo inicial de demonstracao

VIP_MENU = (
    "🛡️ *ÁREA VIP — KIT SEGURANÇA & VENDAS*\n\n"
    "Ferramentas oficiais (somente conteúdo legítimo):\n"
    "• `verifica_vendedor.py` — consulta CNPJ em dados públicos (BrasilAPI)\n"
    "• `gerador_anuncio.py` — anúncio formatado para o grupo\n"
    "• `calculadora_lucro.py` — lucro e margem de cada venda\n"
    "• `planilha_vendas.py` — controle de vendas em CSV\n"
    "• Guia anti-phishing e proteção de conta (2FA)\n\n"
    "Comandos:\n"
    "`/vip` — ver este menu\n"
    "`/resgatar CÓDIGO` — ativar acesso\n"
    "`/gerarcodigo DIAS` — gerar código (apenas dono)"
)

# ===== MODERAÇÃO =====
# Xingamentos reconhecidos automaticamente (sem acentos na lista).
# Palavras avulsas só contam quando são a palavra exata (sem pegar "computador" etc.)
INSULTOS_PALAVRAS = [
    "vagabundo", "vagabunda", "vagaba", "idiota", "imbecil", "retardado",
    "retardada", "desgracado", "desgracada", "arrombado", "arrombada",
    "otario", "otaria", "escroto", "escrota", "vadia", "prostituta", "puta",
    "puto", "cuzao", "viado", "viadinho", "bosta", "merda", "babaca", "burro",
    "burra", "corno", "pilantra", "safado", "safada", "canalha", "sacana",
    "mongol", "mongoloide", "piranha", "rapariga", "vaca", "frouxo", "bundao",
    "broxa", "fdp",
]

INSULTOS_FRASES = [
    "filho da puta", "filha da puta", "filhodaputa", "pau no cu",
    "sem vergonha", "sem-vergonha",
]


def normalizar(texto):
    t = (texto or "").lower()
    for a, b in [("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"), ("é", "e"),
                 ("ê", "e"), ("í", "i"), ("ó", "o"), ("ô", "o"), ("õ", "o"),
                 ("ú", "u"), ("ü", "u"), ("ç", "c")]:
        t = t.replace(a, b)
    return t


def contem_insulto(texto):
    t = normalizar(texto)
    for w in INSULTOS_PALAVRAS:
        if re.search(r"\b" + re.escape(w) + r"\b", t):
            return True
    return any(f in t for f in INSULTOS_FRASES)


def kick_user(chat_id, user_id):
    """Remove o usuario do grupo (ban + unban = expulsao)."""
    r = api_call("banChatMember", {"chat_id": chat_id, "user_id": user_id})
    api_call("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})
    return r.get("ok")


def moderar(message):
    """Apaga mensagem ofensiva e remove o autor (so em grupos)."""
    chat = message.get("chat", {})
    if chat.get("type") not in ("group", "supergroup"):
        return
    texto = message.get("text") or message.get("caption") or ""
    if not contem_insulto(texto):
        return
    chat_id = chat["id"]
    user_id = message["from"]["id"]
    if user_id in (OWNER_ID, ANON_ADMIN_ID) or is_admin(chat_id, user_id):
        return
    api_call("deleteMessage", {"chat_id": chat_id, "message_id": message["message_id"]})
    kick_user(chat_id, user_id)
    params = {"chat_id": chat_id, "text": "🚫 Mensagem ofensiva removida e usuário removido do grupo."}
    if message.get("message_thread_id"):
        params["message_thread_id"] = message["message_thread_id"]
    api_call("sendMessage", params)


def handle_join_request(update):
    """Aprova automaticamente pedidos de entrada e da boas-vindas."""
    jr = update.get("chat_join_request")
    if not jr:
        return
    chat_id = jr.get("chat", {}).get("id")
    user = jr.get("from", {})
    user_id = user.get("id")
    nome = user.get("first_name", "membro")
    r = api_call("approveChatJoinRequest", {"chat_id": chat_id, "user_id": user_id})
    if r.get("ok"):
        api_call("sendMessage", {
            "chat_id": chat_id,
            "text": "👋 Bem-vindo(a), {}! Leia as regras no tópico 📌 Regras e boas vendas!".format(nome),
        })
        api_call("sendMessage", {
            "chat_id": user_id,
            "text": "✅ Você foi aprovado no White Vendas! Leia as regras e boas negociações.",
        })


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now():
    return int(time.time())


def seed_vip_code():
    """Garante que o codigo inicial existe (expira em 30 dias)."""
    codes = load_json(CODES_FILE, {})
    if VIP_SEED_CODE not in codes:
        codes[VIP_SEED_CODE] = {"expires": now() + 30 * 86400, "used": False}
        save_json(CODES_FILE, codes)
        print("Código VIP de demonstração ativo:", VIP_SEED_CODE)


def is_vip(user_id):
    vip = load_json(VIP_FILE, {})
    info = vip.get(str(user_id))
    return bool(info and info.get("expires", 0) >= now())


def redeem_code(user_id, code):
    """Resgata um codigo; devolve (ok, mensagem)."""
    code = code.strip().upper()
    codes = load_json(CODES_FILE, {})
    info = codes.get(code)
    if not info:
        return False, "❌ Código inválido."
    if info.get("used"):
        return False, "❌ Código já utilizado."
    if info.get("expires", 0) < now():
        return False, "❌ Código expirado."
    codes[code]["used"] = True
    save_json(CODES_FILE, codes)
    vip = load_json(VIP_FILE, {})
    vip[str(user_id)] = {"expires": info["expires"]}
    save_json(VIP_FILE, vip)
    return True, "✅ VIP ativado com sucesso! Use /vip para ver as ferramentas."


def generate_code(days):
    """Gera um codigo novo (apenas dono do bot)."""
    code = secrets.token_hex(4).upper()
    codes = load_json(CODES_FILE, {})
    codes[code] = {"expires": now() + int(days) * 86400, "used": False}
    save_json(CODES_FILE, codes)
    return code


def api_call(method, params=None):
    """Faz uma chamada a API do Telegram e devolve o JSON da resposta."""
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(
        API + "/" + method,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=70) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "ignore")
        return json.loads(body) if body else {"ok": False, "description": str(err)}
    except urllib.error.URLError:
        return {"ok": False, "description": "sem conexao com o Telegram"}


def send_message(chat_id, text):
    api_call("sendMessage", {"chat_id": chat_id, "text": text})


def is_admin(chat_id, user_id):
    """Verifica se o usuario e dono/administrador do grupo."""
    result = api_call("getChatMember", {"chat_id": chat_id, "user_id": user_id})
    return result.get("ok") and result.get("result", {}).get("status") in ADMIN_STATUS


def create_topic(chat_id, name, icon_emoji=None):
    """Cria um topico no grupo (exige Topicos ativos e bot admin)."""
    params = {"chat_id": chat_id, "name": name}
    if icon_emoji:
        params["icon_custom_emoji_id"] = icon_emoji
    return api_call("createForumTopic", params)


def handle_command(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "").strip()

    if not text:
        return

    cmd = text.split(" ", 1)[0].lower().split("@")[0]
    args = text.split(" ", 1)[1].strip() if " " in text else ""

    if cmd in ("/start", "/help"):
        send_message(
            chat_id,
            "👋 Eu crio tópicos em grupos e tenho Área VIP!\n\n"
            "Tópicos:\n"
            "• `/criartopico Nome` — cria tópico (só admins)\n\n"
            "Área VIP:\n"
            "• `/vip` — ver menu da área VIP\n"
            "• `/resgatar CÓDIGO` — ativar acesso com código\n"
            "• `/gerarcodigo DIAS` — gerar código (apenas dono)\n\n"
            "Moderação:\n"
            "• `/remover` — responder msg p/ expulsar\n"
            "• `/desbloquear` — responder msg p/ liberar\n"
            "• Entradas aprovadas automaticamente; xingamentos removidos na hora",
        )
        return

    if cmd == "/vip":
        if is_vip(user_id):
            send_message(chat_id, VIP_MENU)
        else:
            send_message(
                chat_id,
                "🔒 Você ainda não tem acesso à Área VIP.\n\n"
                "Para entrar, use `/resgatar CÓDIGO` com um código válido.",
            )
        return

    if cmd == "/resgatar":
        if not args:
            send_message(chat_id, "ℹ️ Uso: /resgatar CÓDIGO")
            return
        ok, msg = redeem_code(user_id, args)
        send_message(chat_id, msg)
        return

    if cmd == "/gerarcodigo":
        if not OWNER_ID or user_id != OWNER_ID:
            send_message(
                chat_id,
                "⛔ Apenas o dono do bot pode gerar códigos. "
                "Defina OWNER_ID no script (seu ID via @userinfobot).",
            )
            return
        try:
            dias = int(args) if args else 30
        except ValueError:
            send_message(chat_id, "⚠️ Use: /gerarcodigo DIAS (ex.: 30)")
            return
        if not (1 <= dias <= 365):
            send_message(chat_id, "⚠️ DIAS deve estar entre 1 e 365.")
            return
        code = generate_code(dias)
        send_message(chat_id, "🎟️ Código gerado ({} dia(s)):\n`{}`".format(dias, code))
        return

    if cmd in ("/remover", "/desbloquear"):
        if user_id not in (OWNER_ID, ANON_ADMIN_ID) and not is_admin(chat_id, user_id):
            send_message(chat_id, "⛔ Só administradores podem usar isso.")
            return
        reply = message.get("reply_to_message")
        if not reply:
            send_message(chat_id, "ℹ️ Responda a mensagem da pessoa para {}.".format(
                "remover" if cmd == "/remover" else "desbloquear"))
            return
        alvo = reply["from"]["id"]
        if cmd == "/remover":
            ok = kick_user(chat_id, alvo)
            send_message(chat_id, "✅ Usuário removido do grupo." if ok else "❌ Não consegui remover.")
        else:
            ok = api_call("unbanChatMember", {"chat_id": chat_id, "user_id": alvo}).get("ok")
            send_message(chat_id, "✅ Usuário desbloqueado." if ok else "❌ Falha ao desbloquear.")
        return

    if cmd != "/criartopico":
        return

    tipo_chat = message.get("chat", {}).get("type", "")
    if tipo_chat == "private":
        send_message(chat_id, "ℹ️ Para criar tópico, envie o comando DENTRO do grupo onde o bot é admin (ex.: grupo White Vendas).")
        return

    if user_id not in (OWNER_ID, ANON_ADMIN_ID) and not is_admin(chat_id, user_id):
        print("Negado: chat={} tipo={} user={} owner={}".format(chat_id, tipo_chat, user_id, OWNER_ID), flush=True)
        send_message(chat_id, "⛔ Permissão negada: só administradores criam tópicos.")
        return

    raw = text.split(" ", 1)
    if len(raw) < 2 or not raw[1].strip():
        send_message(chat_id, "ℹ️ Uso: /criartopico Nome do tópico")
        return

    parts = [p.strip() for p in raw[1].split("|", 1)]
    name = parts[0]
    icon = parts[1] if len(parts) > 1 else None

    if not (1 <= len(name) <= 128):
        send_message(chat_id, "⚠️ O nome do tópico deve ter entre 1 e 128 caracteres.")
        return

    result = create_topic(chat_id, name, icon)
    if result.get("ok"):
        send_message(chat_id, "✅ Tópico criado: {}".format(name))
    else:
        desc = result.get("description", "erro desconhecido")
        send_message(
            chat_id,
            "❌ Não consegui criar o tópico.\n\n"
            "Verifique:\n"
            "• Tópicos ativados no grupo (Configurações → Tópicos)\n"
            "• Bot promovido a administrador\n\n"
            "Detalhe: {}".format(desc),
        )


def main():
    print("Bot iniciado. Aguardando comandos... (Ctrl+C para parar)")
    seed_vip_code()
    offset = 0
    while True:
        try:
            result = api_call(
                "getUpdates",
                {"offset": offset, "timeout": 30, "allowed_updates": ["message", "chat_join_request"]},
            )
            if not result.get("ok"):
                print("Erro no getUpdates:", result.get("description"))
                time.sleep(3)
                continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message")
                if message:
                    try:
                        handle_command(message)
                        moderar(message)
                    except Exception as exc:  # nunca derruba o loop
                        print("Erro ao processar:", exc)
                elif update.get("chat_join_request"):
                    try:
                        handle_join_request(update)
                    except Exception as exc:
                        print("Erro ao aprovar entrada:", exc)
        except KeyboardInterrupt:
            print("\nEncerrado.")
            break
        except Exception as exc:
            print("Erro geral:", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
