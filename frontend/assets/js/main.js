// ========================================
// FastDelivery — JavaScript Principal
// ========================================

// Importa CSS para o Vite processar
import "../css/style.css";

// ---- Mobile menu togglle ----
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("menu-toggle");
  const mobileMenu = document.getElementById("mobile-menu");

  if (toggle && mobileMenu) {
    toggle.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
  }

  // ---- Auth state na navbar (landing page) ----
  const navGuest = document.getElementById("nav-guest");
  const navAuthed = document.getElementById("nav-authed");
  const mobileAuthed = document.getElementById("mobile-nav-authed");
  const user = getUser();

  if (user && navAuthed) {
    const roleLabels = { client: "Cliente", merchant: "Restaurante", driver: "Entregador" };
    const label = roleLabels[user.role] || "Usuário";
    const dashboards = { client: "/client/dashboard.html", merchant: "/merchant/dashboard.html", driver: "/driver/dashboard.html" };
    const dashboardUrl = dashboards[user.role] || "/auth/login.html";

    // Troca visibilidade
    if (navGuest) navGuest.classList.add("hidden");
    navAuthed.classList.remove("hidden");
    navAuthed.classList.add("flex");

    // Preenche saudação
    document.getElementById("nav-user-greeting").textContent = `${label}, ${user.name}`;
    document.getElementById("nav-dashboard-link").href = dashboardUrl;

    // Mobile
    if (mobileAuthed) {
      const mobileGreeting = document.getElementById("mobile-user-greeting");
      const mobileLink = document.getElementById("mobile-dashboard-link");
      if (mobileGreeting) mobileGreeting.textContent = `${label}, ${user.name}`;
      if (mobileLink) mobileLink.href = dashboardUrl;
      mobileAuthed.classList.remove("hidden");
    }

    // Botões de sair
    document.getElementById("nav-logout")?.addEventListener("click", logout);
    document.getElementById("mobile-logout")?.addEventListener("click", logout);
  }
});

// ---- Toast notification system ----
export function showToast(message, type = "info", duration = 4000) {
  // Remove toast anterior se existir
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = `toast toast--${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Força reflow para animar
  toast.offsetHeight;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ---- Load component HTML ----
export async function loadComponent(elementId, url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
    const html = await res.text();
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = html;
  } catch (err) {
    console.error(`[FastDelivery] Error loading component ${url}:`, err);
  }
}

// ---- Format helpers ----
export function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

export function formatDate(dateString) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateString));
}

// ---- Auth helpers ----
export function getToken() {
  return localStorage.getItem("fastdelivery_token");
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem("fastdelivery_user"));
  } catch {
    return null;
  }
}

export function getRole() {
  const user = getUser();
  return user?.role || null;
}

export function isAuthenticated() {
  return !!getToken();
}

export function logout() {
  localStorage.removeItem("fastdelivery_token");
  localStorage.removeItem("fastdelivery_user");
  window.location.href = "/auth/login.html";
}

// ---- Redirect if not authenticated ----
export function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "/auth/login.html";
    return false;
  }
  return true;
}

// ---- Redirect by role ----
export function redirectByRole() {
  const role = getRole();
  switch (role) {
    case "client":
      window.location.href = "/client/vitrine.html";
      break;
    case "merchant":
      window.location.href = "/merchant/dashboard.html";
      break;
    case "driver":
      window.location.href = "/driver/dashboard.html";
      break;
    default:
      window.location.href = "/auth/login.html";
  }
}
