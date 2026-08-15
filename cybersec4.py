#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyber Segurança 4.0 — kit de treino white hat.
Menu interativo: python3 cybersec4.py
Modulos diretos: python3 cybersec4.py <modulo> [args]
"""

import hashlib
import os
import secrets
import string
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))


def rodar(nome, *args):
    """Executa um dos scripts do kit."""
    subprocess.run([sys.executable, os.path.join(DIR, nome)] + list(args))


# ---------- modulos novos ----------

def gerar_senha(comprimento=16):
    chars = string.ascii_letters + string.digits + "!@#$%&*-_"
    return "".join(secrets.choice(chars) for _ in range(comprimento))


def hash_arquivo(caminho):
    if not os.path.exists(caminho):
        print("Arquivo nao encontrado:", caminho)
        return
    dados = open(caminho, "rb").read()
    print("MD5    :", hashlib.md5(dados).hexdigest())
    print("SHA1   :", hashlib.sha1(dados).hexdigest())
    print("SHA256 :", hashlib.sha256(dados).hexdigest())
    print("Tamanho:", len(dados), "bytes")


def cifra_cesar(texto, deslocamento):
    """Cifra educativa (somente letras). Uso para estudar criptografia classica."""
    res = []
    for ch in texto:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            res.append(chr((ord(ch) - base + deslocamento) % 26 + base))
        else:
            res.append(ch)
    return "".join(res)


QUIZ_FUNDAMENTOS = [
    ("O que e phishing?", ["Virus que apaga arquivos", "Engenharia social para roubar dados", "Tipo de firewall", "Um antivirus"], 1,
     "Phishing e enganar a vitima (email/link falso) para roubar dados."),
    ("Qual a melhor defesa contra acesso indevido a contas?", ["Senha igual em tudo", "2FA (verificacao em duas etapas)", "Nao usar internet", "Divulgar a senha"], 1,
     "2FA protege a conta mesmo se a senha vazar."),
    ("O que significa HTTPS?", ["Conexao criptografada", "Site rapido", "Rede social", "Antivirus"], 0,
     "HTTPS criptografa os dados entre seu navegador e o site."),
    ("Recebeu email urgente pedindo senha. O que fazer?", ["Clicar rapido", "Responder com a senha", "Nao clicar e denunciar como phishing", "Encaminhar para amigos"], 2,
     "Nunca informe senha. Denuncie e apague."),
    ("O que e um RAT?", ["Ferramenta de acesso remoto usada por criminosos", "Tipo de rede", "Antivirus", "Navegador"], 0,
     "RAT (Remote Access Trojan) permite controle remoto indevido — e crime."),
    ("Qual pratica e segura?", ["Usar senha do banco em sites de jogo", "Anotar senha em post-it", "Usar gerenciador de senhas", "Compartilhar senha com amigos"], 2,
     "Gerenciadores de senha criam e guardam senhas fortes."),
]

QUIZ_FUND_OPCOES = "abcd"


def quiz_fundamentos():
    acertos = 0
    print("=== QUIZ FUNDAMENTOS DE SEGURANCA ===\n")
    for i, (perg, ops, certa, exp) in enumerate(QUIZ_FUNDAMENTOS, 1):
        print("P{}/{}: {}".format(i, len(QUIZ_FUNDAMENTOS), perg))
        for j, o in enumerate(ops):
            print("  {}) {}".format(QUIZ_FUND_OPCOES[j], o))
        resp = input("Resposta (a-d): ").strip().lower()
        if resp == QUIZ_FUND_OPCOES[certa]:
            acertos += 1
            print("✅ Correto!")
        else:
            print("❌ Errado.")
        print("Explicacao:", exp, "\n")
    print("=== RESULTADO: {}/{} ===".format(acertos, len(QUIZ_FUNDAMENTOS)))


GUIA = """--- GUIA RAPIDO (Kali/Linux/Termux) ---
apt update && apt upgrade        # atualizar (Kali)
pkg update && pkg upgrade        # atualizar (Termux)
nmap -sn 192.168.0.0/24          # hosts ativos (rede SUA)
nmap -p 22,80,443 192.168.0.10   # portas (rede SUA)
ping -c 4 8.8.8.8                # testar conectividade
ifconfig / ip a                  # ver interfaces de rede
whois exemplo.com                # informacoes de dominio
curl -I https://site.com         # ver cabecalhos HTTP
python3 cybersec4.py             # este kit
Lembrete: somente redes suas ou com autorizacao."""


# ---------- menu ----------

MENU = [
    ("🎓 Quiz de fundamentos de segurança", quiz_fundamentos),
    ("🎣 Quiz anti-phishing", lambda: rodar("quiz_antiphishing.py")),
    ("🔑 Gerador de senha forte", lambda: print("Senha:", gerar_senha())),
    ("💪 Verificar força de senha", lambda: rodar("senha_check.py")),
    ("🔐 Hash de arquivo", lambda: rodar("cifra_helper.py", "hash")),
    ("🔡 Cifra de César (estudo)", lambda: rodar("cifra_helper.py", "cifra")),
    ("📡 Scanner de rede educacional", lambda: rodar("scanner_rede.py")),
    ("🔍 Analisar link suspeito", lambda: rodar("check_link.py")),
    ("🏢 Consultar CNPJ", lambda: rodar("verifica_vendedor.py")),
    ("🚨 Relatório de denúncia", lambda: rodar("relatorio_denuncia.py")),
    ("📖 Guia de comandos", lambda: print(GUIA)),
]


def menu():
    while True:
        print("\n" + "=" * 50)
        print("  CYBER SEGURANÇA 4.0 — KIT DE TREINO WHITE HAT")
        print("=" * 50)
        for i, (nome, _) in enumerate(MENU, 1):
            print("  {}) {}".format(i, nome))
        print("  0) Sair")
        op = input("\nEscolha: ").strip()
        if op == "0":
            break
        if op.isdigit() and 1 <= int(op) <= len(MENU):
            try:
                MENU[int(op) - 1][1]()
            except KeyboardInterrupt:
                print("\n(voltando ao menu)")
            except Exception as e:
                print("Erro:", e)
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "senha":
            print(gerar_senha(int(sys.argv[2]) if len(sys.argv) > 2 else 16))
        elif sys.argv[1] == "hash" and len(sys.argv) > 2:
            hash_arquivo(sys.argv[2])
        elif sys.argv[1] == "cifra" and len(sys.argv) > 2:
            print(cifra_cesar(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3))
        elif sys.argv[1] == "quiz":
            quiz_fundamentos()
        else:
            print("Modulos: senha [n], hash ARQUIVO, cifra TEXTO [n], quiz")
    else:
        menu()
