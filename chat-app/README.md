# 💬 White Chat — aplicativo completo (perfil, chat e lives)

App de chat com **perfil**, **conversas em tempo real** e **lives de vídeo**, com servidor próprio. Compatível com **Android 12, 13 e 14** (minSdk 31 / targetSdk 34).

## Estrutura
```
server/server.py   Servidor (Python, sem dependências): perfis, chat e sinalização de lives
web/index.html     Site completo (perfil + chat + live) — funciona no navegador
android/           App Android em Kotlin (compila no Android Studio)
```

## 1) Rodar o servidor
```bash
cd server
python3 server.py 8000
```
Abra `http://IP_DA_MAQUINA:8000` no navegador (PC, celular, Kali ou Termux).

## 2) Site (web)
- **Perfil**: crie username, nome e bio (salvos no servidor).
- **Chat**: salas em tempo real.
- **Live**: transmita sua câmera (WebRTC) ou assista. Funciona em Chrome/Edge/Firefox na mesma rede. Clique no navegador para liberar a câmera.

## 3) App Android
1. Abra a pasta `android/` no **Android Studio** (versão atual).
2. Em `Config.kt`, troque `SERVER` pelo IP da máquina que roda o `server.py` (mesma rede Wi-Fi).
3. Clique em **Build → Build APK(s)**. O APK sai em `app/build/outputs/apk/`.
4. Instale o APK no seu celular (Android 12+). Permissões de câmera/microfone são pedidas ao transmitir.

Telas do app: **Meu Perfil** (criar/listar), **Chat** (salas) e **Lives** (transmitir com câmera frontal ou assistir).

## 4) Lives — como funciona
- Sinalização via `POST /api/signal` + long-poll (`GET /api/signal?room=live:<canal>&after=N`).
- Mídia via **WebRTC** (STUN público): quem transmite envia oferta; quem assiste responde; candidatos ICE trocados pela sinalização.
- Limite realista: poucos espectadores por live (mesh). Para dezenas+ de espectadores seria preciso um SFU (ex.: mediasoup/Janus).

## API do servidor
| Método | Rota | Uso |
|---|---|---|
| POST | `/api/profile` | criar/atualizar perfil `{username, name, bio}` |
| GET | `/api/profile?username=` | buscar perfil |
| GET | `/api/profiles` | listar perfis |
| POST | `/send` | enviar mensagem `{room, user, text}` |
| GET | `/messages?room=&after=` | ler mensagens (long-poll 15s) |
| POST | `/api/signal` | sinalização de live `{room, from, type, payload}` |
| GET | `/api/signal?room=&after=` | ler sinais (long-poll 15s) |

## Segurança
- Código 100% aberto e auditável: servidor, site e app.
- Nenhum dado sai da sua rede; perfis ficam em `server/perfis.json`.
- Não instale APK recebido de chats — compile o seu.
