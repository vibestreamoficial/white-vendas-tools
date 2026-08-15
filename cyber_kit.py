#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyber Kit — kit educacional white hat para Termux/Linux.
Menu: gerador de senha, verificador de link/phishing, forca de senha e guia dark web.

Uso: python3 cyber_kit.py
"""
import re
import secrets
import string
import sys

# ---------- gerador de senha ----------

def gerar_senha(tamanho=16, com_simbolos=True):
    pool = string.ascii_letters + string.digits
    if com_simbolos:
        pool += "!@#$%&*+-_=?"
    senha = [secrets.choice(string.ascii_uppercase),
             secrets.choice(string.ascii_lowercase),
             secrets.choice(string.digits)]
    if com_simbolos:
        senha.append(secrets.choice("!@#$%&*+-_=?"))
    while len(senha) < tamanho:
        senha.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(senha)
    return "".join(senha)

# ---------- verificador de link / phishing ----------

ENCONTRADORES = ["bit.ly", "t.ly", "tinyurl.com", "is.gd", "goo.gl", "cutt.ly", "shorturl.at", "rebrand.ly", "u.nu"]
PALAVRAS_SUSPEITAS = ["premio", "promocao", "ganhou", "urgente", "recuperar", "conta", "confirmar",
                      "atualizar", "pix", "whatsapp", "voucher", "cupom", "login", "verificar"]

def analisar_link(url):
    avisos = []
    m = re.match(r"(https?)://([^/]+)(.*)", url.strip(), re.I)
    if not m:
        return ["⚠️ URL invalida ou sem protocolo (http/https)."]
    proto, host, path = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
    if proto != "https":
        avisos.append("🔴 Sem HTTPS: conexao nao criptografada.")
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        avisos.append("🔴 Link aponta direto para um endereco de IP.")
    if any(e in host for e in ENCONTRADORES):
        avisos.append("🔴 Encurtador de link: destino escondido.")
    partes = host.split(".")
    if len(partes) > 3:
        avisos.append("🟠 Subdominios demais — confira se e o site oficial.")
    if any(p in path for p in PALAVRAS_SUSPEITAS):
        avisos.append("🟠 Palavras de golpe no link (premio/urgente/confirmar...).")
    if "@" in host or "@" in path:
        avisos.append("🔴 URL com '@': o destino real e o que vem depois do @.")
    if host.endswith(".tk") or host.endswith(".ml") or host.endswith(".ga") or host.endswith(".cf"):
        avisos.append("🟠 Dominio gratuito comum em golpes (TK/ML/GA/CF).")
    if not avisos:
        avisos.append("🟢 Nenhum sinal classico encontrado. Confira o dominio digitando o site oficial no navegador.")
    return avisos

# ---------- forca de senha ----------

def forca_senha(s):
    nota = 0
    if len(s) >= 8:
        nota += 1
    if len(s) >= 12:
        nota += 1
    if re.search(r"[a-z]", s):
        nota += 1
    if re.search(r"[A-Z]", s):
        nota += 1
    if re.search(r"[0-9]", s):
        nota += 1
    if re.search(r"[^a-zA-Z0-9]", s):
        nota += 1
    n = {1: "MUITO FRACA", 2: "FRACA", 3: "MEDIA", 4: "BOA", 5: "FORTE", 6: "MUITO FORTE"}
    return n.get(nota, "FRACA")

# ---------- guia dark web educacional ----------

DARK_GUIDE = """
🌐 GUIA DARK WEB — EDUCACIONAL

O que e?
- Deep web: paginas nao indexadas (intranets, areas de login).
- Dark web: parte da deep web acessivel so com anonimizacao (ex.: rede Tor).

E legal?
- SIM: navegar na rede Tor e legal. O Tor foi criado pelo Naval Research Lab dos EUA
  e hoje e mantido pelo Tor Project (organizacao sem fins lucrativos).
- CRIME: comprar/vender itens ilegais (drogas, armas, dados roubados), fraude,
  material de abuso infantil. Quem acessa isso responde criminalmente.

Como acessar com seguranca (educacional)?
- Instale o navegador Tor oficial: https://www.torproject.org
- No Termux: pkg install tor && tor
- Nao desative o NoScript, nao baixe arquivos, nao use credenciais pessoais.

Fontes oficiais e educativas (SEM mercados ilegais):
- https://www.torproject.org        -> projeto oficial do Tor
- https://ssd.eff.org               -> guia de defesa digital (EFF)
- https://www.eff.org               -> Electronic Frontier Foundation
- https://www.privacyguides.org     -> guias de privacidade
- https://www.owasp.org             -> seguranca de aplicacoes

⚠️ AVISO: este guia NAO fornece links para mercados ilegais. Isso e crime e nao ajudamos.
"""

# ---------- menu ----------

def main():
    while True:
        print("\n🧰 CYBER KIT — white hat (educativo)")
        print("1) 🔐 Gerar senha segura")
        print("2) 🔗 Verificar link / phishing")
        print("3) 💪 Forca da senha")
        print("4) 🌐 Guia dark web educacional")
        print("0) Sair")
        op = input("\nEscolha: ").strip()
        if op == "1":
            try:
                tam = int(input("Tamanho (8-64, padrao 16): ") or "16")
                qtd = int(input("Quantas (padrao 3): ") or "3")
            except ValueError:
                print("Use numeros.")
                continue
            print()
            for i in range(max(1, min(qtd, 20))):
                print(f"  {i + 1}. {gerar_senha(max(8, min(tam, 64)))}")
        elif op == "2":
            url = input("Cole a URL: ").strip()
            print("\n" + "\n".join(analisar_link(url)))
        elif op == "3":
            s = input("Digite a senha: ").strip()
            print("Forca:", forca_senha(s))
        elif op == "4":
            print(DARK_GUIDE)
        elif op == "0":
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nAte mais! 🛡️")
