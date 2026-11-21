# 受造界守護者

一款以中六指定主題「好管家——受造界守護者」為核心的離線 Pygame 管理遊戲。玩家在十二個回合內管理希望島，每回合把兩次有限行動分配到森林、河流、農田及村莊，在短期需要、生態、社區福祉與希望之間取得平衡。

## 安裝及執行

建議使用 Python 3.11 或以上版本。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Windows 可使用：

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

完成安裝後，遊戲可完全離線運行。所有圖像和音效均由程式即時產生，沒有使用第三方媒體素材。

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

