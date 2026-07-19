# Models - esqueleto centralizado
# DB fornece: id, created_at, updated_at automaticamente


class UserBase:
    user_type: str  # client | merchant | driver
    avatar_url: str
    name: str
    email: str
    phone: str
    password: str
    px_key: str
    address: str
    balance: float = 0.0
    status: bool = True
    email_confirmed: bool = False
    notify: list[dict] = []  # max 10 notificações


class Client(UserBase):
    """Modelo do cliente."""
    cart: list[dict] = []
    ordem: list[str] = []
    favorites: list[str] = []  # IDs dos merchants favoritos
    addresses: list[dict] = []  # [{label, address, lat, lng}]
    active_ordem: str = ""


class Merchant(UserBase):
    """Modelo do merchant (lojista)."""
    products: list[str] = []
    ordens: list[str] = []
    is_open: bool = False
    taxa_delivery: float = 0.0
    categories: list[str] = []  # ex: ["lanche", "pizza"]
    logo_url: str = ""
    rating: float = 0.0
    opening_hours: str = ""  # ex: "18:00-23:00"
    delivery_time: int = 30  # tempo estimado em minutos


class Driver(UserBase):
    """Modelo do entregador."""
    veiculo: str = ""  # moto | bicycle | car
    current_ordem: str = ""  # ordem atual
    ordens_disponiveis: list[str] = []
    is_online: bool = False
    location: str = ""  # lat,lng


class Produto:
    """Modelo de produto."""
    merchant_id: str
    name: str
    description: str
    images_url: list[str] = []
    acompanhamentos: dict[str, float] = {}
    price: float = 0.0
    categoria: str = ""  # lanche | pizza | sushi | bebida | sobremesa
    is_active: bool = True
    discount: float = 0.0


class SubOrdem:
    """Sub-pedido de um merchant específico."""
    merchant_id: str
    product_id: str
    product_name: str  # snapshot do nome no momento da ordem
    quantidade: int = 1
    acompanhamentos: dict[str, float] = {}
    delivery_fee: float = 0.0
    total: float = 0.0
    platform_tax: float = 0.0
    status: str = "pendente"  # pendente | aceito | recusado | preparando | pronto | esperando_entregador | coletado | em_entrega | entregue
    obs: str = ""


class OrdemCart:
    """Pedido completo com um ou mais merchants."""
    client_id: str
    driver_id: str = ""
    merchant_ids: list[str] = []
    sub_ordens: list[SubOrdem] = []
    pegar_em: list[str] = []  # endereço de cada restaurante
    entregar_em: str = ""
    obs: str = ""
    payment_method: str = ""  # pix | saldo
    total_products: float = 0.0
    total_delivery_fee: float = 0.0
    total_platform_tax: float = 0.0
    driver_gain: float = 0.0
    total: float = 0.0
    status: str = "pendente"  # pendente | aceito | preparando | em_coleta | esperando_entregador | coletado | em_entrega | entregue | cancelado


class Transferencia:
    """Transferência entre contas."""
    ordem_id: str
    de: str
    para: str
    valor: float
    tipo: str  # ordem | saque | platform_tax
    status: str = "pendente"  # pendente | confirmada | falhou | estornada


class Recarga:
    """Recarga de saldo."""
    user_id: str
    valor: float
    metodo: str  # pix | cartao | boleto
    status: str = "pendente"  # pendente | confirmada | falhou


class Comprovante:
    """Comprovante de transação."""
    transferencia_id: str = ""
    recarga_id: str = ""
    tipo: str  # pagamento_ordem | recarga | saque | platform_tax
    de: str
    para: str
    valor: float
    descricao: str = ""


class Cupom:
    """Cupom de desconto."""
    code: str
    discount_percent: float = 0.0
    discount_value: float = 0.0
    merchant_id: str = ""  # vazio = cupom da plataforma
    max_uses: int = 0
    used_count: int = 0
    is_active: bool = True


class Avaliacao:
    """Avaliação de merchant, entregador ou produto."""
    user_id: str
    target_id: str  # ID do avaliado (merchant, driver, product)
    target_type: str  # merchant | driver | product
    ordem_id: str
    score: float  # 1-5
    comment: str = ""
