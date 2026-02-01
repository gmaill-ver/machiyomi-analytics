"""
Google Analytics 4 Data API Client
GA4からデータを取得
"""

from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)
from datetime import datetime, timedelta
import pandas as pd
import config
from auth import get_ga4_client


class GA4Client:
    def __init__(self):
        self.client = get_ga4_client()
        self.property_id = f"properties/{config.GA4_PROPERTY_ID}"

    def _run_report(self, dimensions, metrics, date_range_days=30, limit=100):
        """汎用レポート実行"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range_days)

        request = RunReportRequest(
            property=self.property_id,
            date_ranges=[DateRange(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )],
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            limit=limit
        )

        response = self.client.run_report(request)
        return self._response_to_dataframe(response, dimensions, metrics)

    def _response_to_dataframe(self, response, dimensions, metrics):
        """APIレスポンスをDataFrameに変換"""
        rows = []
        for row in response.rows:
            row_data = {}
            for i, dim in enumerate(dimensions):
                row_data[dim] = row.dimension_values[i].value
            for i, met in enumerate(metrics):
                row_data[met] = row.metric_values[i].value
            rows.append(row_data)
        return pd.DataFrame(rows)

    def get_daily_pv(self, days=30):
        """日別PV数を取得"""
        df = self._run_report(
            dimensions=["date"],
            metrics=["screenPageViews", "sessions", "activeUsers", "averageSessionDuration"],
            date_range_days=days,
            limit=days
        )
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.sort_values('date')
            df['screenPageViews'] = df['screenPageViews'].astype(int)
            df['sessions'] = df['sessions'].astype(int)
            df['activeUsers'] = df['activeUsers'].astype(int)
            df['averageSessionDuration'] = df['averageSessionDuration'].astype(float).round(1)
        return df

    def get_article_performance(self, days=30, limit=100):
        """記事別パフォーマンスを取得"""
        df = self._run_report(
            dimensions=["pagePath", "pageTitle"],
            metrics=["screenPageViews", "averageSessionDuration", "bounceRate"],
            date_range_days=days,
            limit=limit
        )
        if not df.empty:
            # ブログ記事のみフィルタ（トップページやカテゴリページを除外）
            df = df[df['pagePath'].str.match(r'^/[a-z0-9\-]+/$|^/\d+/$')]
            df['screenPageViews'] = df['screenPageViews'].astype(int)
            df['averageSessionDuration'] = df['averageSessionDuration'].astype(float).round(1)
            df['bounceRate'] = (df['bounceRate'].astype(float) * 100).round(1)
            df = df.sort_values('screenPageViews', ascending=False)
        return df

    def get_traffic_sources(self, days=30):
        """流入元を取得"""
        df = self._run_report(
            dimensions=["sessionSource", "sessionMedium"],
            metrics=["sessions", "activeUsers"],
            date_range_days=days,
            limit=20
        )
        if not df.empty:
            df['sessions'] = df['sessions'].astype(int)
            df['activeUsers'] = df['activeUsers'].astype(int)
            df = df.sort_values('sessions', ascending=False)
        return df

    def get_device_category(self, days=30):
        """デバイスカテゴリ別を取得"""
        df = self._run_report(
            dimensions=["deviceCategory"],
            metrics=["sessions", "screenPageViews"],
            date_range_days=days,
            limit=10
        )
        if not df.empty:
            df['sessions'] = df['sessions'].astype(int)
            df['screenPageViews'] = df['screenPageViews'].astype(int)
        return df

    def get_realtime_users(self):
        """リアルタイムユーザー数を取得（参考）"""
        # Note: リアルタイムAPIは別のエンドポイント
        # ここでは過去1時間のデータで代用
        return self._run_report(
            dimensions=["hour"],
            metrics=["activeUsers"],
            date_range_days=1,
            limit=24
        )
