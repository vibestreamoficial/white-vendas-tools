# 💬 Chat White Vendas (site + app Android)

Chat em tempo real de código aberto: um **site (web)** que funciona em qualquer navegador e um **app Android (Kotlin)** que conversa com o mesmo servidor.

## Como rodar o site (servidor + web)
```bash
cd server
python3 server.py 8000
```
Abra `http://IP_DA_MAQUINA:8000` no navegador do celular/PC (mesma rede). Funciona no PC, Kali e Termux (sem instalar nada além do Python).

## App Android
1. Abra a pasta `android/` no Android Studio (versão atual).
2. No arquivo `MainActivity.kt`, troque `base` pelo IP da máquina do servidor.
3. Compile e instale (Build → Build APK(s)).
4. O APK gerado é SEU — não baixe APK de chats/grupos.

## Arquitetura
- `server/server.py` — servidor HTTP (stdlib): sala, envio e long-poll de mensagens.
- `web/index.html` — cliente de navegador.
- `android/` — app Kotlin (min SDK 26 / target 34 — Android 8+ até 14+).

## Limites
- Texto em tempo real (sem câmera/live por enquanto).
- Live de vídeo exigiria WebRTC + servidor de sinalização — arquitetura bem maior.
