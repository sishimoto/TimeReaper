# TimeTracker リリース手順

## バージョニングルール

[セマンティックバージョニング](https://semver.org/lang/ja/) に従う: `MAJOR.MINOR.PATCH`

- **MAJOR**: 後方互換性のない変更（DB スキーマ変更等）
- **MINOR**: 機能追加（後方互換あり）
- **PATCH**: バグ修正

バージョンは `timetracker/__init__.py` の `__version__` で一元管理。  
`setup.py` は自動的にこの値を読み込むため、**変更は `__init__.py` のみ**で OK。

## リリース手順

### 1. バージョン更新

```bash
# timetracker/__init__.py の __version__ を更新
# 例: "0.2.0" → "0.3.0"
vi timetracker/__init__.py
```

### 2. 変更履歴の記録

`CHANGELOG.md` にリリースノートを追記:

```markdown
## [0.3.0] - 2026-03-XX
### Added
- 新機能の説明
### Fixed
- バグ修正の説明
```

### 3. ビルド

```bash
# アイコン生成（初回のみ、または変更時）
pip install Pillow
python scripts/generate_icon.py

# クリーンビルド
./scripts/build.sh --clean

# DMG 作成（配布用）
./scripts/build.sh --clean --dmg
```

### 4. ビルド検証

```bash
# 自動検証
./scripts/build.sh --verify

# 手動検証
open dist/TimeTracker.app
# → メニューバーに ⏱ が表示されることを確認
# → http://127.0.0.1:5555 にアクセスしてダッシュボードを確認
# → /summary ページの動作確認
```

### 5. コミット & タグ

```bash
git add -A
git commit -m "release: v0.3.0

- 変更内容のサマリー"

# タグ付け
git tag -a v0.3.0 -m "v0.3.0: リリース説明"
git push origin main --tags
```

### 6. GitHub Release 作成

1. [GitHub Releases](https://github.com/sishimoto/TimeTracking/releases/new) にアクセス
2. タグ: `v0.3.0` を選択
3. タイトル: `v0.3.0: リリース名`
4. 説明: CHANGELOG.md の該当セクションをコピー
5. `dist/TimeTracker-v0.3.0.dmg` をアップロード
6. 「Publish release」

## 配布方法

### 開発者（git clone）

```bash
git clone https://github.com/sishimoto/TimeTracking.git
cd TimeTracking
./setup.sh
./start.sh
```

### エンドユーザー（DMG）

1. GitHub Releases から最新の `.dmg` をダウンロード
2. DMG を開き、`TimeTracker.app` を `/Applications` にドラッグ
3. 初回起動時:
   - 「開発元が未確認」と表示されたら、右クリック →「開く」を選択
   - アクセシビリティ権限を許可（システム設定で案内）
4. メニューバーの ⏱ アイコンから操作

## ファイル構成

```
scripts/
├── build.sh           # ビルド & 検証スクリプト
└── generate_icon.py   # アイコン生成スクリプト

dist/
├── TimeTracker.app/   # ビルド成果物
│   ├── Contents/
│   │   ├── Info.plist         # バージョン情報等
│   │   ├── MacOS/TimeTracker  # 実行ファイル
│   │   └── Resources/
│   │       ├── config.yaml
│   │       ├── CalHelper.app/
│   │       └── timetracker/templates/
│   └── ...
└── TimeTracker-vX.Y.Z.dmg    # 配布用 DMG
```

## チェックリスト

リリース前に確認:

- [ ] `timetracker/__init__.py` のバージョンを更新した
- [ ] `./scripts/build.sh --clean` でビルドが成功する
- [ ] `./scripts/build.sh --verify` で全チェックが通過する
- [ ] `open dist/TimeTracker.app` で正常に起動する
- [ ] メニューバーに ⏱ が表示される
- [ ] ダッシュボード（http://127.0.0.1:5555）が表示される
- [ ] /summary ページが動作する
- [ ] git tag を付与した
- [ ] GitHub Release を作成した（DMG アップロード済み）
