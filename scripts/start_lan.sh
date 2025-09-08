#!/usr/bin/env bash

set -euo pipefail

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log(){ echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
ok(){ echo -e "${GREEN}[OK]${NC} $1"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $1"; }
err(){ echo -e "${RED}[ERR]${NC} $1" >&2; }

require(){ command -v "$1" >/dev/null 2>&1 || { err "Falta dependencia: $1"; exit 1; }; }

main(){
  log "Verificando dependencias..."
  require docker
  if ! command -v docker-compose >/dev/null 2>&1; then
    warn "docker-compose no encontrado; usando 'docker compose'"
    alias docker-compose='docker compose'
  fi
  ok "Dependencias listas"

  if [ ! -f .env ]; then
    log "Creando .env desde .env.example (ajústalo luego si deseas)"
    cp -n .env.example .env || true
  fi

  # Detectar IP LAN del host
  HOST_IP=$(hostname -I | awk '{print $1}')
  if [ -z "${HOST_IP}" ]; then
    HOST_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}')
  fi
  if [ -z "${HOST_IP}" ]; then
    HOST_IP="127.0.0.1"
    warn "No se pudo detectar IP LAN, usando ${HOST_IP}"
  fi
  ok "IP del host: ${HOST_IP}"

  export REDIS_URL="redis://${HOST_IP}:6379"

  log "Levantando stack Lite (backend + redis + worker)..."
  docker-compose -f docker-compose.lite.yml up -d --build
  ok "Stack Lite levantado"

  log "Esperando a que backend responda..."
  for i in {1..30}; do
    if curl -fsS "http://${HOST_IP}:8000/health" >/dev/null 2>&1; then
      ok "Backend responde en http://${HOST_IP}:8000"
      break
    fi
    sleep 1
  done || true

  echo
  echo -e "${GREEN}Tu red está lista para recibir workers.${NC}"
  echo "Ejecuta ESTE comando en otros dispositivos de tu LAN (Linux/macOS):"
  echo
  echo "-------------------------------------------------------------"
  echo "export REDIS_URL=redis://${HOST_IP}:6379 && \
curl -fsSL https://raw.githubusercontent.com/$(basename $(git rev-parse --show-toplevel) 2>/dev/null || echo 'mea-core')/master/agents/worker.py >/tmp/worker.py || true && \
python3 - <<'PY'
import os,sys,subprocess,urllib.request
url=os.getenv('WORKER_URL','http://${HOST_IP}:8000')  # opcional
try:
  import redis
except Exception:
  subprocess.check_call([sys.executable,'-m','pip','install','redis'])
urllib.request.urlretrieve('http://${HOST_IP}:8000', '/dev/null') if False else None
subprocess.call([sys.executable,'/tmp/worker.py'])
PY"
  echo "-------------------------------------------------------------"
  echo
  echo "O si ya tienes el repo, simplemente:" 
  echo "export REDIS_URL=redis://${HOST_IP}:6379 && python3 agents/worker.py"
  echo
  ok "Listo. Encola tareas con: curl -X POST http://${HOST_IP}:8000/lan/enqueue -H 'Content-Type: application/json' -d '{"id":"t1","text":"hola"}'"
}

main "$@"

