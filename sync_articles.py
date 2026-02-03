"""
WordPress記事一覧をスプレッドシートに同期
WordPress REST APIを使用（SSH不要）
"""

import requests
import re
from datetime import datetime
import config
from auth import get_sheets_client


def get_wordpress_articles():
    """WordPress REST APIから全記事を取得"""
    base_url = "https://machiyomi-fudosan.com/wp-json/wp/v2/posts"
    all_posts = []
    page = 1

    while True:
        params = {
            'per_page': 100,
            'page': page,
            'status': 'publish',
            '_fields': 'id,title,date,link,slug,content,categories'
        }
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            break

        posts = response.json()
        if not posts:
            break

        all_posts.extend(posts)
        page += 1

        # 全ページ取得したか確認
        total_pages = int(response.headers.get('X-WP-TotalPages', 1))
        if page > total_pages:
            break

    return all_posts


def get_categories():
    """カテゴリID→名前のマッピングを取得"""
    url = "https://machiyomi-fudosan.com/wp-json/wp/v2/categories"
    params = {'per_page': 100}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return {cat['id']: cat['name'] for cat in response.json()}
    return {}


def count_links(content):
    """記事本文から内部リンク・外部リンク・画像を数える"""
    internal = len(re.findall(r'href="https://machiyomi-fudosan\.com[^"]*"', content))
    all_links = len(re.findall(r'href="https?://[^"]*"', content))
    external = all_links - internal
    images = len(re.findall(r'<img[^>]*>', content))
    return internal, external, images


def sync_articles():
    """記事一覧シートを更新"""
    print("[記事同期] WordPress REST APIから記事取得中...")
    posts = get_wordpress_articles()
    print(f"  → {len(posts)}件取得")

    categories = get_categories()

    # 記事データを整形
    articles = []
    for post in posts:
        content = post.get('content', {}).get('rendered', '')
        internal, external, images = count_links(content)

        # カテゴリ名を取得
        cat_ids = post.get('categories', [])
        cat_names = [categories.get(cid, '') for cid in cat_ids if cid in categories]
        cat_str = ', '.join(cat_names) if cat_names else '(なし)'

        articles.append({
            'ID': str(post['id']),
            'タイトル': post['title']['rendered'].replace('&#8211;', '–').replace('&#8230;', '…').replace('&amp;', '&'),
            'ステータス': '公開',
            'リンク': post['link'],
            '日付': post['date'].replace('T', ' '),
            'カテゴリ': cat_str,
            'スラッグ': post['slug'],
            '内': str(internal),
            '外': str(external),
            'アイ': '有',  # REST APIでは判定難しいので仮
            '画': str(images),
        })

    # 日付でソート（古い順）
    articles.sort(key=lambda x: x['日付'])

    # スプレッドシートに書き込み
    print("[記事同期] スプレッドシート更新中...")
    client = get_sheets_client()
    spreadsheet = client.open_by_key(config.SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet('記事一覧')

    # 既存データを取得してメタディ・推奨リンクを保持
    existing_data = worksheet.get_all_values()
    existing_meta = {}
    if len(existing_data) > 1:
        header = existing_data[0]
        for row in existing_data[1:]:
            if len(row) > 14:
                existing_meta[row[0]] = {
                    'メタディ': row[12] if len(row) > 12 else '',
                    '推奨リンク': row[14] if len(row) > 14 else ''
                }

    # 15列フォーマットで行を作成
    header = ['ID', 'No,', 'タイトル', 'ステータス', 'リンク', '日付', 'カテゴリ', 'タグ', '内', '外', 'アイ', '画', 'メタディ', 'スラッグ', '推奨リンク']
    rows = [header]

    for i, art in enumerate(articles, 1):
        # 既存のメタディ・推奨リンクを保持
        meta = existing_meta.get(art['ID'], {'メタディ': '', '推奨リンク': ''})

        row = [
            art['ID'],
            str(i),
            art['タイトル'],
            art['ステータス'],
            art['リンク'],
            art['日付'],
            art['カテゴリ'],
            '(なし)',
            art['内'],
            art['外'],
            art['アイ'],
            art['画'],
            meta['メタディ'],
            art['スラッグ'],
            meta['推奨リンク']
        ]
        rows.append(row)

    # シートを更新（記事一覧シートのみ）
    worksheet.clear()
    worksheet.update('A1', rows, value_input_option='RAW')

    print(f"✅ 記事一覧を更新しました（{len(articles)}件）")
    print(f"   最古: {articles[0]['日付'][:10]} - {articles[0]['タイトル'][:25]}...")
    print(f"   最新: {articles[-1]['日付'][:10]} - {articles[-1]['タイトル'][:25]}...")


if __name__ == '__main__':
    sync_articles()
