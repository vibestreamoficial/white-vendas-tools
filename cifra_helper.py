#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper dos modulos de hash e cifra do kit. Uso direto:
   python3 cifra_helper.py hash ARQUIVO
   python3 cifra_helper.py cifra TEXTO [deslocamento]
"""
import hashlib
import sys


def hash_arquivo(caminho):
    dados = open(caminho, "rb").read()
    print("MD5    :", hashlib.md5(dados).hexdigest())
    print("SHA1   :", hashlib.sha1(dados).hexdigest())
    print("SHA256 :", hashlib.sha256(dados).hexdigest())


def cifra_cesar(texto, d):
    res = []
    for ch in texto:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            res.append(chr((ord(ch) - base + d) % 26 + base))
        else:
            res.append(ch)
    return "".join(res)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: cifra_helper.py hash ARQUIVO | cifra_helper.py cifra TEXTO [n]")
    elif sys.argv[1] == "hash":
        hash_arquivo(sys.argv[2])
    elif sys.argv[1] == "cifra":
        print(cifra_cesar(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3))
