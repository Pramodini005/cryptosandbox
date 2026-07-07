# streamlit_app.py
import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
import time

# --- Functions ---
def get_current_price(coin_id, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data[coin_id][currency]

def send_email(subject, body, email_from, email_to, smtp_user, smtp_password, smtp_server, smtp_port):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(email_from, email_to, msg.as_string())

# --- Streamlit UI ---
st.title("📈 Crypto Price Alert Assistant")

st.sidebar.header("Settings")
coin_id = st.sidebar.text_input("CoinGecko Coin ID", "bitcoin")
currency = st.sidebar.text_input("Currency", "usd")
price_threshold = st.sidebar.number_input("Alert Price Threshold", value=40000)
check_interval = st.sidebar.number_input("Check Interval (seconds)", value=60, min_value=10)

st.sidebar.header("Email Settings")
email_from = st.sidebar.text_input("From Email", "your_email@gmail.com")
email_to = st.sidebar.text_input("To Email", "recipient_email@gmail.com")
smtp_user = st.sidebar.text_input("SMTP Username", email_from)
smtp_password = st.sidebar.text_input("SMTP Password (App Password)", type="password")
smtp_server = st.sidebar.text_input("SMTP Server", "smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=587)

status_placeholder = st.empty()  # placeholder for updating price

if st.button("Start Monitoring"):
    st.success(f"Monitoring {coin_id.title()} price...")
    try:
        alert_sent = False
        while not alert_sent:
            price = get_current_price(coin_id, currency)
            status_placeholder.write(f"Current {coin_id.title()} price: {price} {currency}")
            
            if price >= price_threshold:
                subject = f"Crypto Alert: {coin_id.title()} price reached {price} {currency}"
                body = f"The price of {coin_id.title()} is now {price} {currency}."
                send_email(subject, body, email_from, email_to, smtp_user, smtp_password, smtp_server, smtp_port)
                status_placeholder.success(f"⚡ Price threshold reached! Email sent to {email_to}")
                alert_sent = True
            time.sleep(check_interval)
    except Exception as e:
        status_placeholder.error(f"Error: {e}")
