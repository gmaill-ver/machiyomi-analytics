# machiyomi-analytics

machiyomi-fudosan.com の Google Analytics + Search Console データを
Google スプレッドシートに自動反映するダッシュボードツール

## 📊 機能

- **GA4データ取得**: PV数、セッション、ユーザー数、滞在時間
- **Search Console連携**: 検索クエリ、表示回数、クリック数、CTR、順位
- **Googleスプレッドシート出力**: 自動でシートを更新、グラフ用データ整形
- **PythonAnywhere対応**: 毎日自動実行可能

## 📁 ファイル構成

```
machiyomi-analytics/
├── dashboard.py              # メインスクリプト
├── ga4_client.py             # GA4 API クライアント
├── search_console_client.py  # Search Console API クライアント
├── sheets_client.py          # Sheets API クライアント
├── auth.py                   # 認証モジュール
├── config.py                 # 設定ファイル
├── credentials.json          # サービスアカウントキー（自分で配置）
├── requirements.txt          # 依存ライブラリ
└── README.md
```

## 🚀 セットアップ手順

### 1. Google Cloud Console でプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例: `machiyomi-analytics`）
3. 以下のAPIを有効化:
   - Google Analytics Data API
   - Google Search Console API
   - Google Sheets API
   - Google Drive API

### 2. サービスアカウント作成

1. Cloud Console → 「IAMと管理」→「サービスアカウント」
2. 「サービスアカウントを作成」
   - 名前: `machiyomi-dashboard`
   - ロール: 不要（後で各サービスで権限付与）
3. 作成したサービスアカウントをクリック
4. 「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ JSON
5. ダウンロードしたファイルを `credentials.json` としてこのディレクトリに配置

### 3. 各サービスへの権限付与

#### Google Analytics 4
1. [GA4管理画面](https://analytics.google.com/) にアクセス
2. 管理 → プロパティ → プロパティのアクセス管理
3. サービスアカウントのメールアドレスを追加（閲覧者権限でOK）
4. プロパティID をメモ（`config.py` に設定）

#### Google Search Console
1. [Search Console](https://search.google.com/search-console) にアクセス
2. プロパティ選択 → 設定 → ユーザーと権限
3. サービスアカウントのメールアドレスを追加

#### Google スプレッドシート
1. 新しいスプレッドシートを作成
2. 「共有」→ サービスアカウントのメールアドレスを追加（編集者権限）
3. スプレッドシートID をメモ（URLの `/d/XXXXX/` の部分）

### 4. config.py を編集

```python
GA4_PROPERTY_ID = "123456789"  # あなたのGA4プロパティID
SEARCH_CONSOLE_SITE_URL = "https://machiyomi-fudosan.com/"
SPREADSHEET_ID = "あなたのスプレッドシートID"
```

### 5. ライブラリインストール

```bash
pip install -r requirements.txt
```

### 6. 実行

```bash
python dashboard.py
```

## 📅 PythonAnywhere で定期実行

### 1. ファイルをアップロード

PythonAnywhere の Files タブで、すべてのファイルをアップロード

### 2. 仮想環境作成

```bash
mkvirtualenv machiyomi-env --python=python3.10
pip install -r requirements.txt
```

### 3. タスクスケジューラ設定

Tasks タブ → 新しいタスク追加:

```bash
/home/あなたのユーザー名/.virtualenvs/machiyomi-env/bin/python /home/あなたのユーザー名/machiyomi-analytics/dashboard.py
```

時間: 毎日 06:00 など

## 📈 スプレッドシートのグラフ設定（手動）

スプレッドシートに書き込まれたデータを使って、以下のグラフを作成:

### 1. 日別PV推移（折れ線グラフ）
- データ範囲: `日別PV!A:B`
- X軸: 日付
- Y軸: PV数

### 2. 検索順位トレンド（折れ線グラフ）
- データ範囲: `トレンド分析!A:I`
- クリック数、表示回数、順位を可視化

### 3. トップ記事（横棒グラフ）
- データ範囲: `記事別パフォーマンス!B:C`
- 上位10記事のPV比較

### 4. 検索クエリ（横棒グラフ）
- データ範囲: `検索クエリ!A:C`
- 表示回数・クリック数の多いクエリ

## 🔧 トラブルシューティング

### 認証エラー
- `credentials.json` が正しい場所にあるか確認
- サービスアカウントに各サービスへの権限が付与されているか確認

### GA4データが取れない
- プロパティIDが正しいか確認
- サービスアカウントにGA4の閲覧権限があるか確認

### Search Consoleデータが取れない
- サイトURLが正確か確認（末尾のスラッシュに注意）
- データ反映まで3日かかることがある

## 📝 ライセンス

MIT License
