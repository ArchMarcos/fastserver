# 🍕 FastDelivery

API de delivery com 3 papéis (cliente, lojista, entregador) construída com **FastAPI** + **PortunusDB**.

## Pré-requisitos

- Python 3.10+
- Rust (para compilar o PortunusDB)
- Acesso SMTP (opcional, para emails)

## Instalação

```bash
git clone <repo>
cd delivery_prototip

# Ambiente
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Config
cp .env.example .env
# Edite .env com suas credenciais (especialmente SMTP_USER/PASSWORD se quiser emails)

# Banco de dados
cd /tmp/portunus && cargo build --release   # compila PortunusDB (uma vez)
/tmp/portunus/target/release/portunusd --port 3100 &   # inicia o banco

cd /home/marcos/Documentos/delivery_prototip
python setup_db.py                         # cria banco + 16 tabelas

# Servidor
python -m uvicorn src.main:create_app --factory --host 0.0.0.0 --port 3101 --reload
```

## Estrutura

```
src/
├── apps/              # Lógica de negócio
│   ├── auth/          #   Registro, login, confirmação de email
│   ├── clients/       #   Carrinho, favoritos, pedidos, pagamentos, vitrine
│   ├── merchant/      #   Produtos, gestão de pedidos, finanças
│   ├── driver/        #   Entregas, localização, finanças
│   └── notifications/ #   Email (SMTP) e in-app
├── database/          # Conexão PortunusDB (16 tabelas)
├── globals/           # Modelos de dados
├── infra/             # Config, logging, exceções
├── middlewares/       # Guards de autenticação (JWT)
├── routes/            # Rotas da API (FastAPI routers)
├── schemas/           # Modelos Pydantic (request/response)
└── utils/             # bcrypt, JWT
```

---

## 🔐 Autenticação

Todas as rotas protegidas exigem `Authorization: Bearer <token>`.

### Papéis (roles)
| Role | Guard |
|---|---|
| `client` | `client_required` |
| `merchant` | `merchant_required` |
| `driver` | `driver_required` |
| qualquer autenticado | `auth_required` |

### Endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/auth/register/client` | — | Cadastro de cliente |
| `POST` | `/auth/register/merchant` | — | Cadastro de lojista |
| `POST` | `/auth/register/driver` | — | Cadastro de entregador |
| `POST` | `/auth/login/client` | — | Login cliente → JWT |
| `POST` | `/auth/login/merchant` | — | Login lojista → JWT |
| `POST` | `/auth/login/driver` | — | Login entregador → JWT |
| `POST` | `/auth/confirm-email/client` | — | Confirmar email |
| `POST` | `/auth/confirm-email/merchant` | — | Confirmar email |
| `POST` | `/auth/confirm-email/driver` | — | Confirmar email |
| `POST` | `/auth/resend-confirmation/{role}` | role | Reenviar email |
| `POST` | `/auth/logout/{role}` | role | Logout (blacklist) |
| `GET` | `/auth/me/{role}` | role | Perfil do usuário |

### Exemplo

```bash
# Registrar
curl -X POST http://localhost:3101/auth/register/client \
  -H "Content-Type: application/json" \
  -d '{"name":"João","email":"joao@test.com","phone":"11999999999","password":"123456","address":"Rua A, 123"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:3101/auth/login/client \
  -H "Content-Type: application/json" \
  -d '{"ident":"joao@test.com","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Confirmar email
EMAIL_TOKEN="..."  # recebido na resposta do registro
curl -X POST http://localhost:3101/auth/confirm-email/client \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$EMAIL_TOKEN\"}"

# Perfil
curl http://localhost:3101/auth/me/client -H "Authorization: Bearer $TOKEN"
```

---

## 🏪 Merchant

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/merchants/profile` | merchant | Perfil do lojista |
| `PATCH` | `/merchants/profile?field=&value=` | merchant | Atualizar campo |
| `POST` | `/merchants/toggle-open` | merchant | Abrir/fechar loja |
| `GET` | `/merchants/products` | merchant | Listar meus produtos |
| `POST` | `/merchants/products` | merchant | Criar produto |
| `PATCH` | `/merchants/products/{id}` | merchant | Atualizar produto |
| `DELETE` | `/merchants/products/{id}` | merchant | Remover produto |
| `PATCH` | `/merchants/products/{id}/toggle` | merchant | Ativar/desativar |
| `PATCH` | `/merchants/products/{id}/discount` | merchant | Aplicar desconto (%) |

### Exemplo

```bash
# Abrir loja
curl -X POST http://localhost:3101/merchants/toggle-open -H "Authorization: Bearer $MTOKEN"

# Criar produto
curl -X POST http://localhost:3101/merchants/products \
  -H "Authorization: Bearer $MTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pizza Margherita","description":"Clássica","images":[],"acompanhamentos":{"borda":5.0},"price":35.90,"categoria":"pizza"}'

# Listar produtos
curl http://localhost:3101/merchants/products -H "Authorization: Bearer $MTOKEN"

# Aplicar 15% de desconto
curl -X PATCH http://localhost:3101/merchants/products/1/discount \
  -H "Authorization: Bearer $MTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"discount":15.0}'
```

---

## 🛒 Cliente

### Carrinho
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/clients/cart` | client | Ver carrinho |
| `POST` | `/clients/cart/add` | client | Adicionar item |
| `POST` | `/clients/cart/remove` | client | Remover item |
| `PATCH` | `/clients/cart/qty` | client | Alterar quantidade |
| `PATCH` | `/clients/cart/obs` | client | Alterar observação |
| `POST` | `/clients/cart/clear` | client | Limpar carrinho |
| `GET` | `/clients/cart/totals` | client | Ver totais |

### Vitrine
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/clients/vitrine/categories` | client | Listar categorias |
| `GET` | `/clients/vitrine/search?query=` | client | Buscar produtos |
| `GET` | `/clients/vitrine/category/{cat}` | client | Por categoria |
| `GET` | `/clients/vitrine/merchant/{id}` | client | Por lojista |
| `GET` | `/clients/vitrine/open` | client | Lojas abertas |
| `GET` | `/clients/vitrine/product/{id}` | client | Detalhe do produto |

### Favoritos
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/clients/favorites` | client | Listar favoritos |
| `POST` | `/clients/favorites/{merchant_id}` | client | Adicionar |
| `DELETE` | `/clients/favorites/{merchant_id}` | client | Remover |

### Exemplo

```bash
# Adicionar ao carrinho
curl -X POST http://localhost:3101/clients/cart/add \
  -H "Authorization: Bearer $CTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"1","merchant_id":"1","quantidade":2,"acompanhamentos":{"borda":5.0}}'

# Ver carrinho com totais
curl http://localhost:3101/clients/cart -H "Authorization: Bearer $CTOKEN"

# Buscar por "pizza"
curl "http://localhost:3101/clients/vitrine/search?query=pizza" -H "Authorization: Bearer $CTOKEN"

# Adicionar favorito
curl -X POST http://localhost:3101/clients/favorites/1 -H "Authorization: Bearer $CTOKEN"
```

---

## 📦 Pedidos

### Cliente
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/ordens/create` | client | Criar a partir do carrinho |
| `GET` | `/ordens` | client | Listar todas |
| `GET` | `/ordens/active` | client | Ordens ativas |
| `GET` | `/ordens/history` | client | Histórico (entregue/cancelado) |
| `GET` | `/ordens/{id}` | auth | Ver ordem |
| `POST` | `/ordens/{id}/cancel` | client | Cancelar |
| `POST` | `/ordens/{id}/pay` | client | Pagar ordem |
| `POST` | `/ordens/{id}/rate` | client | Avaliar (1-5) |
| `POST` | `/ordens/recharge` | client | Recarregar saldo |
| `GET` | `/ordens/balance` | client | Ver saldo |
| `GET` | `/ordens/history/payments` | client | Histórico financeiro |
| `GET` | `/ordens/comprovantes` | client | Listar comprovantes |

### Exemplo

```bash
# Recarregar R$ 100
curl -X POST http://localhost:3101/ordens/recharge \
  -H "Authorization: Bearer $CTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value":100.0}'

# Criar pedido
curl -X POST http://localhost:3101/ordens/create \
  -H "Authorization: Bearer $CTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entregar_em":"Rua X, 123","payment_method":"saldo"}'

# Pagar
curl -X POST http://localhost:3101/ordens/1/pay -H "Authorization: Bearer $CTOKEN"

# Avaliar
curl -X POST http://localhost:3101/ordens/1/rate \
  -H "Authorization: Bearer $CTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"score":5,"comment":"Excelente!"}'
```

---

## 👨‍🍳 Merchant — Sub-ordens

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/ordens/merchant/pending` | merchant | Pendentes |
| `GET` | `/ordens/merchant/all` | merchant | Todas |
| `GET` | `/ordens/merchant/active` | merchant | Ativas |
| `GET` | `/ordens/merchant/history` | merchant | Histórico |
| `POST` | `/ordens/sub-ordens/{id}/accept` | merchant | Aceitar |
| `POST` | `/ordens/sub-ordens/{id}/refuse` | merchant | Recusar |
| `POST` | `/ordens/sub-ordens/{id}/start-preparing` | merchant | Iniciar preparo |
| `POST` | `/ordens/sub-ordens/{id}/mark-ready` | merchant | Pronto |
| `POST` | `/ordens/sub-ordens/{id}/waiting-driver` | merchant | Aguardando |
| `POST` | `/ordens/sub-ordens/{id}/collected` | merchant | Coletado |
| `GET` | `/ordens/merchant/earnings` | merchant | Ganhos |
| `GET` | `/ordens/merchant/balance` | merchant | Saldo |
| `GET` | `/ordens/merchant/liquid` | merchant | Líquido (taxas) |
| `POST` | `/ordens/merchant/saque` | merchant | Saque PIX |
| `GET` | `/ordens/merchant/comprovantes` | merchant | Comprovantes |

### Exemplo

```bash
# Ver pendentes
PEND=$(curl -s http://localhost:3101/ordens/merchant/pending -H "Authorization: Bearer $MTOKEN")
SUB_ID=$(echo "$PEND" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Aceitar → Preparar → Pronto → Aguardando entregador
for action in accept start-preparing mark-ready waiting-driver; do
  curl -X POST "http://localhost:3101/ordens/sub-ordens/$SUB_ID/$action" \
    -H "Authorization: Bearer $MTOKEN"
done

# Ver ganhos
curl http://localhost:3101/ordens/merchant/earnings -H "Authorization: Bearer $MTOKEN"

# Sacar
curl -X POST http://localhost:3101/ordens/merchant/saque -H "Authorization: Bearer $MTOKEN"
```

---

## 🏍️ Entregador

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/drivers/profile` | driver | Perfil |
| `POST` | `/drivers/online` | driver | Ficar online |
| `POST` | `/drivers/offline` | driver | Ficar offline |
| `POST` | `/drivers/location` | driver | Atualizar GPS |
| `GET` | `/drivers/location` | driver | Ver localização |
| `GET` | `/drivers/location/nearby?lat=&lng=&radius_km=` | driver | Motoristas próximos |
| `GET` | `/drivers/orders/available` | driver | Ordens disponíveis |
| `POST` | `/drivers/orders/{id}/accept` | driver | Aceitar |
| `POST` | `/drivers/orders/{id}/reject` | driver | Recusar |
| `POST` | `/drivers/orders/{id}/in-delivery` | driver | Saiu p/ entrega |
| `POST` | `/drivers/orders/{id}/delivered` | driver | Entregue |
| `GET` | `/drivers/orders/current` | driver | Ordem atual |
| `GET` | `/drivers/orders/history` | driver | Histórico |
| `GET` | `/drivers/earnings` | driver | Ganhos |
| `GET` | `/drivers/balance` | driver | Saldo |
| `POST` | `/drivers/saque` | driver | Saque PIX |

### Exemplo

```bash
# Ficar online + GPS
curl -X POST http://localhost:3101/drivers/online -H "Authorization: Bearer $DTOKEN"
curl -X POST http://localhost:3101/drivers/location \
  -H "Authorization: Bearer $DTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lat":-23.5505,"lng":-46.6333}'

# Ver ordens disponíveis
curl http://localhost:3101/drivers/orders/available -H "Authorization: Bearer $DTOKEN"

# Aceitar → Em entrega → Entregue
curl -X POST http://localhost:3101/drivers/orders/1/accept -H "Authorization: Bearer $DTOKEN"
curl -X POST http://localhost:3101/drivers/orders/1/in-delivery -H "Authorization: Bearer $DTOKEN"
curl -X POST http://localhost:3101/drivers/orders/1/delivered -H "Authorization: Bearer $DTOKEN"
```

---

## 🔔 Notificações

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/notifications` | auth | Listar in-app |
| `POST` | `/notifications/clear` | auth | Limpar todas |

### Exemplo

```bash
curl http://localhost:3101/notifications -H "Authorization: Bearer $CTOKEN"
curl -X POST http://localhost:3101/notifications/clear -H "Authorization: Bearer $CTOKEN"
```

---

## ⚙️ Configuração

Todas as variáveis em `.env`:

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_HOST` | `http://0.0.0.0:3100` | Servidor PortunusDB |
| `DATABASE_USER` | `root` | Usuário do banco |
| `DATABASE_PASSWORD` | — | Senha do banco |
| `JWT_SECRET_KEY` | — | Chave de assinatura JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo JWT |
| `SERVER_PORT` | `3101` | Porta da API |
| `DEBUG` | `false` | Modo debug (Swagger + reload) |
| `SMTP_HOST` | `smtp.gmail.com` | Servidor SMTP |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USER` | — | Email (vazio = modo simulação) |
| `SMTP_PASSWORD` | — | App Password (Gmail) |
| `PLATFORM_TAX` | `0.05` | Taxa da plataforma (5%) |
| `APP_URL` | `http://localhost:{port}` | URL base para links nos emails |

---

## 🧪 Testes rápidos

```bash
# Health check
curl http://localhost:3101/health

# Swagger (se DEBUG=true)
open http://localhost:3101/docs

# Testar envio de email
python test_email.py

# Visualizar todos os templates
python preview_emails.py
```
