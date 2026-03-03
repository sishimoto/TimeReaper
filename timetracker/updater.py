"""
TimeTracker アップデートチェッカー
GitHub Releases API を使用して最新バージョンを確認し、
アップデート通知と自動更新を提供する。
"""

import logging
import re
import subprocess
import sys
import os
import threading
from dataclasses import dataclass
from typing import Optional

import requests

from timetracker import __version__

logger = logging.getLogger(__name__)

# GitHub リポジトリ情報
GITHUB_OWNER = "sishimoto"
GITHUB_REPO = "TimeTracking"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
GITHUB_TAGS_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/tags"


@dataclass
class UpdateInfo:
    """アップデート情報"""
    current_version: str
    latest_version: str
    is_update_available: bool
    release_url: str = ""
    release_notes: str = ""
    download_url: str = ""
    published_at: str = ""


def parse_version(version_str: str) -> tuple[int, ...]:
    """バージョン文字列をタプルに変換（比較用）
    
    '0.2.0' → (0, 2, 0)
    'v0.2.0' → (0, 2, 0)
    """
    cleaned = version_str.strip().lstrip("v")
    parts = re.findall(r'\d+', cleaned)
    return tuple(int(p) for p in parts)


def check_for_updates(timeout: int = 5) -> Optional[UpdateInfo]:
    """GitHub Releases API で最新バージョンを確認する
    
    Args:
        timeout: API リクエストのタイムアウト（秒）
    
    Returns:
        UpdateInfo: アップデート情報。取得失敗時は None
    """
    current = __version__
    logger.debug(f"アップデートチェック開始: 現在 v{current}")
    
    try:
        # まず GitHub Releases の latest を確認
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            latest_tag = data.get("tag_name", "")
            latest_version = latest_tag.lstrip("v")
            
            is_update = parse_version(latest_version) > parse_version(current)
            
            # DMG のダウンロード URL を探す
            download_url = ""
            for asset in data.get("assets", []):
                if asset.get("name", "").endswith(".dmg"):
                    download_url = asset.get("browser_download_url", "")
                    break
            
            info = UpdateInfo(
                current_version=current,
                latest_version=latest_version,
                is_update_available=is_update,
                release_url=data.get("html_url", ""),
                release_notes=data.get("body", ""),
                download_url=download_url,
                published_at=data.get("published_at", ""),
            )
            
            if is_update:
                logger.info(f"新バージョンあり: v{latest_version} (現在: v{current})")
            else:
                logger.debug(f"最新版です: v{current}")
            
            return info
            
        elif response.status_code == 404:
            # リリースが未作成の場合、タグから確認
            logger.debug("GitHub Release が未作成。タグを確認中...")
            return _check_tags_fallback(current, timeout)
        else:
            logger.warning(f"GitHub API エラー: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.warning("アップデートチェック: タイムアウト")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning("アップデートチェック: ネットワーク接続エラー")
        return None
    except Exception as e:
        logger.warning(f"アップデートチェック失敗: {e}")
        return None


def _check_tags_fallback(current_version: str, timeout: int) -> Optional[UpdateInfo]:
    """GitHub Releases がない場合、タグから最新バージョンを確認"""
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(GITHUB_TAGS_URL, headers=headers, timeout=timeout)
        
        if response.status_code != 200:
            return None
        
        tags = response.json()
        if not tags:
            return UpdateInfo(
                current_version=current_version,
                latest_version=current_version,
                is_update_available=False,
            )
        
        # バージョンタグ（v で始まる）をフィルタして最新を取得
        version_tags = []
        for tag in tags:
            name = tag.get("name", "")
            if re.match(r'^v?\d+\.\d+', name):
                version_tags.append(name)
        
        if not version_tags:
            return UpdateInfo(
                current_version=current_version,
                latest_version=current_version,
                is_update_available=False,
            )
        
        # 最新バージョンを取得
        version_tags.sort(key=lambda t: parse_version(t), reverse=True)
        latest_tag = version_tags[0]
        latest_version = latest_tag.lstrip("v")
        
        is_update = parse_version(latest_version) > parse_version(current_version)
        
        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_version,
            is_update_available=is_update,
            release_url=f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/tag/{latest_tag}",
        )
        
    except Exception as e:
        logger.warning(f"タグ確認失敗: {e}")
        return None


def check_for_updates_async(callback) -> None:
    """バックグラウンドでアップデートチェックを実行
    
    Args:
        callback: UpdateInfo を引数に取るコールバック関数
    """
    def _worker():
        result = check_for_updates()
        if result and callback:
            callback(result)
    
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


def perform_git_update() -> dict:
    """git pull でアップデートを実行する（開発者向け）
    
    Returns:
        dict: {'success': bool, 'message': str, 'details': str}
    """
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_dir = os.path.join(project_dir, ".git")
    
    if not os.path.isdir(git_dir):
        return {
            "success": False,
            "message": "Git リポジトリではありません",
            "details": "自動アップデートは git clone されたインストール環境でのみ利用可能です。",
        }
    
    try:
        # 現在のブランチ確認
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=project_dir, timeout=10,
        )
        branch = result.stdout.strip()
        logger.info(f"現在のブランチ: {branch}")
        
        # ローカルの変更チェック
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=project_dir, timeout=10,
        )
        if result.stdout.strip():
            return {
                "success": False,
                "message": "ローカルに未コミットの変更があります",
                "details": f"先に変更をコミットまたはスタッシュしてください:\n{result.stdout}",
            }
        
        # git pull
        logger.info("git pull 実行中...")
        result = subprocess.run(
            ["git", "pull", "origin", branch],
            capture_output=True, text=True, cwd=project_dir, timeout=60,
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "message": "git pull に失敗しました",
                "details": result.stderr,
            }
        
        pull_output = result.stdout.strip()
        
        # pip install -r requirements.txt（依存パッケージの更新）
        venv_pip = os.path.join(project_dir, "venv", "bin", "pip")
        requirements = os.path.join(project_dir, "requirements.txt")
        
        if os.path.exists(venv_pip) and os.path.exists(requirements):
            logger.info("依存パッケージを更新中...")
            result = subprocess.run(
                [venv_pip, "install", "-r", requirements, "-q"],
                capture_output=True, text=True, cwd=project_dir, timeout=120,
            )
            if result.returncode != 0:
                logger.warning(f"pip install 警告: {result.stderr}")
        
        # 新しいバージョンを確認
        new_version = _get_installed_version(project_dir)
        
        return {
            "success": True,
            "message": f"v{new_version} にアップデートしました",
            "details": pull_output,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "アップデートがタイムアウトしました",
            "details": "ネットワーク接続を確認してください。",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"アップデートに失敗しました: {e}",
            "details": str(e),
        }


def _get_installed_version(project_dir: str) -> str:
    """プロジェクトディレクトリから最新のバージョンを読み込む"""
    init_path = os.path.join(project_dir, "timetracker", "__init__.py")
    try:
        with open(init_path) as f:
            content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else __version__
    except Exception:
        return __version__
