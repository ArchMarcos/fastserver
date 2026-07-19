#!/usr/bin/env python3
"""Testa envio real de email usando as credenciais do .env."""
import sys
sys.path.insert(0, ".")

from src.infra.config import settings
from src.apps.notifications.email import send_email

SMTP_USER = settings.SMTP_USER
SMTP_FROM = settings.SMTP_FROM

if not SMTP_USER:
    print("❌ SMTP_USER não configurado no .env")
    sys.exit(1)

print(f"📧 Enviando email de teste...")
print(f"   Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
print(f"   De:   {SMTP_FROM}")
print(f"   Para: {SMTP_USER}")
print()

body = """
<h1>✅ FastDelivery — Email OK!</h1>
<p>Se você recebeu este email, as notificações estão <strong>funcionando</strong>.</p>
<hr>
<p style='color:gray;font-size:12px'>Enviado automaticamente pelo test_email.py</p>
"""

ok = send_email(to=SMTP_USER, subject="Teste de envio 🚀", body=body)

if ok:
    print(f"✅ Email enviado com sucesso! Verifique {SMTP_USER}")
else:
    print("❌ Falha ao enviar. Verifique:")

    # Re-testa com mais detalhes
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_USER
    msg["Subject"] = "[FastDelivery] Teste de envio"
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as s:
            s.set_debuglevel(1)  # mostra diálogo SMTP completo
            s.starttls(context=ssl.create_default_context())
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.sendmail(SMTP_FROM, SMTP_USER, msg.as_string())
            print("✅ Email enviado! (tentativa 2)")
    except Exception as e:
        print(f"❌ Erro detalhado: {e}")
