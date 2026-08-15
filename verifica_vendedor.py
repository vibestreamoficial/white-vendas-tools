#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ferramenta de seguranca para vendas no grupo White Vendas.
Consulta dados publicos de CNPJ via BrasilAPI (gratuita) para ajudar
a verificar se a empresa/pessoa juridica com quem voce negocia existe
e esta ativa. Nao substitui investigacao oficial.

Uso no Termux:
  python3 verifica_vendedor.py 11.222.333/0001-81
"""

import json
import re
import sys
import urllib.request


def limpar(cnpj):
    return re.sub(r"[^0-9]", "", cnpj or "")


def consultar(cnpj):
    url = "https://brasilapi.com.br/api/cnpj/v1/{}".format(cnpj)
    req = urllib.request.Request(url, headers={"User-Agent": "white-vendas-tool/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 verifica_vendedor.py CNPJ")
        print("Ex.: python3 verifica_vendedor.py 11.222.333/0001-81")
        sys.exit(1)

    cnpj = limpar(sys.argv[1])
    if len(cnpj) != 14:
        print("CNPJ invalido: informe 14 digitos (com ou sem pontuacao).")
        sys.exit(1)

    print("Consultando CNPJ {} ...".format(cnpj))
    try:
        d = consultar(cnpj)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print("CNPJ nao encontrado na base publica.")
        else:
            print("Erro na consulta:", err.code, err.reason)
        sys.exit(1)
    except Exception as exc:
        print("Falha de conexao:", exc)
        sys.exit(1)

    print("\n================ RESULTADO ================")
    print("Razao social    :", d.get("razao_social"))
    print("Nome fantasia   :", d.get("nome_fantasia") or "-")
    print("Situacao        :", d.get("descricao_situacao_cadastral"))
    print("Abertura        :", d.get("data_inicio_atividade"))
    print("Porte           :", d.get("porte") or "-")
    print("Atividade       :", d.get("cnae_fiscal_descricao") or "-")
    end = d.get("logradouro") or "-"
    uf = d.get("uf") or ""
    print("Endereco        :", end, d.get("numero", ""), d.get("municipio", ""), uf)
    print("Telefone        :", d.get("ddd_telefone_1") or "-")
    print("Email           :", d.get("email") or "-")
    socios = d.get("socios") or []
    if socios:
        print("Socios:")
        for s in socios:
            print("  -", s.get("nome"), "|", s.get("qualificacao_socio_descricao"))

    situacao = (d.get("descricao_situacao_cadastral") or "").lower()
    print("\n================ AVALIACAO ================")
    notas = []
    notas.append("ATIVA" if "ativa" in situacao else "ATENCAO: situacao '{}'".format(situacao))
    abertura = d.get("data_inicio_atividade") or ""
    if abertura:
        ano = int(abertura[:4])
        idade = 2026 - ano
        notas.append("Empresa com {} ano(s) de registro".format(idade))
        notas.append("Empresa nova (<2 anos): verifique com mais cuidado" if idade < 2 else "Empresa registrada ha tempo: ponto positivo")
    print(" - " + "\n - ".join(notas))
    print("\nChecklist antes de negociar:")
    print(" 1. Confira se o nome/empresa bate com quem fala com voce.")
    print(" 2. Peça comprovante e confira a titularidade do Pix (o app mostra o nome).")
    print(" 3. Prefira pagamento com protecao (Mercado Pago, cartao, etc.).")
    print(" 4. Desconfie de preço muito abaixo do mercado.")
    print(" 5. Em golpe: prints + chamar admin do grupo e registrar BO.")


if __name__ == "__main__":
    main()
