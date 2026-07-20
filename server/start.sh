#!/bin/bash
# =========================================
# FastDelivery Backend — Start/Stop Server
# =========================================
# Gerencia o servidor FastAPI (uvicorn)
# com PID salvo em backend.pid
#
# Uso:
#   ./start.sh            → sobe o servidor (porta 3101)
#   ./start.sh --stop     → mata o servidor
#   ./start.sh --restart  → reinicia
#   ./start.sh --status   → status do servidor
# =========================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$SCRIPT_DIR/backend.pid"
LOGFILE="$SCRIPT_DIR/backend.log"

# Carrega .env se existir
if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(grep -v '^\s*#' "$SCRIPT_DIR/.env" | xargs)
fi

HOST="${SERVER_HOST:-0.0.0.0}"
PORT="${SERVER_PORT:-3101}"
APP="src.main:create_app"

# --- Caminho do Python
# Procura o .venz em prioridade
if [ -d "$SCRIPT_DIR/.venv" ]; then
  PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif [ -d "$SCRIPT_DIR/../.venv" ]; then
  PYTHON="$(cd "$SCRIPT_DIR/.." && pwd)/.venv/bin/python"
else
  PYTHON="python3"
fi

VENV_DIR="$(dirname "$PYTHON")"

stop_server() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "  🛑 Parando servidor (PID $PID)..."
      kill "$PID"
      for i in $(seq 1 10); do
        kill -0 "$PID" 2>/dev/null || break
        sleep 1
      done
      kill -0 "$PID" 2>/dev/null && kill -9 "$PID" 2>/dev/null && echo "  💀 Forçado (SIGKILL)"
    else
      echo "  ⚠️  PID $PID não está rodando"
    fi
    rm -f "$PIDFILE"
    echo "  ✅ Servidor parado"
  else
    echo "  ✅ Servidor já estava parado"
  fi
}

start_server() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "  ⚠️  Servidor já rodando (PID $PID) em $HOST:$PORT"
      return 0
    fi
    rm -f "$PIDFILE"
  fi

  echo "  🚀 Subindo FastDelivery API em $HOST:$PORT..."

  cd "$SCRIPT_DIR" || exit 1
  export PATH="$VENV_DIR:$PATH"

  nohup "$PYTHON" -m uvicorn "$APP" --factory \
    --host "$HOST" --port "$PORT" \
    --reload \
    >> "$LOGFILE" 2>&1 &
  PID=$!
  echo $PID > "$PIDFILE"

  # Aguarda ficar de pé
  for i in $(seq 1 15); do
    sleep 1
    if curl -sf "http://$HOST:$PORT/health" > /dev/null 2>&1; then
      echo "  ✅ Servidor rodando (PID $PID) → http://$HOST:$PORT"
      echo "  📝 Logs: $LOGFILE"
      return 0
    fi
  done

  echo "  ❌ Servidor não respondeu após 15s — verifique $LOGFILE"
  return 1
}

status_server() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "  🟢 Rodando (PID $PID) em $HOST:$PORT"
      if curl -sf "http://$HOST:$PORT/health" > /dev/null 2>&1; then
        echo "  ✅ Health check: OK"
      else
        echo "  ⚠️  Health check: FAIL"
      fi
    else
      echo "  🔴 PID $PID encontrado mas processo morto (stale PID)"
      rm -f "$PIDFILE"
    fi
  else
    echo "  ⚪ Servidor parado"
  fi
}

# ---- Main ----
case "${1:-}" in
  --stop|-stop)
    stop_server
    ;;
  --restart|-restart)
    stop_server
    sleep 1
    start_server
    ;;
  --status|-status)
    status_server
    ;;
  *)
    start_server
    ;;
esac
