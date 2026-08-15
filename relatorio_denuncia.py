#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um relatorio de denuncia organizado (para BO / SaferNet / suporte da plataforma).
Uso: python3 relatorio_denuncia.py
Isso NAO envia nada — apenas monta o documento com as evidencias que VOCE coletou.
"""

def pergunta(texto, obrigatorio=True):
    valor = input(texto + " ").strip()
    while obrigatorio and not valor:
        valor = input("Obrigatorio. " + texto + " ").strip()
    return valor

def main():
    print("=== GERADOR DE RELATORIO DE DENUNCIA ===\n")
    plataforma = pergunta("Plataforma (ex.: Kwai, Instagram, Telegram):")
    perfil = pergunta("Perfil/ID do conteudo suspeito:")
    links = []
    print("Links das evidencias (um por linha; linha vazia para terminar):")
    while True:
        l = input("> ").strip()
        if not l:
            break
        links.append(l)
    descricao = pergunta("Descricao do que foi encontrado:")
    data = pergunta("Data/hora aproximadas do fato (ex.: 12/08/2026 20h):", obrigatorio=False)

    linhas = [
        "RELATORIO DE DENUNCIA",
        "=" * 40,
        "Plataforma: " + plataforma,
        "Perfil/ID: " + perfil,
        "Data/hora: " + (data or "nao informado"),
        "",
        "DESCRICAO:",
        descricao,
        "",
        "EVIDENCIAS (links):",
    ]
    linhas += ["- " + l for l in links] or ["- (nenhum link informado)"]
    linhas += [
        "",
        "PRINTS/FOTOS: salve as imagens junto deste arquivo e nomeie com data/hora.",
        "",
        "ONDE ENCAMINHAR:",
        "- Plataforma: botao Denunciar no perfil/publicacao",
        "- SaferNet Brasil: https://new.safernet.org.br/denuncie",
        "- Delegacia Eletronica do seu estado (BO)",
        "- Policia Federal / 181 (disque denuncia)",
    ]
    texto = "\n".join(linhas)
    open("relatorio_denuncia.md", "w", encoding="utf-8").write(texto)
    print("\n✅ Relatorio salvo em relatorio_denuncia.md")
    print("Use junto com os prints. A denuncia efetiva e feita por voce, nos canais oficiais.")

if __name__ == "__main__":
    main()
