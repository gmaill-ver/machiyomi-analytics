#!/usr/bin/env python3
"""
machiyomi-fudosan.com Analytics Dashboard
Google Analytics + Search Console → Google Sheets

Usage:
    python dashboard.py          # フルダッシュボード更新
    python dashboard.py --quick  # サマリーのみ更新
"""

import argparse
from datetime import datetime
import config
from ga4_client import GA4Client
from search_console_client import SearchConsoleClient
from sheets_client import SheetsClient


def build_dashboard(quick_mode=False):
    """ダッシュボードを構築"""
    print(f"[{datetime.now()}] ダッシュボード更新開始...")
    print(f"対象サイト: {config.SEARCH_CONSOLE_SITE_URL}")
    print(f"期間: 過去{config.REPORT_DAYS}日間")
    print("-" * 50)

    # クライアント初期化
    ga4 = GA4Client()
    gsc = SearchConsoleClient()
    sheets = SheetsClient()

    # === Google Analytics データ取得 ===
    print("[GA4] 日別PVデータ取得中...")
    daily_pv = ga4.get_daily_pv(days=config.REPORT_DAYS)
    print(f"  → {len(daily_pv)}日分取得完了")

    print("[GA4] 記事別パフォーマンス取得中...")
    article_perf = ga4.get_article_performance(days=config.REPORT_DAYS)
    print(f"  → {len(article_perf)}記事分取得完了")

    print("[GA4] 流入元データ取得中...")
    traffic = ga4.get_traffic_sources(days=config.REPORT_DAYS)
    print(f"  → {len(traffic)}ソース取得完了")

    # === Search Console データ取得 ===
    print("[GSC] 検索クエリデータ取得中...")
    queries = gsc.get_search_queries(days=config.REPORT_DAYS)
    print(f"  → {len(queries)}クエリ取得完了")

    print("[GSC] 日別検索パフォーマンス取得中...")
    gsc_daily = gsc.get_daily_performance(days=config.REPORT_DAYS)
    print(f"  → {len(gsc_daily)}日分取得完了")

    print("[GSC] ページ別パフォーマンス取得中...")
    page_perf = gsc.get_page_performance(days=config.REPORT_DAYS)
    print(f"  → {len(page_perf)}ページ取得完了")

    # === サマリーデータ作成 ===
    summary_data = {
        'total_pv': int(daily_pv['screenPageViews'].sum()) if not daily_pv.empty else 0,
        'total_sessions': int(daily_pv['sessions'].sum()) if not daily_pv.empty else 0,
        'total_users': int(daily_pv['activeUsers'].sum()) if not daily_pv.empty else 0,
        'avg_session_duration': round(daily_pv['averageSessionDuration'].mean(), 1) if not daily_pv.empty else 0,
        'total_clicks': int(queries['clicks'].sum()) if not queries.empty else 0,
        'total_impressions': int(queries['impressions'].sum()) if not queries.empty else 0,
        'avg_ctr': round(queries['ctr'].mean(), 2) if not queries.empty else 0,
        'avg_position': round(queries['position'].mean(), 1) if not queries.empty else 0,
        'top_articles': []
    }

    # トップ記事リスト
    if not article_perf.empty:
        for _, row in article_perf.head(10).iterrows():
            summary_data['top_articles'].append({
                'title': row['pageTitle'][:50],
                'pv': int(row['screenPageViews'])
            })

    # === スプレッドシートに書き込み ===
    print("-" * 50)
    print("[Sheets] サマリー更新中...")
    sheets.write_summary(summary_data)

    if not quick_mode:
        print("[Sheets] 日別PVシート更新中...")
        sheets.write_daily_pv(daily_pv)

        print("[Sheets] 記事別パフォーマンスシート更新中...")
        sheets.write_article_performance(article_perf)

        print("[Sheets] 検索クエリシート更新中...")
        sheets.write_search_queries(queries)

        print("[Sheets] トレンド分析シート更新中...")
        sheets.write_trends(daily_pv, gsc_daily)

    print("-" * 50)
    print(f"[{datetime.now()}] ダッシュボード更新完了!")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}")

    # サマリー表示
    print("\n" + "=" * 50)
    print("📊 サマリー（過去30日間）")
    print("=" * 50)
    print(f"総PV数:           {summary_data['total_pv']:,}")
    print(f"総セッション数:   {summary_data['total_sessions']:,}")
    print(f"ユニークユーザー: {summary_data['total_users']:,}")
    print(f"平均滞在時間:     {summary_data['avg_session_duration']}秒")
    print("-" * 50)
    print(f"検索クリック数:   {summary_data['total_clicks']:,}")
    print(f"検索表示回数:     {summary_data['total_impressions']:,}")
    print(f"平均CTR:          {summary_data['avg_ctr']}%")
    print(f"平均検索順位:     {summary_data['avg_position']}位")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='machiyomi-fudosan.com Analytics Dashboard')
    parser.add_argument('--quick', action='store_true', help='サマリーのみ更新')
    args = parser.parse_args()

    build_dashboard(quick_mode=args.quick)


if __name__ == '__main__':
    main()
