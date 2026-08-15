#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analisa um link localmente e avisa sinais de golpe. Uso: python3 check_link.py 'URL'"""
import re
import sys

ENCONTRADORES = ["bit.ly", "t.ly", "tinyurl.com", "is.gd", "goo.gl", "cutt.ly", "shorturl.at", "rebrand.ly", "u.nu"]
PALAVRAS_SUSPEITAS = ["premio", "promocao", "ganhou", "urgente", "recuperar", "conta", "confirmar", "atualizar", "pix", "whatsapp", "voucher", "cupom"]

def analisar(url):
    avisos = []
    m = re.match(r"(https?)://([^/]+)(.*)", url.strip(), re.I)
    if not m:
        return ["⚠️ URL invalida ou sem protocolo (http/https)."], None
    proto, host, path = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
    if proto != "https":
        avisos.append("🔴 Sem HTTPS: conexao nao criptografada.")
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        avisos.append("🔴 O link aponta direto para um endereco de IP.")
    if any(e in host for e in ENCONTRADORES):
        avisos.append("🔴 Encurtador de link: destino escondido.")
    partes = host.split(".")
    if len(partes) > 3:
        avisos.append("🟠 Dominio com subdomínios demais — confira se e o site oficial.")
    if any(p in path for p in PALAVRAS_SUSPEITAS):
        avisos.append("🟠 Palavras de golpe no link (premio/urgente/confirmar...).")
    if "@" in host or "@" in path:
        avisos.append("🔴 URL com '@': o destino real e o que vem depois do @.")
    if not avisos:
        avisos.append("🟢 Nenhum sinal classico encontrado. Mesmo assim, confira o dominio digitando o site oficial no navegador.")
    return avisos, host

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 check_link.py 'https://exemplo.com/link'")
        sys.exit(1)
    avisos, host = analisar(sys.argv[1])
    print("Link analisado:", sys.argv[1])
    if host:
        print("Dominio:", host)
    print("\n".join(avisos))

if __name__ == "__main__":
    main()
