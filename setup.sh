#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

echo "==> Verificando prerequisitos..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 no encontrado."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker no encontrado."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "ERROR: docker compose no encontrado."; exit 1; }

echo "==> Creando entorno virtual en $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "==> Configurando .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    .env creado desde .env.example. Revisalo antes de continuar."
else
  echo "    .env ya existe, no se sobreescribe."
fi

echo "==> Levantando base de datos con Docker..."
docker compose up -d

echo "==> Esperando a que PostgreSQL esté listo..."
until docker compose exec db pg_isready -q; do
  sleep 1
done

echo "==> Generando migración inicial..."
alembic revision --autogenerate -m "initial schema"

echo "==> Aplicando migraciones..."
alembic upgrade head

echo "==> Cargando datos de prueba..."
python -m app.seed.seed_data

echo ""
echo "Setup completo."
echo ""
echo "Para activar el entorno virtual en tu terminal:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Para levantar la app:"
echo "  uvicorn app.main:app --reload"
