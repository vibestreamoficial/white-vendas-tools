#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcula lucro e margem de uma venda.
Uso: python3 calculadora_lucro.py preco_venda custo_produto [frete] [comissao_%]
Ex.: python3 calculadora_lucro.py 150 80 15 5
"""

import sys


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 calculadora_lucro.py preco_venda custo [frete] [comissao_%]")
        print("Ex.: python3 calculadora_lucro.py 150 80 15 5")
        sys.exit(1)

    try:
        venda = float(sys.argv[1])
        custo = float(sys.argv[2])
        frete = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        comissao_pct = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    except ValueError:
        print("Valores invalidos. Use numeros (ponto para decimais).")
        sys.exit(1)

    comissao = venda * comissao_pct / 100
    despesas = custo + frete + comissao
    lucro = venda - despesas
    margem = (lucro / venda * 100) if venda else 0

    print("================ RESUMO ================")
    print("Preco de venda : R$ {:.2f}".format(venda))
    print("Custo produto  : R$ {:.2f}".format(custo))
    print("Frete          : R$ {:.2f}".format(frete))
    print("Comissao ({}%) : R$ {:.2f}".format(comissao_pct, comissao))
    print("----------------------------------------")
    print("Despesas totais: R$ {:.2f}".format(despesas))
    print("LUCRO          : R$ {:.2f}".format(lucro))
    print("MARGEM         : {:.1f}%".format(margem))
    if lucro < 0:
        print("\n⚠️  Prejuizo! Ajuste o preco de venda.")
    elif margem < 20:
        print("\n💡 Margem baixa: tente vender por pelo menos R$ {:.2f}".format(despesas * 1.2))


if __name__ == "__main__":
    main()
