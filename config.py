"""
Configuration for machiyomi-fudosan.com Analytics Dashboard
"""

# Google Analytics 4 Property ID
# GA4管理画面 → プロパティ設定 → プロパティID
GA4_PROPERTY_ID = "510946460"  # machiyomi-fudosan.com

# Google Search Console Site URL
SEARCH_CONSOLE_SITE_URL = "https://machiyomi-fudosan.com/"

# Google Spreadsheet ID
# スプレッドシートのURLから取得: https://docs.google.com/spreadsheets/d/XXXXX/edit
SPREADSHEET_ID = "1_SVVgdH49XdnsqZeMOCzddZqvFwVmbAtYo_ofRsRack"

# Credentials file path (サービスアカウントのJSONキー)
CREDENTIALS_FILE = "credentials.json"

# レポート期間設定
REPORT_DAYS = 120  # 過去120日分のデータを取得（10月6日〜全期間）

# シート名設定
SHEETS = {
    "daily_pv": "日別PV",
    "article_performance": "記事別パフォーマンス",
    "search_queries": "検索クエリ",
    "trends": "トレンド分析",
    "summary": "サマリー",
    "time_analysis": "時間帯分析"
}
