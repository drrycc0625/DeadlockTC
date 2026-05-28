# Deadlock 繁體中文漢化（台灣）

> Fork 自 [233Isaac/DeadlockSC](https://github.com/233Isaac/DeadlockSC)（簡中原版）→ [cycleapple/DeadlockTC](https://github.com/cycleapple/DeadlockTC)（繁中初版）→ 本 fork（補翻最新版 + 工具鏈現代化）

**最新更新**：2026-05-28，全量補翻新版 Deadlock 新增的 **4877 條字串**，並補上新版部署所需的語言模組與一鍵安裝器。

---

## ⚠️ 為什麼需要這個 fork

cycleapple 原 fork 停更於 2024-11，期間 Deadlock 經歷大改：

- 新增約 **4877 條未翻字串**（主要在 citadel_main / heroes / attributes / mods / gc）
- Valve 從 `citadel/gameinfo.gi` 的 `SupportedLanguages` **移除了 tchinese 登記**
- 原 Updater 的「散檔 + `-language tchinese`」方法**已不再 work**（語言下拉沒繁中，啟動參數也會 fallback 回 English）

本 fork 補上：

| 補強 | 說明 |
|---|---|
| 4877 條新版翻譯 | 台灣用語、英雄名保留英文 |
| `citadel_tchinese/` 語言模組 | 含 gameinfo.gi，讓 Deadlock 認可繁中 |
| `citadel/cfg/boot.vcfg` | 強制 UILanguage=tchinese |
| **`install.py` 一鍵安裝器** | 自動偵測路徑、複製檔、patch Valve 原檔、備份 |

---

## 🚀 快速安裝（Windows）

### 方法 A：下載 Release zip（推薦給一般使用者）

1. 到 [Releases](https://github.com/drrycc0625/DeadlockTC/releases) 下載最新 zip
2. 解壓縮到任意位置（**建議放在固定位置，未來更新會用到**）
3. **完全退出 Steam**（包含右下系統匣的 Steam 圖示）
4. 在解壓縮資料夾內，雙擊 `install.py`（需安裝 [Python 3.8+](https://www.python.org/downloads/)）
   - 或開啟 PowerShell / cmd：`python install.py`
5. 跟著畫面提示按 Enter 完成
6. 啟動 Steam → 庫 → Deadlock → **右鍵 → 內容 → 一般 → 啟動選項**填入：
   ```
   -language tchinese
   ```
7. 建議同畫面**取消勾選「啟用 Deadlock 的 Steam 雲端」**（避免設定被同步覆蓋）
8. 啟動遊戲，介面即為繁體中文 🎉

### 方法 B：git clone（開發者 / 想看原始碼）

```bash
git clone https://github.com/drrycc0625/DeadlockTC.git
cd DeadlockTC
python install.py
```

### 方法 C：手動指定遊戲路徑

如果自動偵測失敗（例如 Steam 裝在非預設位置）：

```bash
python install.py --game-dir "D:/Games/Steam/steamapps/common/Deadlock/game"
```

### 方法 D：先預覽再安裝

```bash
python install.py --dry-run     # 只顯示會做什麼，不實際寫入
```

---

## 🐧 Linux 安裝

本 repo 的 `install.py` 暫只支援 Windows（用 Registry 偵測 Steam）。Linux 使用者請手動操作：

```bash
git clone https://github.com/drrycc0625/DeadlockTC.git /tmp/deadlock-tc
GAME=~/.local/share/Steam/steamapps/common/Deadlock/game

# 1. 複製整個 game/ 目錄
cp -rv /tmp/deadlock-tc/game/* "$GAME/"

# 2. 手動編輯 Valve 原檔 gameinfo.gi，在 SupportedLanguages 區塊加入 tchinese
#    找到 "schinese" "3" 那一行，下面加一行 "tchinese" "3"
nano "$GAME/citadel/gameinfo.gi"

# 3. Steam 啟動選項加 -language tchinese
```

---

## ✅ 安裝後驗證

1. 啟動 Deadlock，介面應為繁體中文
2. Settings → Language 下拉應出現「**Traditional Chinese**」選項
3. 進入英雄選擇、商店、計分板，文字皆為繁中

---

## ⚠️ 常見問題

### Q1：選什麼語言最後都跑回 English

**原因**：Steam 雲端把 `boot.vcfg` 同步成 english 覆蓋了本地修改。

**解法**：Steam → 庫 → Deadlock → 右鍵 → 內容 → 一般 → **取消勾選「啟用 Deadlock 的 Steam 雲端」**。然後重跑 `python install.py`。

### Q2：Steam「驗證遊戲完整性」後繁中失效

**原因**：Valve 還原了被本 fork 修改過的 `citadel/gameinfo.gi` 與 `citadel/cfg/boot.vcfg`。

**解法**：重跑 `python install.py` 即可恢復。注意 `citadel_tchinese/` 目錄不會被驗證，所以那部分通常保留。

### Q3：進遊戲後某些字串還是英文

**原因**：Deadlock 持續新增字串。本 fork 翻譯涵蓋至 2026-05；之後新版本新增的字串會以英文顯示。

**解法**：到 [Issues](https://github.com/drrycc0625/DeadlockTC/issues) 回報，或自行 PR。

### Q4：install.py 報 "找不到 Steam"

**解法**：手動指定 `--game-dir` 參數，例如：
```bash
python install.py --game-dir "D:/Games/Steam/steamapps/common/Deadlock/game"
```

### Q5：要還原成英文版怎麼辦

每次跑 install.py 都會在 `backup/<時間戳>/` 留下原檔備份。把備份內容複製回遊戲對應位置即可。或者讓 Steam 跑「驗證遊戲完整性」也會自動還原 Valve 原檔。

---

## 📁 目錄結構

```
DeadlockTC/
├── install.py                  ← 一鍵安裝器（Windows 自動、Linux 手動）
├── README.md                   ← 本文件
├── LICENSE                     ← MIT
└── game/                       ← install.py 會把這整個目錄複製到 Deadlock /game
    ├── citadel/
    │   ├── cfg/
    │   │   └── boot.vcfg                                    ← 強制 UILanguage=tchinese
    │   ├── panorama/fonts/fonts.conf                        ← 字型相容設定
    │   └── resource/localization/
    │       └── citadel_*/citadel_*_tchinese.txt             ← 5 大類別繁中翻譯
    └── citadel_tchinese/
        └── gameinfo.gi                                      ← 繁中語言模組（讓 Deadlock 認可 tchinese）
```

---

## 🤝 貢獻翻譯

歡迎開 PR 修正翻譯。**台灣用語準則**：

- **用詞**：影片（非視頻）、最佳化（非優化）、伺服器、預設、設定、載入、離開、線上、螢幕、品質、資訊
- **英雄角色名一律保留英文原名**（Lash、Haze、Abrams、Sinclair、Venator、Graves…），不音譯。理由：repo 既有描述文字（lore / playstyle）本來就用英文英雄名，名稱條目跟著英文較一致。
- **保留**：HTML 標籤 `<span class="highlight">`、`<br>`、變數占位符 `{s:Var}` / `{i:Var}` / `%param%` 不可改動
- **格式**：中英文/數字間不留空格

---

## 📜 授權

沿用上游 cycleapple/DeadlockTC 之 MIT 授權（見 [LICENSE](LICENSE)）。

翻譯內容為 Valve 遊戲《Deadlock》遊戲字串的繁中衍生作品，僅供愛好者使用，不作商業用途。

---

## 🙏 致謝

- [233Isaac/DeadlockSC](https://github.com/233Isaac/DeadlockSC) — 簡中翻譯原始來源
- [cycleapple/DeadlockTC](https://github.com/cycleapple/DeadlockTC) — 繁中初版 fork
- 本 fork 由 Claude (Anthropic Opus 4.7) 協助補翻 4877 條與重建工具鏈
