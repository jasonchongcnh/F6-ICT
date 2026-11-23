# 受造界守護者

一款以中六指定主題「好管家——受造界守護者」為核心的離線 Pygame 管理遊戲。玩家在十二個回合內管理希望島，每回合把兩次有限行動分配到森林、河流、農田及村莊，在短期需要、生態、社區福祉與希望之間取得平衡。

## 安裝及執行

本專題使用 Pygame CE 2.5.6，支援 **Python 3.11、3.12 或 3.13**。請勿使用目前不相容的 Anaconda Python 3.14，否則 Pygame 的字型模組可能無法載入。

### macOS（建議方法）

在 Terminal 進入專題資料夾後執行：

```bash
chmod +x setup_macos.command
./setup_macos.command
```

安裝程式會尋找 Python 3.11–3.13、建立獨立的 `.venv-mac`、安裝 Pygame，然後啟動遊戲。以後可用：

```bash
.venv-mac/bin/python main.py
```

如果 Mac 只有 Anaconda Python 3.14，先安裝相容版本：

```bash
brew install python@3.12
```

或從 [python.org 的 macOS 下載頁](https://www.python.org/downloads/macos/) 安裝 Python 3.12／3.13，再重新執行 `setup_macos.command`。

### Linux／其他 Unix 系統

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

### Windows

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

完成安裝後，遊戲可完全離線運行。所有圖像和音效均由程式即時產生，沒有使用第三方媒體素材。

## macOS 常見問題

如看到 `font module not available`、`partially initialized module 'pygame.font'` 或 `NotImplementedError`，代表執行了不相容的 Python／Pygame 組合。不要在 Anaconda Python 3.14 直接執行 `python main.py`；請使用上述 `.venv-mac/bin/python main.py`。

## 操作方法

- `WASD`／方向鍵：在島嶼區域之間移動
- `1`／`2`、`Enter`／`Space`：執行行動或選擇按鈕
- 滑鼠：選擇按鈕和事件選項
- `Esc`：暫停或返回
- `F5`：儲存；`F9`：載入
- `M`：聲音開關；`C`：高對比模式

主選單提供遊戲說明、新遊戲、載入和離開。暫停選單提供儲存、繼續、重新開始及返回主選單。

## 開發驗證

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m tools.balance_simulation --runs 500
```

架構、工程筆記、測試數據、錯誤紀錄及提交指引位於 `docs/` 和 `evidence/`。

