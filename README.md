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
| `cybersec4.py` | Cyber Segurança 4.0: menu com 11 ferramentas de treino |

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

---

## 💬 White Chat — TikTok Edition (`chat-app/`)

App social estilo TikTok: feed vertical de vídeos, lives, DMs, perfil e **painel admin** com moderação de posts.

### Rodar (2 passos)
```bash
cd chat-app/web
npm install
npm run build          # gera o app em web/dist
cd ../server
python3 server.py 8000 # serve o app + API em http://IP:8000
```

### Telas
- **App (usuário):** feed "Para Você" com scroll snap e curtir por duplo toque, Explorar (lives em grade 2 colunas + transmissão WebRTC), Chat (DMs com não-lidos), Perfil (avatar, contadores, editar/compartilhar) e botão `+` pra criar post (drag & drop, legenda, música, toggles).
- **Admin:** entre em `http://IP:8000/admin` (ou `/#/admin`) — login `admin` / `admin123`. Dashboard com gráfico, Usuários (banir/deletar), Posts (aprovar/reprovar/fixar/excluir — posts novos entram como **Pendente** e só aparecem no feed após aprovação), Lives, Denúncias e Config do servidor.

### APIs principais
`/api/posts` (feed + criação com fila de moderação), `/api/posts/<id>/approve|reject|pin|delete|like`, `/api/lives`, `/api/dm`, `/api/conversas`, `/api/reports`, `/api/admin/login`, `/api/users`, `/api/config`.

### App Android (Kotlin, Android 12-14)
Projeto em `chat-app/android/` — compile no Android Studio ou use o APK da Release `chat-app-v1.0` no GitHub. A URL do servidor é configurável dentro do app.

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


## Cyber Segurança 4.0 🧠
Kit de treino white hat com menu interativo:
```bash
python3 cybersec4.py
```
Módulos: quiz de fundamentos, quiz anti-phishing, gerador de senha forte, força de senha, hash de arquivo, cifra de César, scanner educacional, analisador de links, consulta de CNPJ, relatório de denúncia e guia de comandos.

Uso direto:
```bash
python3 cybersec4.py senha 16
python3 cybersec4.py cifra "OLAMUNDO" 3
python3 cifra_helper.py hash arquivo.py
python3 cybersec4.py quiz
```
