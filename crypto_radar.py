import requests

# =========================
# CONFIG (RELLENA ESTO)
# =========================
TELEGRAM_TOKEN = "8799458763:AAHVaMqSdw_wz1qumRuTxG_jiAVwWjTMn1g"
CHAT_ID = "1751107577"

# =========================
# FUNCION TELEGRAM
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

# =========================
# TEST FORZADO (IMPORTANTE)
# =========================
send_telegram("🚨 TEST RADAR — si ves esto, Telegram funciona")

# =========================
# OBTENER PRECIOS
# =========================
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": "bitcoin,ethereum,ripple",
    "vs_currencies": "usd"
}

response = requests.get(url, params=params)
data = response.json()

btc = data["bitcoin"]["usd"]
eth = data["ethereum"]["usd"]
xrp = data["ripple"]["usd"]

print("Precios actuales:")
print("BTC:", btc)
print("ETH:", eth)
print("XRP:", xrp)
