import requests
import statistics
from datetime import datetime

# =========================
# CONFIG (RELLENA ESTO)
# =========================
TELEGRAM_TOKEN = "8799458763:AAHVaMqSdw_wz1qumRuTxG_jiAVwWjTMn1g"
CHAT_ID = "1751107577"

# =========================
# TELEGRAM
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# =========================
# HORA ACTUAL (UTC)
# =========================
now = datetime.utcnow()
current_hour = now.hour

# =========================
# PRECIOS
# =========================
price_url = "https://api.coingecko.com/api/v3/simple/price"
price_params = {
    "ids": "bitcoin,ethereum,ripple,solana",
    "vs_currencies": "usd"
}
price_data = requests.get(price_url, params=price_params).json()

btc = price_data["bitcoin"]["usd"]
eth = price_data["ethereum"]["usd"]
xrp = price_data["ripple"]["usd"]
sol = price_data["solana"]["usd"]

# =========================
# HISTORICO
# =========================
def get_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "14"}
    data = requests.get(url, params=params).json()
    return [p[1] for p in data["prices"]]

def compute_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))
    avg_gain = statistics.mean(gains[-period:])
    avg_loss = statistics.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)

btc_hist = get_history("bitcoin")
eth_hist = get_history("ethereum")

btc_rsi = compute_rsi(btc_hist)
eth_rsi = compute_rsi(eth_hist)

btc_week = (btc_hist[-1] / btc_hist[-8] - 1) * 100
eth_week = (eth_hist[-1] / eth_hist[-8] - 1) * 100

# =========================
# RISK SCORE
# =========================
risk = 0

if btc_rsi > 70:
    risk += 25
if btc_rsi > 80:
    risk += 15
if eth_rsi > 70:
    risk += 15
if btc_week > 15:
    risk += 20
if eth_week > 20:
    risk += 10
if btc > 75000:
    risk += 10
if eth > 2500:
    risk += 5

risk = min(risk, 100)

# =========================
# ALERTAS
# =========================
alerts = []

if btc > 75000:
    alerts.append(f"🚨 BTC > 75k (${btc:,.0f})")

if eth > 2500:
    alerts.append(f"🚨 ETH > 2.5k (${eth:,.0f})")

if sol > 140:
    alerts.append(f"🚨 SOL > 140 (${sol:,.0f})")

if btc_rsi > 75:
    alerts.append(f"⚠️ BTC RSI extremo: {btc_rsi}")

if eth_rsi > 75:
    alerts.append(f"⚠️ ETH RSI extremo: {eth_rsi}")

if btc_week > 15:
    alerts.append(f"📈 BTC +{btc_week:.1f}% semanal")

# =========================
# REGIMEN
# =========================
if risk >= 70:
    regime = "🔥 POSIBLE TECHO DE CICLO"
elif risk >= 40:
    regime = "🟡 RIESGO MEDIO"
else:
    regime = "🟢 NORMAL"

# =========================
# MENSAJE BASE
# =========================
base_message = (
    "📊 CRYPTO DAILY REPORT\n\n"
    f"BTC: ${btc:,.0f} | RSI {btc_rsi}\n"
    f"ETH: ${eth:,.0f} | RSI {eth_rsi}\n"
    f"XRP: ${xrp:,.2f}\n"
    f"SOL: ${sol:,.0f}\n\n"
    f"Risk Score: {risk}/100\n"
    f"{regime}"
)

# =========================
# ENVIO
# =========================
# ALERTAS INMEDIATAS
if alerts:
    send_telegram(base_message + "\n\n" + "\n".join(alerts))

# REPORTE DIARIO A LAS 11:00 UTC
elif current_hour == 11:
    send_telegram(base_message)
