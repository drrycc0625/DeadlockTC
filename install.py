# -*- coding: utf-8 -*-
"""
Deadlock 繁體中文漢化一鍵安裝器
適用：Windows，需 Python 3.8+

功能：
1. 自動偵測 Steam 與 Deadlock 安裝路徑（從 Windows Registry）
2. 把 fork 內的 game/ 全部複製到遊戲目錄（含散檔翻譯、boot.vcfg、citadel_tchinese 模組）
3. 自動 patch Valve 原檔 citadel/gameinfo.gi 把 tchinese 加入 SupportedLanguages
4. 所有被覆蓋的原檔會備份到 backup/<時間戳>/
5. 完成後提示使用者設定啟動參數與關閉 Steam Cloud

使用：
    python install.py                        # 互動式自動安裝
    python install.py --game-dir "C:/..."    # 手動指定遊戲 /game 目錄
    python install.py --dry-run              # 只顯示會做什麼，不實際寫入
"""
import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STEAM_APP_ID = 1422450
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_GAME = SCRIPT_DIR / "game"
BACKUP_ROOT = SCRIPT_DIR / "backup"
BACKUP_DIR = BACKUP_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")


def find_steam_path():
    """從 Windows Registry 找 Steam 安裝路徑。"""
    try:
        import winreg
    except ImportError:
        return None
    for hive_path in (r"SOFTWARE\Wow6432Node\Valve\Steam", r"SOFTWARE\Valve\Steam"):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hive_path) as key:
                p, _ = winreg.QueryValueEx(key, "InstallPath")
                return Path(p)
        except FileNotFoundError:
            continue
        except OSError:
            continue
    return None


def find_deadlock_game_dir(steam_path):
    """從 Steam libraryfolders.vdf 找 Deadlock，回傳 /game 目錄。"""
    if not steam_path:
        return None
    candidates = [steam_path / "steamapps"]
    libfolders = steam_path / "steamapps" / "libraryfolders.vdf"
    if libfolders.exists():
        text = libfolders.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'"path"\s+"([^"]+)"', text):
            lib = Path(m.group(1).replace("\\\\", "\\"))
            candidates.append(lib / "steamapps")
    for sapps in candidates:
        manifest = sapps / f"appmanifest_{STEAM_APP_ID}.acf"
        game_root = sapps / "common" / "Deadlock" / "game"
        if manifest.exists() and game_root.exists():
            return game_root
    return None


def backup_file(src_in_game, game_dir):
    """把 src_in_game 備份到 BACKUP_DIR，保留相對結構。"""
    if not src_in_game.exists():
        return
    try:
        rel = src_in_game.relative_to(game_dir)
    except ValueError:
        rel = Path(src_in_game.name)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_in_game, dst)


def copy_repo_files(game_dir, dry_run):
    """把 REPO_GAME 內所有檔案複製到 game_dir 對應位置。"""
    if not REPO_GAME.exists():
        print(f"! 找不到 {REPO_GAME}（請確認 install.py 在 fork 根目錄）")
        return False
    n_copied = 0
    for src in REPO_GAME.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(REPO_GAME)
        dst = game_dir / rel
        if dry_run:
            print(f"  [dry-run] {rel}")
            continue
        if dst.exists():
            backup_file(dst, game_dir)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n_copied += 1
        print(f"  ✓ {rel}")
    if not dry_run:
        print(f"  共複製 {n_copied} 個檔")
    return True


def patch_supported_languages(game_dir, dry_run):
    """在 citadel/gameinfo.gi 的 SupportedLanguages 區塊加入 tchinese。"""
    gi = game_dir / "citadel" / "gameinfo.gi"
    if not gi.exists():
        print(f"  ! 找不到 {gi}")
        return False
    raw = gi.read_text(encoding="utf-8-sig")
    if '"tchinese"' in raw:
        print(f"  - 已含 tchinese，無需 patch")
        return True
    # 在 "schinese" "3" 後插入 "tchinese" "3"
    # 用容錯 pattern：允許不同縮排/換行
    pattern = re.compile(r'("schinese"\s+"3")(\s*\r?\n)(\s*)("spanish")')
    m = pattern.search(raw)
    if not m:
        print('  ! 找不到 schinese→spanish 區塊，請手動編輯加入 "tchinese" "3"')
        return False
    insert = f'{m.group(1)}{m.group(2)}{m.group(3)}"tchinese" "3"{m.group(2)}{m.group(3)}{m.group(4)}'
    new = raw[:m.start()] + insert + raw[m.end():]
    if dry_run:
        print(f"  [dry-run] 將在 SupportedLanguages 加入 tchinese")
        return True
    backup_file(gi, game_dir)
    gi.write_text(new, encoding="utf-8")
    print(f"  ✓ 已加入 tchinese 到 SupportedLanguages")
    return True


def print_final_notice(game_dir, dry_run):
    print()
    print("=" * 60)
    if dry_run:
        print("  ✓ DRY-RUN 完成（未實際寫入任何檔案）")
    else:
        print("  ✓ 安裝完成！")
    print("=" * 60)
    if not dry_run:
        print(f"備份目錄：{BACKUP_DIR}")
        print()
        print("⚠️  最後一哩路（請務必照做，否則繁中不會顯示）：")
        print()
        print("  1. Steam 啟動選項加入：-language tchinese")
        print("     操作：Steam 庫 → Deadlock → 右鍵 → 內容 → 一般 → 啟動選項")
        print()
        print("  2. 建議關閉 Steam 雲端（避免 boot.vcfg 被同步覆寫成英文）：")
        print("     Deadlock → 右鍵 → 內容 → 一般 → 取消「啟用 Deadlock 的 Steam 雲端」")
        print()
        print("  3. 開啟遊戲，介面應變為繁體中文。")
        print()
        print("⚠️  如果之後做了 Steam「驗證遊戲完整性」，gameinfo.gi 與 boot.vcfg")
        print("    會被 Valve 還原；重跑本腳本即可恢復。")


def main():
    ap = argparse.ArgumentParser(
        description="Deadlock 繁體中文漢化一鍵安裝器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--game-dir", type=Path, help="手動指定 Deadlock /game 目錄")
    ap.add_argument("--dry-run", action="store_true", help="只顯示會做什麼，不實際寫入")
    ap.add_argument("--yes", action="store_true", help="跳過開始前的確認")
    args = ap.parse_args()

    if sys.platform != "win32":
        print("本一鍵安裝器目前僅支援 Windows。")
        print("Linux 使用者請參考 README 手動複製 game/ 內容到遊戲目錄，並編輯 citadel/gameinfo.gi。")
        sys.exit(1)

    print("=" * 60)
    print("  Deadlock 繁體中文漢化一鍵安裝器")
    print("=" * 60)

    if args.game_dir:
        game_dir = args.game_dir
        print(f"指定路徑：{game_dir}")
    else:
        print("偵測 Steam 與 Deadlock 路徑...")
        steam = find_steam_path()
        if not steam:
            print("! 找不到 Steam 安裝路徑。請用 --game-dir 指定 Deadlock 的 /game 目錄。")
            sys.exit(1)
        print(f"  Steam: {steam}")
        game_dir = find_deadlock_game_dir(steam)
        if not game_dir:
            print("! 找不到 Deadlock 安裝。請用 --game-dir 指定，例如：")
            print(r'    python install.py --game-dir "C:\Program Files (x86)\Steam\steamapps\common\Deadlock\game"')
            sys.exit(1)
        print(f"  Deadlock /game: {game_dir}")

    if not (game_dir / "citadel" / "gameinfo.gi").exists():
        print(f"! 路徑似乎不正確（找不到 {game_dir}/citadel/gameinfo.gi）")
        sys.exit(1)

    if not args.dry_run and not args.yes:
        try:
            print()
            print("即將執行：")
            print("  1. 複製 fork 內 game/ 全部翻譯與設定檔到遊戲目錄")
            print("  2. Patch citadel/gameinfo.gi 加入 tchinese 到 SupportedLanguages")
            print("  3. 所有被覆蓋的原檔會備份到 backup/<時間戳>/")
            print()
            input("按 Enter 開始（Ctrl+C 取消）...")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            sys.exit(0)

    print()
    print("[1/2] 複製翻譯與設定檔")
    if not copy_repo_files(game_dir, args.dry_run):
        sys.exit(1)

    print()
    print("[2/2] Patch citadel/gameinfo.gi（讓 Deadlock 認可 tchinese 語言）")
    if not patch_supported_languages(game_dir, args.dry_run):
        sys.exit(1)

    print_final_notice(game_dir, args.dry_run)

    if not args.dry_run and not args.yes:
        try:
            input("\n按 Enter 結束...")
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
