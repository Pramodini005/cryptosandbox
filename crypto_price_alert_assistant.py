import requests
import time
import smtplib
from email.mime.text import MIMEText

# --- Configuration ---
COIN_ID = "bitcoin"  # CoinGecko coin id, e.g. 'bitcoin'
CURRENCY = "usd"
PRICE_THRESHOLD = 40000  # Alert if price crosses this value
CHECK_INTERVAL = 60  # seconds

EMAIL_FROM = "pramodinivgoudar@gmail.com"
EMAIL_TO = "ranjitapm123@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "pramodinivgoudar@gmail.com"
SMTP_PASSWORD = "abcd efgh unuz arwy"  # Use app password for Gmail (not your real password)

# --- Core Logic ---
def get_current_price(coin_id, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data[coin_id][currency]

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def main():
    print(f"Monitoring {COIN_ID} price every {CHECK_INTERVAL} seconds...")
    while True:
        try:
            price = get_current_price(COIN_ID, CURRENCY)
            print(f"Current {COIN_ID} price: {price} {CURRENCY}")
            if price >= PRICE_THRESHOLD:
                subject = f"Crypto Alert: {COIN_ID.title()} price reached {price} {CURRENCY}"
                body = f"The price of {COIN_ID.title()} is now {price} {CURRENCY}."
                send_email(subject, body)
                print("Alert sent! Exiting.")
                break  # Stop monitoring after alert
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()