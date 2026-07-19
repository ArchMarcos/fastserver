# FastDelivery

Esqueleto de um app de delivery (cliente, lojista, entregador) construído com **Portunus SDK** + **FastAPI**.

## Estrutura

```
src/
├── apps/           # Lógica de negócio (auth, client, merchant, driver, notifications)
├── database/       # Conexão com o banco Portunus
├── globals/        # Modelos de dados centralizados
├── infra/          # Config, logging, erros
├── middlewares/     # Guards de autenticação
├── routes/         # Rotas da API (esqueleto)
└── main.py         # Entry point FastAPI
setup_db.py         # Script para criar banco + tabelas
```

## Uso

```bash
pip install -r requirements.txt
python setup_db.py        # cria banco e tabelas
python src/main.py         # inicia servidor
```

## Funcionalidades (esqueleto)

- **Clientes**: cadastro, carrinho, favoritos, vitrine, pedidos, pagamento
- **Lojistas**: produtos, gerenciamento de pedidos, finanças
- **Entregadores**: modo online, localização, aceitar/recusar pedidos
- **Notificações**: push e e-mail
- **Autenticação**: JWT com confirmação de e-mail
