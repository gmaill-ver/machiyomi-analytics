"""
Google Sheets API Client
スプレッドシートにデータを書き込み・グラフ設定
"""

import gspread
import pandas as pd
from datetime import datetime
import config
from auth import get_sheets_client


class SheetsClient:
    def __init__(self):
        self.client = get_sheets_client()
        self.spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)

    def _get_or_create_sheet(self, sheet_name):
        """シートを取得、なければ作成"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=26
            )
        return worksheet

    def _clear_and_write(self, sheet_name, df, include_header=True):
        """シートをクリアしてDataFrameを書き込み"""
        worksheet = self._get_or_create_sheet(sheet_name)
        worksheet.clear()

        if df.empty:
            worksheet.update('A1', [['データがありません']])
            return worksheet

        # DataFrameを2次元リストに変換
        if include_header:
            data = [df.columns.tolist()] + df.values.tolist()
        else:
            data = df.values.tolist()

        # 日付型を文字列に変換
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                if isinstance(cell, (datetime, pd.Timestamp)):
                    data[i][j] = cell.strftime('%Y-%m-%d')
                elif pd.isna(cell):
                    data[i][j] = ''

        worksheet.update('A1', data)
        return worksheet

    def write_summary(self, summary_data):
        """サマリーシートを更新"""
        sheet_name = config.SHEETS['summary']
        worksheet = self._get_or_create_sheet(sheet_name)
        worksheet.clear()

        # サマリーデータを書き込み
        data = [
            ['machiyomi-fudosan.com ダッシュボード'],
            [''],
            ['最終更新', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            [''],
            ['=== 過去30日間のサマリー ==='],
            [''],
            ['総PV数', summary_data.get('total_pv', 0)],
            ['総セッション数', summary_data.get('total_sessions', 0)],
            ['ユニークユーザー数', summary_data.get('total_users', 0)],
            ['平均セッション時間(秒)', summary_data.get('avg_session_duration', 0)],
            [''],
            ['=== 検索パフォーマンス ==='],
            [''],
            ['総クリック数', summary_data.get('total_clicks', 0)],
            ['総表示回数', summary_data.get('total_impressions', 0)],
            ['平均CTR(%)', summary_data.get('avg_ctr', 0)],
            ['平均検索順位', summary_data.get('avg_position', 0)],
            [''],
            ['=== トップ記事 ==='],
            [''],
        ]

        # トップ5記事を追加
        top_articles = summary_data.get('top_articles', [])
        for i, article in enumerate(top_articles[:5], 1):
            data.append([f'{i}. {article["title"]}', f'{article["pv"]} PV'])

        worksheet.update('A1', data)
        return worksheet

    def write_daily_pv(self, df):
        """日別PVシートを更新"""
        sheet_name = config.SHEETS['daily_pv']

        # カラム名を日本語に
        df_display = df.copy()
        df_display.columns = ['日付', 'PV数', 'セッション数', 'ユーザー数', '平均滞在時間(秒)']

        worksheet = self._clear_and_write(sheet_name, df_display)
        return worksheet

    def write_article_performance(self, df):
        """記事別パフォーマンスシートを更新"""
        sheet_name = config.SHEETS['article_performance']

        df_display = df.copy()
        df_display.columns = ['URL', '記事タイトル', 'PV数', '平均滞在時間(秒)', '直帰率(%)']

        worksheet = self._clear_and_write(sheet_name, df_display)
        return worksheet

    def write_search_queries(self, df):
        """検索クエリシートを更新"""
        sheet_name = config.SHEETS['search_queries']

        df_display = df.copy()
        df_display.columns = ['検索クエリ', 'クリック数', '表示回数', 'CTR(%)', '平均順位']

        worksheet = self._clear_and_write(sheet_name, df_display)
        return worksheet

    def write_trends(self, ga_daily, gsc_daily):
        """トレンド分析シートを更新（GA + GSC統合）"""
        sheet_name = config.SHEETS['trends']
        worksheet = self._get_or_create_sheet(sheet_name)
        worksheet.clear()

        # GA日別データとGSC日別データをマージ
        if not ga_daily.empty and not gsc_daily.empty:
            ga_daily['date'] = pd.to_datetime(ga_daily['date'])
            gsc_daily['date'] = pd.to_datetime(gsc_daily['date'])

            merged = pd.merge(
                ga_daily,
                gsc_daily,
                on='date',
                how='outer'
            ).sort_values('date')

            merged.columns = [
                '日付', 'PV数', 'セッション数', 'ユーザー数', '平均滞在時間',
                'クリック数', '表示回数', 'CTR(%)', '平均順位'
            ]

            self._clear_and_write(sheet_name, merged)

        return worksheet
