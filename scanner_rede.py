#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner de rede EDUCACIONAL (use apenas em redes suas ou com autorizacao).
Varre portas de um host. Base para estudos de seguranca.
Uso: python3 scanner_rede.py 192.168.0.1 22,80,443,3389
"""

import socket
import sys


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scanner_rede.py HOST PORTA,PORTA,...")
        print("Ex.: python3 scanner_rede.py 192.168.0.1 22,80,443")
        sys.exit(1)
    host = sys.argv[1]
    portas = [int(p) for p in sys.argv[2].split(",") if p.strip()]
    print("Escaneando {} nas portas {} ...".format(host, portas))
    for porta in portas:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        try:
            if s.connect_ex((host, porta)) == 0:
                print("  {}:{} -> ABERTA".format(host, porta))
        finally:
            s.close()
    print("Concluido. Lembrete: use apenas em redes suas ou com autorizacao.")


if __name__ == "__main__":
    main()
