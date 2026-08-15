#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checa a forca de uma senha (educativo). Uso: python3 senha_check.py 'SuaSenha'"""
import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 senha_check.py 'sua-senha'")
        sys.exit(1)
    s = sys.argv[1]
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
    print("Forca da senha:", n.get(nota, "FRACA"))
    print("Dica: use 12+ caracteres, maiusculas, minusculas, numeros e simbolos.")


if __name__ == "__main__":
    main()
