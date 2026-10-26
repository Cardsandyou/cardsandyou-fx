"""每天抓臺灣銀行美元即期匯率（本行買入／賣出取平均），輸出 fx.json。

臺灣銀行 CSV：https://rate.bot.com.tw/xrt/flcsv/0/day
欄位：前半段為「本行買入」，後半段為「本行賣出」，各有一欄「即期」。
假日或非營業時間，臺灣銀行會維持最後一次掛牌的匯率，這裡照樣記錄並附上掛牌時間。
"""
import csv, io, json, re, sys, urllib.request
from datetime import datetime, timezone, timedelta

URL = 'https://rate.bot.com.tw/xrt/flcsv/0/day'
BACKUP_URL = 'https://open.er-api.com/v6/latest/USD'  # Rates By Exchange Rate API: https://www.exchangerate-api.com
TW = timezone(timedelta(hours=8))

def from_bot():
    """主要來源：臺灣銀行即期匯率（本行買入／賣出平均）"""
    req = urllib.request.Request(URL, headers={'User-Agent': 'cardsandyou-fx-updater'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8-sig')
        disp = resp.headers.get('Content-Disposition', '')
    rows = list(csv.reader(io.StringIO(raw)))
    header = [h.strip() for h in rows[0]]
    spot = [i for i, h in enumerate(header) if h == '即期']
    if len(spot) < 2:
        raise ValueError('找不到「即期」欄位，臺灣銀行 CSV 格式可能改變了')
    usd = next((r for r in rows[1:] if r and r[0].strip() == 'USD'), None)
    if not usd:
        raise ValueError('CSV 中找不到 USD')
    buy, sell = float(usd[spot[0]]), float(usd[spot[1]])
    if not (20 < buy < 50 and 20 < sell < 50):
        raise ValueError(f'匯率數值異常：{buy} / {sell}')
    # 掛牌時間：檔名通常是 ExchangeRate@YYYYMMDDHHMM.csv
    m = re.search(r'@(\d{12})', disp)
    posted = (datetime.strptime(m.group(1), '%Y%m%d%H%M').strftime('%Y/%m/%d %H:%M')
              if m else datetime.now(TW).strftime('%Y/%m/%d %H:%M') + '（抓取時間）')
    return {'buy': buy, 'sell': sell, 'mid': round((buy + sell) / 2, 4),
            'posted': posted, 'source': '臺灣銀行即期匯率'}


def from_backup():
    """備援來源：臺灣銀行網站連不上時才使用（ExchangeRate-API 開放版，每日更新一次的中間價）"""
    req = urllib.request.Request(BACKUP_URL, headers={'User-Agent': 'cardsandyou-fx-updater'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.load(resp)
    mid = float(d['rates']['TWD'])
    if not 20 < mid < 50:
        raise ValueError(f'備援匯率數值異常：{mid}')
    posted = datetime.fromtimestamp(d['time_last_update_unix'], TW).strftime('%Y/%m/%d %H:%M')
    return {'buy': None, 'sell': None, 'mid': round(mid, 4), 'posted': posted,
            'source': '備援：ExchangeRate-API（臺灣銀行暫時無法取得）'}


try:
    data = from_bot()
except Exception as e:
    print('臺灣銀行抓取失敗，改用備援來源：', e)
    data = from_backup()

data = {'pair': 'USD/TWD', **data, 'fetched': datetime.now(TW).strftime('%Y/%m/%d %H:%M')}
with open('fx.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(data)
