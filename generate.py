import requests
import datetime
import urllib.parse

URL = 'https://graphql.anilist.co'
query = '''
query ($page: Int, $perPage: Int) {
  Page (page: $page, perPage: $perPage) {
    media (status: RELEASING, format: TV, sort: POPULARITY_DESC) {
      id
      title { native, romaji }
      coverImage { large }
      nextAiringEpisode { airingAt, episode }
    }
  }
}
'''

def get_anime_data():
    variables = {'page': 1, 'perPage': 50}
    response = requests.post(URL, json={'query': query, 'variables': variables})
    return response.json()['data']['Page']['media']

def generate_html(anime_list):
    days_map = {0: "月曜日", 1: "火曜日", 2: "水曜日", 3: "木曜日", 4: "金曜日", 5: "土曜日", 6: "日曜日"}
    organized_data = {day: [] for day in days_map.values()}
    
    for anime in anime_list:
        # 日本語と英語の両方のタイトルを取得
        native = anime['title']['native']
        romaji = anime['title']['romaji']
        
        if anime['nextAiringEpisode']:
            dt = datetime.datetime.fromtimestamp(anime['nextAiringEpisode']['airingAt'], datetime.timezone(datetime.timedelta(hours=9)))
            organized_data[days_map[dt.weekday()]].append({
                "native": native,
                "romaji": romaji,
                "thumb": anime['coverImage']['large']
            })

    html = """<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>Anime Schedule</title><style>
        body { background: #0b0e14; color: #fff; font-family: sans-serif; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }
        .card { background: #1a202c; border-radius: 10px; overflow: hidden; text-align: center; border: 1px solid #2d3748; transition: 0.3s; }
        .card:hover { border-color: #63b3ed; transform: translateY(-5px); }
        .card img { width: 100%; height: 250px; object-fit: cover; }
        .card p { padding: 10px; font-size: 0.9em; margin: 0; }
        a { color: inherit; text-decoration: none; }
    </style></head><body><h1>放送中のアニメ (Nyaa.si リンク)</h1>"""
    
    for day, animes in organized_data.items():
        if not animes: continue
        html += f"<h2>{day}</h2><div class='grid'>"
        for a in animes:
            # 検索ワードを (英語名)|(日本語名) の形式に。
            # c=0_0 に変更して全カテゴリ（アニメ全体）を対象にする。
            search_query = f'("{a["romaji"]}")|("{a["native"]}")'
            url = f"https://nyaa.si/?f=0&c=0_0&q={urllib.parse.quote(search_query)}"
            
            html += f'''<div class="card">
                <a href="{url}" target="_blank">
                    <img src="{a["thumb"]}">
                    <p>{a["native"]}</p>
                </a>
            </div>'''
        html += "</div>"
    
    html += "</body></html>"
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generate_html(get_anime_data())
