"""
Google Sheets Chart Creator
スプレッドシートにグラフを自動作成
"""

import config
from auth import get_sheets_client


def create_charts(spreadsheet_id):
    """全シートにグラフを作成"""
    client = get_sheets_client()
    spreadsheet = client.open_by_key(spreadsheet_id)

    # 各シートのIDを取得
    sheet_ids = {}
    for sheet in spreadsheet.worksheets():
        sheet_ids[sheet.title] = sheet.id

    requests = []

    # 1. 日別PV推移グラフ（折れ線）
    if config.SHEETS['daily_pv'] in sheet_ids:
        requests.append(create_line_chart(
            sheet_id=sheet_ids[config.SHEETS['daily_pv']],
            title="📈 日別PV推移（全期間）",
            x_col=0,  # 日付
            y_cols=[1, 2],  # PV数, セッション数
            start_row=1,
            end_row=130,
            position_col=6
        ))

    # 2. 記事別PVグラフ（横棒）
    if config.SHEETS['article_performance'] in sheet_ids:
        requests.append(create_bar_chart(
            sheet_id=sheet_ids[config.SHEETS['article_performance']],
            title="📊 記事別PV数 TOP20",
            label_col=1,  # 記事タイトル
            value_col=2,  # PV数
            start_row=1,
            end_row=21,
            position_col=6
        ))

    # 3. 検索クエリグラフ（横棒）
    if config.SHEETS['search_queries'] in sheet_ids:
        requests.append(create_bar_chart(
            sheet_id=sheet_ids[config.SHEETS['search_queries']],
            title="🔍 検索クエリ TOP20",
            label_col=0,  # クエリ
            value_col=2,  # 表示回数
            start_row=1,
            end_row=21,
            position_col=6
        ))

    # 4. トレンド分析グラフ（折れ線 - クリック数と表示回数）
    if config.SHEETS['trends'] in sheet_ids:
        requests.append(create_line_chart(
            sheet_id=sheet_ids[config.SHEETS['trends']],
            title="📉 検索パフォーマンス推移（全期間）",
            x_col=0,  # 日付
            y_cols=[5, 6],  # クリック数, 表示回数
            start_row=1,
            end_row=130,
            position_col=10
        ))

    # バッチリクエスト実行
    if requests:
        body = {'requests': requests}
        spreadsheet.batch_update(body)
        print(f"✅ {len(requests)}個のグラフを作成しました")


def create_line_chart(sheet_id, title, x_col, y_cols, start_row, end_row, position_col):
    """折れ線グラフを作成"""
    series = []
    for y_col in y_cols:
        series.append({
            'series': {
                'sourceRange': {
                    'sources': [{
                        'sheetId': sheet_id,
                        'startRowIndex': start_row,
                        'endRowIndex': end_row,
                        'startColumnIndex': y_col,
                        'endColumnIndex': y_col + 1
                    }]
                }
            },
            'targetAxis': 'LEFT_AXIS'
        })

    return {
        'addChart': {
            'chart': {
                'spec': {
                    'title': title,
                    'basicChart': {
                        'chartType': 'LINE',
                        'legendPosition': 'BOTTOM_LEGEND',
                        'axis': [
                            {'position': 'BOTTOM_AXIS', 'title': '日付'},
                            {'position': 'LEFT_AXIS', 'title': '数値'}
                        ],
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': start_row,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': x_col,
                                        'endColumnIndex': x_col + 1
                                    }]
                                }
                            }
                        }],
                        'series': series,
                        'headerCount': 1
                    }
                },
                'position': {
                    'overlayPosition': {
                        'anchorCell': {
                            'sheetId': sheet_id,
                            'rowIndex': 1,
                            'columnIndex': position_col
                        },
                        'widthPixels': 600,
                        'heightPixels': 400
                    }
                }
            }
        }
    }


def create_bar_chart(sheet_id, title, label_col, value_col, start_row, end_row, position_col):
    """横棒グラフを作成"""
    return {
        'addChart': {
            'chart': {
                'spec': {
                    'title': title,
                    'basicChart': {
                        'chartType': 'BAR',
                        'legendPosition': 'NO_LEGEND',
                        'axis': [
                            {'position': 'BOTTOM_AXIS', 'title': ''},
                            {'position': 'LEFT_AXIS', 'title': ''}
                        ],
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': start_row,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': label_col,
                                        'endColumnIndex': label_col + 1
                                    }]
                                }
                            }
                        }],
                        'series': [{
                            'series': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': start_row,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': value_col,
                                        'endColumnIndex': value_col + 1
                                    }]
                                }
                            },
                            'targetAxis': 'BOTTOM_AXIS',
                            'color': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
                        }],
                        'headerCount': 1
                    }
                },
                'position': {
                    'overlayPosition': {
                        'anchorCell': {
                            'sheetId': sheet_id,
                            'rowIndex': 1,
                            'columnIndex': position_col
                        },
                        'widthPixels': 600,
                        'heightPixels': 500
                    }
                }
            }
        }
    }


if __name__ == '__main__':
    create_charts(config.SPREADSHEET_ID)
