import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || process.env.EXPRESS_PORT || 3000;
const API_TARGET = process.env.VITE_API_URL || "http://0.0.0.0:3101";
const DIST = join(__dirname, "dist");

// ── Proxy: só encaminha chamadas de API (sem extensão de arquivo) ──
const apiProxy = createProxyMiddleware({
  target: API_TARGET,
  changeOrigin: true,
});

// Filtro: NÃO faz proxy se for arquivo estático ou rota de página
function apiOnly(pathname, req) {
  // Arquivos estáticos → não proxy
  if (/\.\w{2,5}$/i.test(pathname)) return false;
  // Apenas rotas de API com 1 ou 2 segmentos: /auth/login/client, /client/cart, etc.
  // Rotas com .html → não proxy
  return true;
}

// ── Middleware ───────────────────────────────────────

// 1. Arquivos estáticos (dist/)
app.use(express.static(DIST));

// 2. Proxy para API (sem .html, sem assets)
// Nota: Express app.use("/auth", ...) remove o prefixo do req.url.
// Restauramos com req.originalUrl para o backend receber o path completo.
const apiPaths = ["/auth", "/clients", "/merchants", "/drivers", "/ordens", "/notifications"];
apiPaths.forEach(function(p) {
  app.use(p, function(req, res, next) {
    if (/\.\w{2,5}$/i.test(req.path)) return next();
    req.url = req.originalUrl;  // restaura o path completo
    apiProxy(req, res, next);
  });
});

// 3. Fallback: só serve index.html na raiz. HTML inexistente → 404.
app.get("/", function(req, res) {
  res.sendFile(join(DIST, "index.html"));
});

// ── Start ────────────────────────────────────────────
app.listen(PORT, function() {
  console.log("\n  🚀 FastDelivery Frontend → http://0.0.0.0:" + PORT);
  console.log("  🔁 API Proxy → " + API_TARGET);
  console.log("  📁 Static → dist/\n");
});
