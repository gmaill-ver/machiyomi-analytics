"""
Google Search Console API Client
検索パフォーマンスデータを取得
"""

from datetime import datetime, timedelta
import pandas as pd
import config
from auth import get_search_console_service


class SearchConsoleClient:
    def __init__(self):
        self.service = get_search_console_service()
        self.site_url = config.SEARCH_CONSOLE_SITE_URL

    def _execute_request(self, request_body):
        """APIリクエストを実行"""
        response = self.service.searchanalytics().query(
            siteUrl=self.site_url,
            body=request_body
        ).execute()
        return response.get('rows', [])

    def get_search_queries(self, days=30, limit=100):
        """検索クエリ別パフォーマンスを取得"""
        end_date = datetime.now() - timedelta(days=3)  # GSCは3日前まで
        start_date = end_date - timedelta(days=days)

        request_body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'rowLimit': limit,
            'startRow': 0
        }

        rows = self._execute_request(request_body)

        data = []
        for row in rows:
            data.append({
                'query': row['keys'][0],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('impressions', ascending=False)
        return df

    def get_page_performance(self, days=30, limit=100):
        """ページ別検索パフォーマンスを取得"""
        end_date = datetime.now() - timedelta(days=3)
        start_date = end_date - timedelta(days=days)

        request_body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'rowLimit': limit,
            'startRow': 0
        }

        rows = self._execute_request(request_body)

        data = []
        for row in rows:
            data.append({
                'page': row['keys'][0],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('clicks', ascending=False)
        return df

    def get_daily_performance(self, days=30):
        """日別検索パフォーマンスを取得"""
        end_date = datetime.now() - timedelta(days=3)
        start_date = end_date - timedelta(days=days)

        request_body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['date'],
            'rowLimit': days,
            'startRow': 0
        }

        rows = self._execute_request(request_body)

        data = []
        for row in rows:
            data.append({
                'date': row['keys'][0],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        return df

    def get_query_by_page(self, page_url, days=30, limit=20):
        """特定ページの検索クエリを取得"""
        end_date = datetime.now() - timedelta(days=3)
        start_date = end_date - timedelta(days=days)

        request_body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url
                }]
            }],
            'rowLimit': limit,
            'startRow': 0
        }

        rows = self._execute_request(request_body)

        data = []
        for row in rows:
            data.append({
                'query': row['keys'][0],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })

        return pd.DataFrame(data)

    def get_device_performance(self, days=30):
        """デバイス別検索パフォーマンスを取得"""
        end_date = datetime.now() - timedelta(days=3)
        start_date = end_date - timedelta(days=days)

        request_body = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['device'],
            'rowLimit': 10,
            'startRow': 0
        }

        rows = self._execute_request(request_body)

        data = []
        for row in rows:
            data.append({
                'device': row['keys'][0],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })

        return pd.DataFrame(data)
