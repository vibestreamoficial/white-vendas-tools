#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quiz educativo: voce reconhece phishing? Uso: python3 quiz_antiphishing.py"""

PERGUNTAS = [
    ("Um 'banco' envia email pedindo para clicar num link e digitar sua senha 'urgente'.", True,
     "Bancos NUNCA pedem senha por email ou link. Verifique sempre o remetente e o dominio."),
    ("Mensagem do 'suporte' do WhatsApp pede o codigo de 6 digitos que voce recebeu por SMS.", True,
     "Codigo de verificacao e pessoal e intransferivel. Quem pede esta tentando roubar sua conta."),
    ("Um amigo te envia um link curto para 'ver fotos' sem contexto.", True,
     "Links curtos escondem o destino. Confirme com o amigo por outro canal antes de clicar."),
    ("Promocao 'voce ganhou um Iphone' pedindo seu CPF e dados do cartao para 'liberar o premio'.", True,
     "Premio nao exige dados de cartao. Desconfie de brindes milagrosos."),
    ("Email do seu provedor avisa de cobranca real com numero de pedido e botao 'ver fatura'.", False,
     "Pode ser legitimo, mas confira o dominio do remetente e entre no site digitando o endereco."),
    ("Perfil falso de 'loja famosa' no Instagram responde seu comentario com link para pagamento fora do app.", True,
     "Compre sempre pelo app/site oficial. Pagamento fora do app e golpe."),
    ("Recebe PDF chamado 'fatura_2026.pdf' de remetente desconhecido e baixa direto.", True,
     "Arquivos de desconhecidos podem conter malware. Nunca abra sem confirmar a origem."),
    ("Mensagem do 'Pix' diz que voce recebeu um valor e pede para confirmar dados no link.", True,
     "Notificacoes reais de Pix ficam no app do banco. Nunca confirme dados por link."),
]

def main():
    acertos = 0
    for i, (texto, eh_golpe, explicacao) in enumerate(PERGUNTAS, 1):
        print("\nPERGUNTA {}/{}".format(i, len(PERGUNTAS)))
        print("Situacao:", texto)
        print("Isso e golpe (phishing)? [s/N] ", end="")
        resp = input().strip().lower()
        certo = (resp in ("s", "sim")) == eh_golpe
        if certo:
            acertos += 1
            print("✅ Correto!")
        else:
            print("❌ Errado.")
        print("Explicacao:", explicacao)
    print("\n=== RESULTADO: {}/{} acertos ===".format(acertos, len(PERGUNTAS)))
    if acertos == len(PERGUNTAS):
        print("Excelente! Voce sabe se proteger. 🛡️")
    elif acertos >= len(PERGUNTAS) // 2:
        print("Bom, mas revise as explicacoes acima.")
    else:
        print("Cuidado! Estude os sinais de phishing antes de negociar online.")

if __name__ == "__main__":
    main()
