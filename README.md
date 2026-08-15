# White Vendas Tools 🛒🛡️

Kit de ferramentas legítimas do grupo White Vendas — para vender com segurança e estudar cyber segurança (white hat).

## Ferramentas
| Arquivo | O que faz |
|---|---|
| `verifica_vendedor.py` | Consulta CNPJ em dados públicos (BrasilAPI): situação, tempo de registro, sócios |
| `gerador_anuncio.py` | Gera anúncio formatado para o grupo |
| `calculadora_lucro.py` | Calcula lucro, margem e preço mínimo |
| `planilha_vendas.py` | Controla vendas em CSV (faturamento/lucro) |
| `scanner_rede.py` | Scanner de portas EDUCACIONAL (redes suas ou autorizadas) |
| `senha_check.py` | Checa a força de uma senha |
| `telegram_topics_bot.py` | Bot do grupo (tópicos, VIP, moderação) — configure `BOT_TOKEN` |

| `lab_virtual.sh` | Monta laboratório virtual (KVM/VirtualBox) para treinar Kali Linux |
| `quiz_antiphishing.py` | Quiz educativo para reconhecer golpes de phishing |
| `check_link.py` | Analisa links e avisa sinais de golpe |
| `relatorio_denuncia.py` | Gera relatório de denúncia para BO/SaferNet |

## Instalação
**Termux (Android):**
```bash
bash install_termux.sh
```
**Kali/Linux:**
```bash
bash install_kali.sh
```

## Exemplos
```bash
python3 verifica_vendedor.py 11.222.333/0001-81
python3 gerador_anuncio.py "Iphone 12" 1500 "Sao Paulo/SP" usado "64GB"
python3 calculadora_lucro.py 150 80 15 5
python3 planilha_vendas.py relatorio
python3 scanner_rede.py 192.168.0.1 22,80,443
python3 senha_check.py 'MinhaSenha123!'
```

## Bot
```bash
export BOT_TOKEN="token_do_seu_bot"
python3 telegram_topics_bot.py
```
Comandos: `/criartopico`, `/vip`, `/resgatar`, `/gerarcodigo`, `/remover`, `/desbloquear`.

## Regras
Conteúdo white hat apenas. Nada de phishing, RATs ou acesso a contas de terceiros.


## Laboratório virtual
```bash
bash lab_virtual.sh
```
Depois: baixe o Kali Linux (kali.org) e uma VM vulnerável de treino (ex.: Metasploitable 2) e estude na sua própria rede.

## Anti-phishing
```bash
python3 quiz_antiphishing.py
```


## Links suspeitos
```bash
python3 check_link.py 'https://link-suspeito.com/premio'
```

## Denúncia
```bash
python3 relatorio_denuncia.py
```
Gera `relatorio_denuncia.md` com as evidências, para você encaminhar à plataforma, SaferNet ou delegacia. Veja também `guia_golpes.md` e `checklist_seguranca.md`.
