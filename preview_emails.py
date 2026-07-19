#!/usr/bin/env python3
"""Envia os 5 templates redesenhados para visualização."""
import sys
sys.path.insert(0, ".")

from src.infra.config import settings
from src.apps.notifications.email import (
    send_confirmation,
    send_welcome,
    send_receipt,
    send_status_update,
    send_reset_password,
)

TO = settings.SMTP_USER
NAME = TO.split("@")[0]

print("🎨 Enviando 5 templates com identidade azul bebê + branco")
print(f"📧 Para: {TO}")
print()

send_confirmation(TO, NAME, "eyJhbGciOiJIUzI1NiJ9.demo_payload_token")
print("  ✅ 1/5 - Confirmação de email (header azul + botão)")

send_welcome(TO, NAME)
print("  ✅ 2/5 - Boas-vindas (badge + CTA)")

send_receipt(TO, NAME, {
    "tipo": "pagamento_ordem",
    "valor": 89.90,
    "descricao": "Pedido #42 — Pizza Margherita + Coca-Cola",
    "transferencia_id": "42",
})
print("  ✅ 3/5 - Comprovante (card com detalhes)")

send_status_update(TO, NAME, "42", "entregue")
print("  ✅ 4/5 - Status do pedido (barra de progresso visual)")

send_reset_password(TO, "r3s3t_t0k3n_d3m0")
print("  ✅ 5/5 - Redefinição de senha")

print()
print("📬 Confira sua caixa de entrada!")
