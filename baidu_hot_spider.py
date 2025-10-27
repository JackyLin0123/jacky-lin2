"""
Baidu 热搜 Top10 爬虫 + 存入 MySQL
"""
import requests, datetime
from bs4 import BeautifulSoup
from mysql_helper import MySqlHelper

DB = dict(host="127.0.0.1", user="root", password="NewStrong_2025#", database="learn_db")

def fetch_json():
    url = "https://top.baidu.com/api/board?platform=pc&tab=realtime"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        contents = []
        for c in data["data"]["cards"][0]["content"][:10]:
            title = c["word"]
            heat = str(c.get("hotScore", ""))
            desc = c.get("desc", "")
            link = f"https://www.baidu.com/s?wd={title}"
            contents.append(dict(rank_no=len(contents)+1, title=title, heat=heat, url=link, summary=desc))
        return contents
    except Exception:
        return []

def fetch_html():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "lxml")
    items = []
    blocks = soup.select("div.category-wrap_iQLoo")[:10]
    for i, blk in enumerate(blocks, start=1):
        title = blk.select_one(".c-single-text-ellipsis").text.strip()
        link = blk.select_one("a")["href"]
        heat = blk.select_one(".hot-index_1Bl1a").text.strip()
        desc = blk.select_one(".hot-desc_1m_jR")
        desc = desc.text.strip() if desc else ""
        items.append(dict(rank_no=i, title=title, heat=heat, url=link, summary=desc))
    return items

def save_to_db(items):
    helper = MySqlHelper(**DB)
    today = datetime.date.today()
    sql = """
    INSERT INTO baidu_hot (rank_no, title, heat, url, summary, snapshot_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      title=VALUES(title), heat=VALUES(heat), url=VALUES(url), summary=VALUES(summary)
    """
    data = [(i['rank_no'], i['title'], i['heat'], i['url'], i['summary'], today) for i in items]
    helper.executemany(sql, data)
    print(f"[OK] 写入 {len(items)} 条记录。")

def main():
    print("正在爬取百度热搜 Top10...")
    items = fetch_json() or fetch_html()
    if not items:
        print("❌ 获取失败，请检查网络或页面结构。")
        return
    save_to_db(items)
    helper = MySqlHelper(**DB)
    rows = helper.query("SELECT rank_no,title,heat FROM baidu_hot WHERE snapshot_date=%s ORDER BY rank_no", (datetime.date.today(),))
    for r in rows:
        print(f"{r['rank_no']:>2}. {r['title']} ({r['heat']})")

if __name__ == "__main__":
    main()
