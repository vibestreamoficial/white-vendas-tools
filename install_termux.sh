#!/data/data/com.termux/files/usr/bin/bash
# Instala o kit no Termux (Android)
pkg update -y && pkg upgrade -y
pkg install -y python git nmap
pip install --upgrade pip
echo "OK! Use: python3 verifica_vendedor.py 11.222.333/0001-81"
