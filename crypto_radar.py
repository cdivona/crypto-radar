import requests
import statistics
from datetime import datetime

# =========================
# CONFIG (RELLENA ESTO)
# =========================
TELEGRAM_TOKEN = "8799458763:AAHVaMqSdw_wz1qumRuTxG_jiAVwWjTMn1g"
CHAT_ID = "1751107577"

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "PEGA_AQUI_TU_TOKEN"
CHAT_ID = "PEGA_AQUI_TU_CHAT_ID"

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
# TIME
# =========================
now = datetime.utcnow()
current_hour = now.hour

# =========================
# PRICE DATA
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
# HISTORY
# =========================
def get_history(coin_id, days=250):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    data = requests.get(url, params=params).json()
    return [p[1] for p in data["prices"]]

btc_hist = get_history("bitcoin", 250)
eth_hist = get_history("ethereum", 250)

# =========================
# RSI
# =========================
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

btc_rsi = compute_rsi(btc_hist)
eth_rsi = compute_rsi(eth_hist)

# =========================
# MOVING AVERAGES
# =========================
def moving_average(prices, period):
    return statistics.mean(prices[-period:])

btc_ma50 = moving_average(btc_hist, 50)
btc_ma200 = moving_average(btc_hist, 200)

# =========================
# WEEK / MONTH MOMENTUM
# =========================
btc_week = (btc_hist[-1] / btc_hist[-8] - 1) * 100
eth_week = (eth_hist[-1] / eth_hist[-8] - 1) * 100
btc_30d = (btc_hist[-1] / btc_hist[-31] - 1) * 100

# ============================================================
# 🔥 RISK SCORE (EUFORIA / TECHO)
# ============================================================
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

# ============================================================
# ❄️ DOWNSIDE RISK (MERCADO ROMPIENDOSE)
# ============================================================
downside = 0
down_signals = []

if btc < btc_ma200:
    downside += 30
    down_signals.append("⚠️ BTC bajo MA200")

if btc < btc_ma50:
    downside += 15
    down_signals.append("📉 BTC bajo MA50")

if btc_rsi < 40:
    downside += 20
    down_signals.append(f"RSI débil {btc_rsi}")

if btc_week < -10:
    downside += 25
    down_signals.append(f"🔻 BTC {btc_week:.1f}% semanal")

downside = min(downside, 100)

# ============================================================
# 🧭 MARKET REGIME
# ============================================================
if btc > btc_ma200 and downside < 40:
    regime = "🟢 BULL TREND"
elif downside >= 60:
    regime = "🔴 BEARISH SHIFT"
else:
    regime = "🟡 NEUTRAL"

# ============================================================
# 🔥 CYCLE TOP MODEL
# ============================================================
extension = (btc - btc_ma200) / btc_ma200 * 100

cycle_score = 0
cycle_signals = []

if extension > 60:
    cycle_score += 20
    cycle_signals.append(f"📈 +{extension:.0f}% sobre MA200")

if extension > 80:
    cycle_score += 20

if btc_rsi > 78:
    cycle_score += 20
    cycle_signals.append(f"🔥 RSI extremo {btc_rsi}")

if btc_30d > 40:
    cycle_score += 20
    cycle_signals.append(f"🚀 +{btc_30d:.0f}% en 30d")

if risk >= 75:
    cycle_score += 20

cycle_score = min(cycle_score, 100)

if cycle_score >= 70:
    cycle_status = "🚨 ALTA PROBABILIDAD DE TECHO"
elif cycle_score >= 40:
    cycle_status = "⚠️ POSIBLE DISTRIBUCION"
else:
    cycle_status = "🟢 Ciclo saludable"

# ============================================================
# 🚨 PRICE ALERTS
# ============================================================
alerts = []

if btc > 75000:
    alerts.append(f"🚨 BTC > 75k (${btc:,.0f})")

if eth > 2500:
    alerts.append(f"🚨 ETH > 2.5k (${eth:,.0f})")

if sol > 140:
    alerts.append(f"🚨 SOL > 140 (${sol:,.0f})")

# ============================================================
# 📊 BASE MESSAGE
# ============================================================
base_message = (
    "📊 CRYPTO RADAR PRO\n\n"
    f"BTC: ${btc:,.0f} | RSI {btc_rsi}\n"
    f"ETH: ${eth:,.0f} | RSI {eth_rsi}\n"
    f"XRP: ${xrp:,.2f}\n"
    f"SOL: ${sol:,.0f}\n\n"
    f"Market Regime: {regime}\n"
    f"Risk Score: {risk}/100\n"
    f"Downside Risk: {downside}/100\n"
    f"Cycle Top Score: {cycle_score}/100\n"
    f"{cycle_status}"
)

# ============================================================
# 📩 SEND LOGIC
# ============================================================

# ALERTAS PRIORITARIAS
if alerts:
    send_telegram(
        base_message
        + "\n\n"
        + "\n".join(alerts)
        + ("\n\n" + "\n".join(cycle_signals) if cycle_signals else "")
        + ("\n\n" + "\n".join(down_signals) if down_signals else "")
    )

# REPORTE DIARIO 11:00 UTC
elif current_hour == 11:
    send_telegram(base_message)
