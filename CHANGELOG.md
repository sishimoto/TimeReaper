# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/ja/).

## [0.2.0] - 2026-03-03

### Added
- 日次サマリーページ: 10分ブロック単位のタグ一括編集 (#15)
- サマリーページ: Shift+クリックで範囲選択
- サマリーページ: 各ブロックにタブ/ウィンドウタイトルを補足表示
- ダッシュボード: タグ編集 UI (#14)
- ダッシュボード: カード→セクションスクロール
- 2軸分類システム: タスク分類 + コスト分類 (#11)
- Mac Calendar 連携: EventKit ヘルパーアプリ経由 (#8, #9)
- カレンダーイベント中の自動 meeting 分類 (#10)
- ブラウザタブタイトル記録 (#6, #12)
- 起動スクリプト + LaunchAgent による自動起動 (#13)
- py2app パッケージング (#7)
- ビルドスクリプト (scripts/build.sh)
- アイコン生成スクリプト (scripts/generate_icon.py)
- リリース手順書 (docs/RELEASE.md)
- バージョン管理一元化 (__init__.py → setup.py 自動読み込み)

### Fixed
- UTC タイムゾーンによる日付ずれ修正 (#15)
- Electron アプリ名の解決改善

## [0.1.0] - 2026-02-25

### Added
- アクティブウィンドウ監視 (AppleScript ベース)
- ブラウザ URL 取得 (Chrome / Safari / Arc / Edge / Firefox)
- アイドル検出 (HIDIdleTime、5分閾値)
- アクティビティ自動分類
- Flask Web ダッシュボード (ダークテーマ、Chart.js)
- macOS メニューバー常駐 (rumps)
- CSV エクスポート
- Electron アプリ名の解決 (bundle ID マッピング)
