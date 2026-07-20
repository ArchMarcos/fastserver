# Envio de e-mails — SMTP real com templates HTML (identidade: azul bebê + branco)
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from loguru import logger
from src.infra.config import settings

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_FROM = settings.SMTP_FROM

# ── Identidade visual ──
AZUL = "#7CB9E8"          # azul bebê principal
AZUL_ESCURO = "#3A8BBF"   # hover / destaque
FUNDO = "#F5FAFD"          # fundo levemente azulado
BRANCO = "#FFFFFF"
CINZA = "#8899A6"
TEXTO = "#2C3E50"

APP_URL = getattr(settings, "APP_URL", f"http://localhost:{settings.SERVER_PORT}")


# ── Base ──

def _wrap(title: str, content: str, preheader: str = "") -> str:
    """Envolve o conteúdo num layout comum com header e footer."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{FUNDO};font-family:'Segoe UI',Helvetica,Arial,sans-serif">
<!--[if mso]><style>.btn {{ mso-hide:all; }}</style><![endif]-->
{"<div style='display:none;max-height:0;overflow:hidden'>" + preheader + "</div>" if preheader else ""}

<table width="100%" cellpadding="0" cellspacing="0" style="background:{FUNDO};padding:40px 0">
<tr><td align="center">

  <!-- Card principal -->
  <table width="560" cellpadding="0" cellspacing="0" style="background:{BRANCO};border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06)">

    <!-- Header azul -->
    <tr>
      <td style="background:{AZUL};padding:32px 40px 24px;text-align:center">
        <div style="font-size:22px;font-weight:700;color:{BRANCO};letter-spacing:-0.3px">🍕 {settings.PLATFORM_NAME}</div>
      </td>
    </tr>

    <!-- Título -->
    <tr>
      <td style="padding:30px 40px 10px;text-align:center">
        <h1 style="margin:0;font-size:20px;font-weight:600;color:{TEXTO};line-height:1.4">{title}</h1>
      </td>
    </tr>

    <!-- Conteúdo -->
    <tr>
      <td style="padding:16px 40px 32px;color:{TEXTO};font-size:15px;line-height:1.7">
        {content}
      </td>
    </tr>

    <!-- Divisor -->
    <tr><td style="padding:0 40px"><div style="border-top:1px solid #E8EDF1"></div></td></tr>

    <!-- Footer -->
    <tr>
      <td style="padding:20px 40px 28px;text-align:center;color:{CINZA};font-size:12px;line-height:1.6">
        {settings.PLATFORM_NAME} &copy; 2026<br>
        <span style="color:#BCC5CB">Este é um email automático. Não responda.</span>
      </td>
    </tr>

  </table>

</td></tr>
</table>
</body>
</html>"""


def _btn(text: str, url: str) -> str:
    return (
        f'<a href="{url}" style="display:inline-block;padding:14px 36px;'
        f'background:{AZUL};color:{BRANCO};text-decoration:none;'
        f'border-radius:8px;font-size:15px;font-weight:600;'
        f'margin:8px 0;text-align:center;border:2px solid {AZUL}">'
        f'{text}</a>'
    )


def _tag(label: str, value: str) -> str:
    return f'<div style="margin-bottom:8px"><span style="color:{CINZA};font-size:13px">{label}</span><br><span style="font-weight:600">{value}</span></div>'


def _status_badge(text: str, color: str = AZUL) -> str:
    return f'<span style="display:inline-block;padding:6px 16px;background:{color};color:{BRANCO};border-radius:20px;font-size:14px;font-weight:600">{text}</span>'


# ── Templates ──

def send_email(to, subject, body, html=True):
    """Envia email via SMTP. Retorna True/False, nunca lança exceção."""
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.info("[email simulado] para={to} assunto={subj}", to=to, subj=subject)
        return True

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = f"[{settings.PLATFORM_NAME}] {subject}"
    sub = "html" if html else "plain"
    msg.attach(MIMEText(body, sub))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.sendmail(SMTP_FROM, to, msg.as_string())
        logger.info("email enviado para {to}: {subj}", to=to, subj=subject)
        return True
    except Exception as e:
        logger.error("falha ao enviar email para {to}: {err}", to=to, err=e)
        return False


def send_confirmation(email, name, token):
    link = f"{APP_URL}/auth/confirm-email?token={token}"
    content = (
        f'<p style="margin-top:0">Olá <strong>{name}</strong>,</p>'
        f"<p>Seja bem-vindo(a) ao <strong>{settings.PLATFORM_NAME}</strong>! "
        f"Clique no botão abaixo para confirmar seu e-mail e começar a usar.</p>"
        f'<div style="text-align:center;margin:24px 0">{_btn("Confirmar E-mail", link)}</div>'
        f'<p style="color:{CINZA};font-size:13px">Ou cole este link no navegador:<br><a href="{link}" style="color:{AZUL_ESCURO}">{link}</a></p>'
    )
    body = _wrap(f"Confirme seu e-mail, {name} 👋", content, "Confirme seu e-mail para ativar sua conta")
    send_email(email, f"Confirme seu e-mail", body)


def send_welcome(email, name):
    link = f"{APP_URL}"
    content = (
        f'<p style="margin-top:0">Olá <strong>{name}</strong>,</p>'
        f'<div style="text-align:center;margin:12px 0">{_status_badge("✨ Conta Confirmada")}</div>'
        f"<p>Sua conta no <strong>{settings.PLATFORM_NAME}</strong> está ativa. "
        f"Agora você já pode explorar restaurantes, montar seu pedido e aproveitar!</p>"
        f'<div style="text-align:center;margin:20px 0">{_btn("Começar a pedir", link)}</div>'
    )
    body = _wrap("Conta confirmada! 🎉", content)
    send_email(email, "Conta confirmada — aproveite!", body)


def send_reset_password(email, token):
    link = f"{APP_URL}/reset?token={token}"
    content = (
        f'<p style="margin-top:0">Olá,</p>'
        f"<p>Recebemos uma solicitação para redefinir sua senha. "
        f"Se foi você, clique no botão abaixo:</p>"
        f'<div style="text-align:center;margin:24px 0">{_btn("Redefinir Senha", link)}</div>'
        f'<p style="color:{CINZA};font-size:13px">Se você <strong>não</strong> solicitou, ignore este email. Sua senha continua segura.</p>'
    )
    body = _wrap("Redefinição de senha 🔐", content)
    send_email(email, "Redefinição de senha", body)


def send_receipt(email, name, comprovante):
    valor = float(comprovante.get("valor", 0))
    tipo = comprovante.get("tipo", "pagamento")
    desc = comprovante.get("descricao", "")
    tid = comprovante.get("transferencia_id", "")

    tipo_label = {
        "pagamento_ordem": "Pagamento do Pedido",
        "recarga": "Recarga de Saldo",
        "saque": "Saque via PIX",
        "platform_tax": "Taxa da Plataforma",
    }.get(tipo, tipo)

    content = (
        f'<p style="margin-top:0">Olá <strong>{name}</strong>,</p>'
        f'<p>Segue o comprovante da sua transação.</p>'

        # Mini card do comprovante
        f'<div style="background:{FUNDO};border-radius:10px;padding:20px 24px;margin:16px 0">'
        f"{_tag('Tipo', tipo_label)}"
        f"{_tag('Valor', f'R$ {valor:.2f}')}"
        f"{_tag('Descrição', desc) if desc else ''}"
        f"{_tag('ID', tid) if tid else ''}"
        f"</div>"

        f'<p style="color:{CINZA};font-size:13px">Qualquer dúvida, entre em contato com nosso suporte.</p>'
    )
    body = _wrap("Comprovante de transação 🧾", content)
    send_email(email, "Comprovante", body)


def send_status_update(email, name, order_id, new_status):
    stages = [
        ("aceito", "✅", "Confirmado"),
        ("preparando", "👨‍🍳", "Em preparo"),
        ("pronto", "📦", "Pronto"),
        ("esperando_entregador", "🏍️", "Aguardando"),
        ("coletado", "🛵", "A caminho"),
        ("em_entrega", "🚀", "Saiu para entrega"),
        ("entregue", "🎉", "Entregue!"),
        ("cancelado", "❌", "Cancelado"),
    ]

    current_index = 0
    current_emoji = ""
    current_label = new_status
    for i, (k, emoji, label) in enumerate(stages):
        if k == new_status:
            current_index = i
            current_emoji = emoji
            current_label = label
            break

    # Barra de progresso
    dots = ""
    for i, (_, emoji, label) in enumerate(stages):
        active = i == current_index
        past = i < current_index
        opacity = "1" if active or past else "0.35"
        bg = AZUL if active else ("transparent" if past else "transparent")
        color = AZUL if active or past else CINZA
        border = f"2px solid {AZUL}" if active else ("2px solid #D5E5F0" if past else "2px solid #E0E6EB")
        scale = "scale(1.15)" if active else "scale(1)"
        dots += (
            f'<div style="display:inline-block;width:40px;height:40px;border-radius:50%;'
            f'background:{bg};color:{color};border:{border};text-align:center;'
            f'line-height:38px;margin:0 4px;font-size:18px;transform:{scale}">{emoji}</div>'
        )

    content = (
        f'<p style="margin-top:0">Olá <strong>{name}</strong>,</p>'
        f'<p>O status do seu pedido <strong>#{order_id}</strong> foi atualizado:</p>'

        f'<div style="text-align:center;margin:20px 0">{_status_badge(f"{current_emoji}  {current_label}", AZUL)}</div>'

        f'<div style="text-align:center;margin:24px 0 8px">{dots}</div>'

        f'<p style="color:{CINZA};font-size:12px;text-align:center;margin-top:4px">'
        + "  →  ".join(label for _, _, label in stages)
        + "</p>"

        f'<div style="text-align:center;margin:24px 0 4px">{_btn("Ver pedido", APP_URL + "/orders/" + order_id)}</div>'
    )
    body = _wrap(f"Pedido #{order_id} — {current_label} {current_emoji}", content, f"Status do pedido: {current_label}")
    send_email(email, f"Pedido #{order_id} — {current_label}", body)
