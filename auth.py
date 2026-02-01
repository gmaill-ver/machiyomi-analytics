"""
Google API Authentication Module
サービスアカウントを使用した認証
"""

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from googleapiclient.discovery import build
import gspread
import config


def get_credentials():
    """サービスアカウント認証情報を取得"""
    SCOPES = [
        'https://www.googleapis.com/auth/analytics.readonly',
        'https://www.googleapis.com/auth/webmasters.readonly',
        'https://www.googleapis.com/auth/spreadsheets',
    ]

    credentials = service_account.Credentials.from_service_account_file(
        config.CREDENTIALS_FILE,
        scopes=SCOPES
    )
    return credentials


def get_ga4_client():
    """Google Analytics 4 クライアントを取得"""
    credentials = get_credentials()
    client = BetaAnalyticsDataClient(credentials=credentials)
    return client


def get_search_console_service():
    """Search Console サービスを取得"""
    credentials = get_credentials()
    service = build('searchconsole', 'v1', credentials=credentials)
    return service


def get_sheets_client():
    """Google Sheets クライアントを取得"""
    credentials = get_credentials()
    client = gspread.authorize(credentials)
    return client
