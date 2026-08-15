#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controla suas vendas em CSV (abre no Excel/Sheets).
Uso:
  python3 planilha_vendas.py nova                    -> cria vendas.csv
  python3 planilha_vendas.py add "Produto" 150 80 15 -> adiciona venda
  python3 planilha_vendas.py relatorio               -> mostra totais
"""

import csv
import os
import sys

ARQ = "vendas.csv"


def criar():
    with open(ARQ, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["produto", "preco_venda", "custo", "frete", "lucro"])
    print("{} criado.".format(ARQ))


def add(produto, venda, custo, frete):
    lucro = venda - custo - frete
    existe = os.path.exists(ARQ)
    with open(ARQ, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["produto", "preco_venda", "custo", "frete", "lucro"])
        w.writerow([produto, venda, custo, frete, round(lucro, 2)])
    print("Venda adicionada: {} | lucro R$ {:.2f}".format(produto, lucro))


def relatorio():
    if not os.path.exists(ARQ):
        print("Nenhuma venda ainda. Use: python3 planilha_vendas.py nova")
        return
    with open(ARQ, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    if not linhas:
        print("Planilha vazia.")
        return
    total_venda = sum(float(l["preco_venda"]) for l in linhas)
    total_lucro = sum(float(l["lucro"]) for l in linhas)
    print("Vendas registradas: {}".format(len(linhas)))
    print("Faturamento total : R$ {:.2f}".format(total_venda))
    print("Lucro total       : R$ {:.2f}".format(total_lucro))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "relatorio"
    if cmd == "nova":
        criar()
    elif cmd == "add" and len(sys.argv) >= 5:
        try:
            add(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]) if len(sys.argv) > 5 else 0)
        except ValueError:
            print("Valores invalidos.")
    elif cmd == "relatorio":
        relatorio()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
