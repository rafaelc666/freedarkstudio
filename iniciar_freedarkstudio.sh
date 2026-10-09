#!/usr/bin/env bash
# FreeDarkStudio — webui com seletor de tema
# Uso: ./iniciar_freedarkstudio.sh [dark|light|freedark]   (padrão: freedark)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
TEMA="${1:-freedark}"
case "$TEMA" in
  dark|light|freedark) ;;
  *) echo "Tema inválido: $TEMA (use: dark, light ou freedark)" >&2; exit 1 ;;
esac
mkdir -p .streamlit
cp ".streamlit/themes/$TEMA.toml" .streamlit/config.toml
echo "Tema aplicado: $TEMA"
export PYTHONPATH="$DIR"
export PYTHONWARNINGS="ignore::UserWarning:streamlit"
exec .venv/bin/python -m streamlit run webui/Main.py \
  --browser.gatherUsageStats=False --server.enableCORS=True "${@:2}"
