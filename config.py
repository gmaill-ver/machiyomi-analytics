"""
Configuration for machiyomi-fudosan.com Analytics Dashboard
"""

# Google Analytics 4 Property ID
# GA4管理画面 → プロパティ設定 → プロパティID
GA4_PROPERTY_ID = "YOUR_GA4_PROPERTY_ID"  # 例: "123456789"

# Google Search Console Site URL
SEARCH_CONSOLE_SITE_URL = "https://machiyomi-fudosan.com/"

# Google Spreadsheet ID
# スプレッドシートのURLから取得: https://docs.google.com/spreadsheets/d/XXXXX/edit
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"

# Credentials file path (サービスアカウントのJSONキー)
CREDENTIALS_FILE = "credentials.json"

# レポート期間設定
REPORT_DAYS = 30  # 過去30日分のデータを取得

# シート名設定
SHEETS = {
    "daily_pv": "日別PV",
    "article_performance": "記事別パフォーマンス",
    "search_queries": "検索クエリ",
    "trends": "トレンド分析",
    "summary": "サマリー"
}
