#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "《受造界守護者》macOS 安裝程式"
echo "正在尋找相容的 Python 3.11–3.13……"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [[ -z "$PYTHON_BIN" ]] && command -v python3 >/dev/null 2>&1; then
    PYTHON_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || true)"
    if [[ "$PYTHON_MINOR" == "11" || "$PYTHON_MINOR" == "12" || "$PYTHON_MINOR" == "13" ]]; then
        PYTHON_BIN="python3"
    fi
fi

if [[ -z "$PYTHON_BIN" ]]; then
    echo
    echo "找不到相容的 Python。你的 Anaconda Python 3.14 暫不支援 Pygame CE 2.5.6。"
    echo
    echo "請先執行其中一項："
    echo "  brew install python@3.12"
    echo "或在 https://www.python.org/downloads/macos/ 安裝 Python 3.12／3.13。"
    echo
    echo "安裝後再次雙擊 setup_macos.command。"
    read -r -p "按 Enter 關閉……" _
    exit 1
fi

echo "使用 $($PYTHON_BIN --version) 建立獨立環境 .venv-mac"
"$PYTHON_BIN" -m venv .venv-mac
./.venv-mac/bin/python -m pip install --upgrade pip
./.venv-mac/bin/python -m pip install -r requirements.txt

echo
echo "安裝完成，正在啟動遊戲……"
./.venv-mac/bin/python main.py

