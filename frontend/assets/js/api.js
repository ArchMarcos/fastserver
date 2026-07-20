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

// ---- Client (prefixo /clients) ----
export const client = {
  // Vitrine
  listOpenMerchants() {
    return request("GET", "/clients/vitrine/open", null, true);
  },
  getMerchantMenu(merchantId) {
    return request("GET", `/clients/vitrine/merchant/${merchantId}`, null, true);
  },
  searchProducts(query) {
    return request("GET", `/clients/vitrine/search?query=${encodeURIComponent(query)}`, null, true);
  },
  listCategories() {
    return request("GET", "/clients/vitrine/categories", null, true);
  },
  getProduct(productId) {
    return request("GET", `/clients/vitrine/product/${productId}`, null, true);
  },

  // Carrinho
  getCart() {
    return request("GET", "/clients/cart", null, true);
  },
  addToCart(payload) {
    return request("POST", "/clients/cart/add", payload, true);
  },
  removeFromCart(payload) {
    return request("POST", "/clients/cart/remove", payload, true);
  },
  updateCartQty(payload) {
    return request("PATCH", "/clients/cart/qty", payload, true);
  },
  updateCartObs(payload) {
    return request("PATCH", "/clients/cart/obs", payload, true);
  },
  clearCart() {
    return request("POST", "/clients/cart/clear", null, true);
  },
  cartTotals() {
    return request("GET", "/clients/cart/totals", null, true);
  },

  // Favoritos
  listFavorites() {
    return request("GET", "/clients/favorites", null, true);
  },
  addFavorite(merchantId) {
    return request("POST", `/clients/favorites/${merchantId}`, null, true);
  },
  removeFavorite(merchantId) {
    return request("DELETE", `/clients/favorites/${merchantId}`, null, true);
  },

  // Perfil
  getProfile() {
    return request("GET", "/clients/profile", null, true);
  },
  updateProfile(field, value) {
    return request("PATCH", `/clients/profile?field=${field}&value=${encodeURIComponent(value)}`, null, true);
  },
};

// ---- Orders (prefixo /ordens) ----
export const orders = {
  create(payload) {
    return request("POST", "/ordens/create", payload, true);
  },
  list() {
    return request("GET", "/ordens", null, true);
  },
  active() {
    return request("GET", "/ordens/active", null, true);
  },
  history() {
    return request("GET", "/ordens/history", null, true);
  },
  getById(id) {
    return request("GET", `/ordens/${id}`, null, true);
  },
  cancel(id) {
    return request("POST", `/ordens/${id}/cancel`, null, true);
  },
  pay(id) {
    return request("POST", `/ordens/${id}/pay`, null, true);
  },
  rate(id, payload) {
    return request("POST", `/ordens/${id}/rate`, payload, true);
  },

  // Carteira
  balance() {
    return request("GET", "/ordens/balance", null, true);
  },
  recharge(payload) {
    return request("POST", "/ordens/recharge", payload, true);
  },
  paymentHistory() {
    return request("GET", "/ordens/history/payments", null, true);
  },
  comprovantes() {
    return request("GET", "/ordens/comprovantes", null, true);
  },
};

// ---- Merchant (prefixo /merchants) ----
export const merchant = {
  getDashboard() {
    return request("GET", "/merchants/dashboard", null, true);
  },
  listProducts() {
    return request("GET", "/merchants/products", null, true);
  },
  createProduct(payload) {
    return request("POST", "/merchants/products", payload, true);
  },
  updateProduct(productId, payload) {
    return request("PUT", `/merchants/products/${productId}`, payload, true);
  },
  deleteProduct(productId) {
    return request("DELETE", `/merchants/products/${productId}`, null, true);
  },
  listOrders() {
    return request("GET", "/merchants/ordem/list", null, true);
  },
  getOrder(ordemId) {
    return request("GET", `/merchants/ordem/${ordemId}`, null, true);
  },
  updateOrderStatus(ordemId, payload) {
    return request("PUT", `/merchants/ordem/${ordemId}/status`, payload, true);
  },
  getBalance() {
    return request("GET", "/merchants/balance", null, true);
  },
  getComprovantes() {
    return request("GET", "/merchants/comprovantes", null, true);
  },
  getTransferencias() {
    return request("GET", "/merchants/transferencias", null, true);
  },
};

// ---- Driver (prefixo /drivers) ----
export const driver = {
  getAvailableOrders() {
    return request("GET", "/drivers/ordem/available", null, true);
  },
  acceptOrder(ordemId) {
    return request("POST", `/drivers/ordem/${ordemId}/accept`, null, true);
  },
  markDelivered(ordemId) {
    return request("POST", `/drivers/ordem/${ordemId}/delivered`, null, true);
  },
  getHistory() {
    return request("GET", "/drivers/history", null, true);
  },
  updateLocation(payload) {
    return request("PUT", "/drivers/location", payload, true);
  },
  getProfile() {
    return request("GET", "/drivers/profile", null, true);
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
