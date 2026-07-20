#!/bin/bash
# =========================================
# FastDelivery Frontend — Start/Stop Server
# =========================================
# Uso:
#   ./start.sh            → builda (se necessário) e sobe
#   ./start.sh --dev      → modo dev (Vite, porta 5173)
#   ./start.sh --stop     → mata o servidor
#   ./start.sh --restart  → reinicia
#   ./start.sh --status   → status
# =========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$SCRIPT_DIR/frontend.pid"
LOGFILE="$SCRIPT_DIR/frontend.log"

# ── Carrega .env ─────────────────────────────────────
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

PORT="${EXPRESS_PORT:-3000}"
DEV_PORT="${VITE_DEV_PORT:-5173}"

# ── Funções ──────────────────────────────────────────

stop_server() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "  🛑 Parando (PID $PID)..."
      kill "$PID" 2>/dev/null || true
      for i in $(seq 1 5); do
        kill -0 "$PID" 2>/dev/null || break
        sleep 1
      done
      kill -0 "$PID" 2>/dev/null && kill -9 "$PID" 2>/dev/null && echo "  💀 Forçado SIGKILL"
    fi
    rm -f "$PIDFILE"
    echo "  ✅ Parado"
  else
    echo "  ✅ Já estava parado"
  fi
}

start_prod() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "  ⚠️  Já rodando (PID $(cat "$PIDFILE")) na porta $PORT"
    return 0
  fi
  rm -f "$PIDFILE"

  # Build automático se necessário
  if [ ! -d "$SCRIPT_DIR/dist" ]; then
    echo "  📦 Build não encontrado. Rodando 'npm run build'..."
    cd "$SCRIPT_DIR" && npm run build
  fi

  echo "  🚀 Subindo Express em http://0.0.0.0:$PORT ..."
  cd "$SCRIPT_DIR" || exit 1

  export PORT
  nohup node server.js >> "$LOGFILE" 2>&1 &
  PID=$!
  echo "$PID" > "$PIDFILE"

  sleep 2
  if kill -0 "$PID" 2>/dev/null; then
    echo "  ✅ Rodando (PID $PID) → http://0.0.0.0:$PORT"
    echo "  📝 Logs: $LOGFILE"
    echo "  🔁 Proxy API → ${VITE_API_URL:-http://0.0.0.0:3101}"
  else
    echo "  ❌ Morreu ao iniciar — veja $LOGFILE"
    rm -f "$PIDFILE"
    exit 1
  fi
}

start_dev() {
  echo "  🧪 Subindo Vite dev server em http://localhost:$DEV_PORT ..."
  cd "$SCRIPT_DIR" || exit 1

  npx vite --host --port "$DEV_PORT" >> "$LOGFILE" 2>&1 &
  PID=$!
  echo "$PID" > "$PIDFILE"

  sleep 2
  if kill -0 "$PID" 2>/dev/null; then
    echo "  ✅ Vite rodando (PID $PID) → http://localhost:$DEV_PORT"
    echo "  📝 Logs: $LOGFILE"
    echo "  🔁 Proxy API → ${VITE_API_URL:-http://0.0.0.0:3101}"
  else
    echo "  ❌ Vite morreu — veja $LOGFILE"
    rm -f "$PIDFILE"
    exit 1
  fi
}

status_server() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "  🟢 Rodando (PID $(cat "$PIDFILE"))"
  else
    echo "  ⚪ Parado"
    [ -f "$PIDFILE" ] && rm -f "$PIDFILE"
  fi
}

# ── Main ─────────────────────────────────────────────

case "${1:-}" in
  --dev|-dev)
    stop_server
    sleep 1
    start_dev
    ;;
  --stop|-stop)
    stop_server
    ;;
  --restart|-restart)
    stop_server
    sleep 1
    start_prod
    ;;
  --status|-status)
    status_server
    ;;
  *)
    start_prod
    ;;
esac
