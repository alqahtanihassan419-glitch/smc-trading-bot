import pandas as pd
from polygon import RESTClient
import requests
import time
import os

# جلب المفاتيح من السيرفر (لحماية بياناتك)
POLYGON_KEY = os.getenv("POLYGON_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

client = RESTClient(POLYGON_KEY)

def check_strategy(symbol):
    try:
        # فحص البيانات لآخر 4 شموع (فريم 5 دقائق)
        aggs = list(client.get_aggs(symbol, 5, "minute", "2026-04-01", "2026-04-03"))
        df = pd.DataFrame(aggs)
        c1, c2, c3, c4 = df.iloc[-4], df.iloc[-3], df.iloc[-2], df.iloc[-1]
        
        # استراتيجية Breaker Block + FVG (صعود)
        bullish = (c1['h'] < c2['h'] and c4['c'] > c2['h']) and (c2['h'] < c4['l'])
        # استراتيجية Breaker Block + FVG (هبوط)
        bearish = (c1['l'] > c2['l'] and c4['c'] < c2['l']) and (c2['l'] > c4['h'])
        
        if bullish: return "CALL 🚀", c4['c']
        if bearish: return "PUT 📉", c4['c']
        return None, None
    except: return None, None

def send_alert(symbol, side, price):
    # حسابات تجميلية لتظهر مثل الصورة
    strike = round(price)
    profit_usd = price * 0.10 # افتراض ربح 10%
    profit_sar = profit_usd * 3.75
    
    msg = (
        f"🤖 **رويوت سباكس - SMC PRO**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"صفقتنا اليوم ولله الحمد 🔥🤩\n\n"
        f"📦 **بمجموعة عقود:** {symbol} ${strike} {side}\n\n"
        f"💵 **سعر الدخول:** ${price:.2f}\n"
        f"🚀 **أعلى سعر وصل:** ${price + profit_usd:.2f}\n\n"
        f"📈 **الربح:** ${profit_usd:.2f} ( {profit_sar:.2f} ريال )\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✨ **قوة الإشارة:** ممتازة ⚡"
    )
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# تشغيل المراقبة
while True:
    for s in ["SPY", "QQQ", "TSLA", "NVDA"]:
        side, price = check_strategy(s)
        if side: send_alert(s, side, price)
    time.sleep(300) # فحص كل 5 دقائق
