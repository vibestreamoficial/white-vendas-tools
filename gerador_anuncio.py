#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um anuncio formatado pronto para colar no topico Anuncios do grupo.
Uso: python3 gerador_anuncio.py "Produto" 150 "Sao Paulo/SP" "usado" "Iphone 12 64GB, bateria 89%"
"""

import sys


def main():
    if len(sys.argv) < 5:
        print("Uso: python3 gerador_anuncio.py 'Produto' preco 'Cidade/UF' estado 'detalhes'")
        print('Ex.: python3 gerador_anuncio.py "Iphone 12" 1500 "Sao Paulo/SP" usado "64GB, bateria 89%"')
        sys.exit(1)

    produto, preco, cidade, estado = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    detalhes = sys.argv[5] if len(sys.argv) > 5 else ""

    anu = [
        "[VENDO] {} - R$ {} - {}".format(produto, preco, cidade),
        "",
        "• Produto: {}".format(produto),
        "• Condição: {}".format(estado),
    ]
    if detalhes:
        anu.append("• Detalhes: {}".format(detalhes))
    anu += [
        "• Preço: R$ {}".format(preco),
        "• Local: {}".format(cidade),
        "",
        "📸 Fotos reais nos comentários (obrigatório).",
        "💬 Negociação apenas pelo chat do grupo.",
        "✅ Confira minha reputação antes de fechar.",
        "🚫 Não pague adiantado para terceiros.",
    ]

    print("\n".join(anu))
    print("\n--- copie e cole no tópico Anúncios ---")


if __name__ == "__main__":
    main()
