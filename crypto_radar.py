import requests
import statistics

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
# OBTENER PRECIOS ACTUALES
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
# OBTENER HISTORICO (RSI + semanal)
# =========================
def get_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "14"}
    data = requests.get(url, params=params).json()
    prices = [p[1] for p in data["prices"]]
    return prices

def compute_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    avg_gain = statistics.mean(gains[-period:])
    avg_loss = statistics.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

# =========================
# CALCULOS
# =========================
btc_hist = get_history("bitcoin")
eth_hist = get_history("ethereum")

btc_rsi = compute_rsi(btc_hist)
eth_rsi = compute_rsi(eth_hist)

btc_week_change = (btc_hist[-1] / btc_hist[-8] - 1) * 100
eth_week_change = (eth_hist[-1] / eth_hist[-8] - 1) * 100

# =========================
# SCORE DE RIESGO
# =========================
risk = 0

# RSI
if btc_rsi and btc_rsi > 70:
    risk += 25
if btc_rsi and btc_rsi > 80:
    risk += 15

if eth_rsi and eth_rsi > 70:
    risk += 15

# subida semanal
if btc_week_change > 15:
    risk += 20
if eth_week_change > 20:
    risk += 10

# precios extendidos
if btc > 75000:
    risk += 10
if eth > 2500:
    risk += 5

risk = min(risk, 100)

# =========================
# MENSAJE
# =========================
alerts = []

# precios objetivo
if btc > 75000:
    alerts.append(f"🚨 BTC > 75k (${btc:,.0f})")

if eth > 2500:
    alerts.append(f"🚨 ETH > 2.5k (${eth:,.0f})")

if sol > 140:
    alerts.append(f"🚨 SOL > 140 (${sol:,.0f})")

# RSI extremo
if btc_rsi and btc_rsi > 75:
    alerts.append(f"⚠️ BTC RSI extremo: {btc_rsi}")

if eth_rsi and eth_rsi > 75:
    alerts.append(f"⚠️ ETH RSI extremo: {eth_rsi}")

# subida fuerte
if btc_week_change > 15:
    alerts.append(f"📈 BTC +{btc_week_change:.1f}% semanal")

if eth_week_change > 20:
    alerts.append(f"📈 ETH +{eth_week_change:.1f}% semanal")

# =========================
# SEÑAL DE TECHO
# =========================
if risk >= 70:
    regime = "🔥 POSIBLE TECHO DE CICLO"
elif risk >= 40:
    regime = "🟡 RIESGO MEDIO"
else:
    regime = "🟢 NORMAL"

# =========================
# ENVIAR SOLO SI HAY ALGO
# =========================
if alerts or risk >= 60:
    message = (
        "🚨 CRYPTO RADAR PRO\n\n"
        f"BTC: ${btc:,.0f} | RSI {btc_rsi}\n"
        f"ETH: ${eth:,.0f} | RSI {eth_rsi}\n"
        f"XRP: ${xrp:,.2f}\n"
        f"SOL: ${sol:,.0f}\n\n"
        f"Risk Score: {risk}/100\n"
        f"{regime}\n\n"
        + "\n".join(alerts)
    )
    send_telegram(message)
