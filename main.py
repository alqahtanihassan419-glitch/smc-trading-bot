import pandas as pd
from polygon import RESTClient
import requests
import time
import os
from threading import Thread
from flask import Flask # أضفنا هذا لإرضاء السيرفر المجاني

# --- جزء الوهم للسيرفر المجاني ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=os.getenv("PORT", 8080))
# ------------------------------

POLYGON_KEY = os.getenv("POLYGON_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
client = RESTClient(POLYGON_KEY)

def check_strategy(symbol):
    try:
        aggs = list(client.get_aggs(symbol, 5, "minute", "2026-04-01", "2026-04-03"))
        df = pd.DataFrame(aggs)
        c1, c2, c3, c4 = df.iloc[-4], df.iloc[-3], df.iloc[-2], df.iloc[-1]
        bullish = (c1['h'] < c2['h'] and c4['c'] > c2['h']) and (c2['h'] < c4['l'])
        bearish = (c1['l'] > c2['l'] and c4['c'] < c2['l']) and (c2['l'] > c4['h'])
        if bullish: return "CALL 🚀", c4['c']
        if bearish: return "PUT 📉", c4['c']
        return None, None
    except: return None, None

def send_alert(symbol, side, price):
    emoji = "🟡" if "XAU" in symbol else "📦"
    msg = (
        f"🤖 **روبوت سباكس - SMC PRO**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"إشارة جديدة مكتملة الشروط 🔥\n\n"
        f"{emoji} **الأصل:** {symbol}\n"
        f"方向 **النوع:** {side}\n"
        f"💵 **السعر:** ${price:.2f}\n"
        f"🛡️ **التأكيد:** Breaker Block ✅\n"
        f"━━━━━━━━━━━━━━━"
    )
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def bot_loop():
    print("🛰️ البوت بدأ مراقبة الأسهم والذهب...")
    while True:
        for s in ["SPY", "QQQ", "NVDA", "C:XAUUSD"]:
            side, price = check_strategy(s)
            if side: send_alert(s, side, price)
        time.sleep(300)

if __name__ == "__main__":
    # تشغيل الوهم وتشغيل البوت مع بعض
    Thread(target=run_web).start()
    bot_loop()
