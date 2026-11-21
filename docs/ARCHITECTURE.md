# 系統架構及 API 說明

```text
main.py
  └─ GameApp（guardians/app.py）——輸入、場景、回饋、渲染
       ├─ UI 工具（guardians/ui.py）——按鈕、文字換行、數值條
       ├─ GameModel（guardians/model.py）——規則與狀態轉換
       │    └─ events.py + data/events.json——經驗證的事件資料
       └─ storage.py——原子式 JSON 儲存／載入

tests/——模型、事件、存檔、畫面流程及無障礙回歸測試
tools/balance_simulation.py——無視窗策略模擬器
```

## 資料流程

1. Pygame 把鍵盤／滑鼠事件交給 `GameApp.handle_event`。
2. 當前場景把輸入轉成 `perform_zone_action` 或 `choose_event` 等模型命令。
3. `GameModel` 驗證命令、改變資源／價值、排程延後效果、記錄歷史並檢查結局。
4. `GameApp` 讀取新狀態，渲染地圖、儀表板、事件卡或結局。
5. `storage.py` 只序列化模型狀態，畫面物件和執行中程序不會寫入存檔。

模型完全不依賴 Pygame，因此測試和數百次模擬可快速執行，介面亦不會暗中改變規則。

