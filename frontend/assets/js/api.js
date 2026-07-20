// ========================================
// FastDelivery — API Client
// ========================================

// URL base da API — usa VITE_API_URL se definida (produção direta),
// ou string vazia (proxy Vite/Express resolve)
const API_BASE = import.meta.env.VITE_API_URL || "";

async function request(method, path, body = null, auth = false) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = localStorage.getItem("fastdelivery_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  try {
    const res = await fetch(`${API_BASE}${path}`, opts);
    const data = await res.json();

    if (!res.ok) {
      throw {
        status: res.status,
        message: data.detail || data.message || "Erro desconhecido",
        data,
      };
    }

    return data;
  } catch (err) {
    if (err.status) throw err;
    throw { status: 0, message: "Erro de conexão com o servidor", data: null };
  }
}

// ---- Auth ----
export const auth = {
  register(role, payload) {
    return request("POST", `/auth/register/${role}`, payload);
  },
  login(role, payload) {
    return request("POST", `/auth/login/${role}`, payload);
  },
  confirmEmail(token) {
    return request("POST", `/auth/confirm-email/${token}`);
  },
  forgotPassword(payload) {
    return request("POST", "/auth/forgot-password", payload);
  },
  resetPassword(token, payload) {
    return request("POST", `/auth/reset-password/${token}`, payload);
  },
  me(role) {
    return request("GET", `/auth/me/${role}`, null, true);
  },
};

// ---- Client ----
export const client = {
  // Produtos (vitrine)
  listProducts(merchantId) {
    const qs = merchantId ? `?merchant_id=${merchantId}` : "";
    return request("GET", `/client/products${qs}`, null, true);
  },
  getProduct(productId) {
    return request("GET", `/client/products/${productId}`, null, true);
  },

  // Carrinho
  getCart() {
    return request("GET", "/client/cart", null, true);
  },
  addToCart(payload) {
    return request("POST", "/client/cart", payload, true);
  },
  removeFromCart(productId) {
    return request("DELETE", `/client/cart/${productId}`, null, true);
  },

  // Pedidos
  createOrder() {
    return request("POST", "/client/ordem", null, true);
  },
  listOrders() {
    return request("GET", "/client/ordem/list", null, true);
  },
  getOrder(ordemId) {
    return request("GET", `/client/ordem/${ordemId}`, null, true);
  },

  // Pagamento
  getBalance() {
    return request("GET", "/client/balance", null, true);
  },
  payOrder(ordemId) {
    return request("POST", `/client/ordem/${ordemId}/pay`, null, true);
  },
  getComprovantes() {
    return request("GET", "/client/comprovantes", null, true);
  },
  recarregar(payload) {
    return request("POST", "/client/recarregar", payload, true);
  },
  getRecargas() {
    return request("GET", "/client/recargas", null, true);
  },

  // Perfil
  updateProfile(payload) {
    return request("PUT", "/client/profile", payload, true);
  },
};

// ---- Merchant ----
export const merchant = {
  // Dashboard
  getDashboard() {
    return request("GET", "/merchant/dashboard", null, true);
  },

  // Produtos
  listProducts() {
    return request("GET", "/merchant/products", null, true);
  },
  createProduct(payload) {
    return request("POST", "/merchant/products", payload, true);
  },
  updateProduct(productId, payload) {
    return request("PUT", `/merchant/products/${productId}`, payload, true);
  },
  deleteProduct(productId) {
    return request("DELETE", `/merchant/products/${productId}`, null, true);
  },

  // Pedidos
  listOrders() {
    return request("GET", "/merchant/ordem/list", null, true);
  },
  getOrder(ordemId) {
    return request("GET", `/merchant/ordem/${ordemId}`, null, true);
  },
  updateOrderStatus(ordemId, payload) {
    return request("PUT", `/merchant/ordem/${ordemId}/status`, payload, true);
  },

  // Financeiro
  getBalance() {
    return request("GET", "/merchant/balance", null, true);
  },
  getComprovantes() {
    return request("GET", "/merchant/comprovantes", null, true);
  },
  getTransferencias() {
    return request("GET", "/merchant/transferencias", null, true);
  },
};

// ---- Driver ----
export const driver = {
  getAvailableOrders() {
    return request("GET", "/driver/ordem/available", null, true);
  },
  acceptOrder(ordemId) {
    return request("POST", `/driver/ordem/${ordemId}/accept`, null, true);
  },
  markDelivered(ordemId) {
    return request("POST", `/driver/ordem/${ordemId}/delivered`, null, true);
  },
  getHistory() {
    return request("GET", "/driver/history", null, true);
  },
  updateLocation(payload) {
    return request("PUT", "/driver/location", payload, true);
  },
  getProfile() {
    return request("GET", "/driver/profile", null, true);
  },
};

// ---- Notifications ----
export const notifications = {
  list() {
    return request("GET", "/notifications", null, true);
  },
  clear() {
    return request("POST", "/notifications/clear", null, true);
  },
};
