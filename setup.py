"""
TimeTracker - py2app セットアップスクリプト
macOS アプリケーションバンドル (.app) のビルドに使用します。

使い方:
    python setup.py py2app
    python setup.py py2app --alias  (開発用: シンボリックリンクビルド)
"""

import re
from setuptools import setup


def get_version():
    """timetracker/__init__.py からバージョンを動的に読み込む"""
    with open("timetracker/__init__.py", "r") as f:
        content = f.read()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise RuntimeError("バージョン情報が見つかりません")
    return match.group(1)


VERSION = get_version()

APP = ["main.py"]
DATA_FILES = [
    ("../Resources", ["config.yaml"]),
    ("../Resources/timetracker/templates", [
        "timetracker/templates/dashboard.html",
        "timetracker/templates/summary.html",
        "timetracker/templates/weekly.html",
    ]),
]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "assets/AppIcon.icns" if __import__("os").path.exists("assets/AppIcon.icns") else None,
    "plist": {
        "CFBundleName": "TimeTracker",
        "CFBundleDisplayName": "TimeTracker",
        "CFBundleIdentifier": "com.timetracker.app",
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "LSUIElement": True,  # メニューバーアプリとしてDockに表示しない
        "NSAppleEventsUsageDescription": "TimeTracker needs access to System Events to monitor active windows.",
        "NSAccessibilityUsageDescription": "TimeTracker needs accessibility access to detect the active window.",
    },
    "packages": [
        "timetracker",
        "timetracker.integrations",
        "flask",
        "jinja2",
        "rumps",
    ],
    "includes": [
        "timetracker.config",
        "timetracker.monitor",
        "timetracker.classifier",
        "timetracker.database",
        "timetracker.dashboard",
        "timetracker.menubar",
        "urllib3.contrib.resolver",
        "urllib3.contrib.resolver.system",
        "urllib3.contrib.resolver._system",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "test",
    ],
}

setup(
    app=APP,
    name="TimeTracker",
    version=VERSION,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
