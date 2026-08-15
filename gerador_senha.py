#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de senhas seguras (educativo) — Termux/Linux.
Uso: python3 gerador_senha.py [tamanho] [quantidade]
Ex.: python3 gerador_senha.py 16 5
"""
import secrets
import string
import sys

SEM_AMBIGUOS = "il1Lo0O"


def gerar(tamanho=16, com_simbolos=True, sem_ambiguos=False):
    pool = string.ascii_letters + string.digits
    if com_simbolos:
        pool += "!@#$%&*+-_=?"
    if sem_ambiguos:
        pool = "".join(c for c in pool if c not in SEM_AMBIGUOS)
    # garante pelo menos 1 de cada classe quando possivel
    senha = []
    if com_simbolos:
        senha.append(secrets.choice(string.ascii_uppercase))
        senha.append(secrets.choice(string.ascii_lowercase))
        senha.append(secrets.choice(string.digits))
        senha.append(secrets.choice("!@#$%&*+-_=?"))
    while len(senha) < tamanho:
        senha.append(secrets.choice(pool))
    secrets.SystemRandom().shuffle(senha)
    return "".join(senha)


def main():
    try:
        tam = int(sys.argv[1]) if len(sys.argv) > 1 else 16
        qtd = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    except ValueError:
        print("Use numeros: python3 gerador_senha.py 16 5")
        sys.exit(1)
    tam = max(8, min(tam, 64))
    qtd = max(1, min(qtd, 20))
    print(f"🔐 {qtd} senha(s) segura(s) de {tam} caracteres:\n")
    for i in range(qtd):
        print(f"  {i + 1}. {gerar(tam)}")
    print("\n💡 Dica: guarde em cofre de senhas (ex.: Bitwarden/KeePass), nunca em texto puro.")


if __name__ == "__main__":
    main()
