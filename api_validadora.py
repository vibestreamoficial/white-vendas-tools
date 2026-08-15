#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API VALIDADORA (educacional/white) — valida e-mail, telefone e CPF.
Modo CLI:  python3 api_validadora.py --email ana@exemplo.com --telefone 11999999999 --cpf 123.456.789-09
Modo HTTP: python3 api_validadora.py --server 8000
   GET http://IP:8000/api/validar?email=...&telefone=...&cpf=...
"""
import json
import re
import smtplib
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
TEL_RE = re.compile(r"^(\+55)?(\d{10,11})$")


def valida_email(email):
    if not EMAIL_RE.match(email or ""):
        return {"valido": False, "motivo": "formato de e-mail invalido"}
    _, dominio = email.rsplit("@", 1)
    try:
        # descobre o MX do dominio (existe caixa de entrada?)
        registros = []
        try:
            import dns.resolver  # opcional: pip install dnspython
            registros = [str(r.exchange).rstrip(".") for r in dns.resolver.resolve(dominio, "MX")]
        except Exception:
            # fallback: resolve o proprio dominio como A
            socket.getaddrinfo(dominio, 25)
            registros = [dominio]
        if not registros:
            return {"valido": False, "motivo": "dominio sem MX (nao recebe e-mail)"}
        # teste SMTP leve (opcional, pode falhar sem rede completa)
        try:
            with smtplib.SMTP(registros[0], 25, timeout=8) as s:
                s.ehlo("white.local")
                s.mail("check@white.local")
                s.quit()
        except Exception:
            pass
        return {"valido": True, "dominio": dominio, "mx": registros[0]}
    except Exception as e:
        return {"valido": False, "motivo": "dominio nao resolveu: " + str(e)}


def valida_telefone(tel):
    m = TEL_RE.match(re.sub(r"[^0-9+]", "", tel or ""))
    if not m:
        return {"valido": False, "motivo": "formato invalido (use DDD + numero, ex.: 11999999999)"}
    numero = m.group(2)
    ddd = numero[:2]
    if not (11 <= int(ddd) <= 99):
        return {"valido": False, "motivo": "DDD invalido"}
    return {"valido": True, "ddd": ddd, "numero": numero}


def valida_cpf(cpf):
    n = re.sub(r"[^0-9]", "", cpf or "")
    if len(n) != 11 or n == n[0] * 11:
        return {"valido": False, "motivo": "CPF em formato invalido (checagem de digitos)"}
    for t in range(9, 11):
        soma = sum(int(n[i]) * ((t + 1) - i) for i in range(t))
        if int(n[t]) != (soma * 10 % 11) % 10:
            return {"valido": False, "motivo": "digito verificador invalido"}
    return {"valido": True, "formatado": "%s.%s.%s-%s" % (n[:3], n[3:6], n[6:9], n[9:])}


def validar_tudo(email="", telefone="", cpf=""):
    r = {}
    if email:
        r["email"] = valida_email(email)
    if telefone:
        r["telefone"] = valida_telefone(telefone)
    if cpf:
        r["cpf"] = valida_cpf(cpf)
    return r


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/api/validar":
            q = parse_qs(p.query)
            r = validar_tudo(q.get("email", [""])[0], q.get("telefone", [""])[0], q.get("cpf", [""])[0])
            body = json.dumps({"ok": True, "resultado": r}, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a):
        pass


def main():
    if "--server" in sys.argv:
        try:
            porta = int(sys.argv[sys.argv.index("--server") + 1])
        except (ValueError, IndexError):
            porta = 8000
        print("API Validadora rodando em http://0.0.0.0:{} (Ctrl+C para parar)".format(porta))
        ThreadingHTTPServer(("0.0.0.0", porta), Handler).serve_forever()
    args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    r = validar_tudo(args.get("--email", ""), args.get("--telefone", ""), args.get("--cpf", ""))
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
