import requests

# === CONFIG ===
TELEGRAM_TOKEN = "8799458763:AAG--SoRpvskDLeMZcLwqeYwINC7CD-zgYA"
CHAT_ID = "1751107577"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

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

alert = ""

if btc > 80000:
    alert += f"🚨 BTC alto: ${btc}\n"

if eth > 4500:
    alert += f"🚨 ETH alto: ${eth}\n"

if xrp > 1.5:
    alert += f"🚨 XRP alto: ${xrp}\n"

if alert:
    send_telegram("CRYPTO RADAR PRO\n\n" + alert)
else:
    print("Sin alertas.")
