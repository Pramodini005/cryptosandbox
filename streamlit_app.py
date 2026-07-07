import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import asyncio
import websocket
import threading
from datetime import datetime, timedelta
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Crypto Price Alert Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .alert-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    
    .success-alert {
        border-left: 4px solid #28a745;
        background: #d4edda;
    }
    
    .warning-alert {
        border-left: 4px solid #ffc107;
        background: #fff3cd;
    }
    
    .danger-alert {
        border-left: 4px solid #dc3545;
        background: #f8d7da;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'prices' not in st.session_state:
    st.session_state.prices = {}
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"holdings": [], "total_value": 0.0}

# Helper functions
@st.cache_data(ttl=60)
def get_supported_coins():
    """Get supported cryptocurrencies"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/coins")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

@st.cache_data(ttl=30)
def get_current_prices(symbols):
    """Get current prices for symbols"""
    try:
        symbols_str = ",".join(symbols)
        response = requests.get(f"{API_BASE_URL}/api/prices?symbols={symbols_str}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

@st.cache_data(ttl=300)
def get_chart_data(symbol, days=7):
    """Get chart data for a symbol"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/chart/{symbol}?days={days}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

@st.cache_data(ttl=1800)
def get_market_sentiment():
    """Get market sentiment"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/market-sentiment")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def get_price_predictions(symbol):
    """Get AI price predictions"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/predictions/{symbol}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def create_alert(symbol, condition, target_price):
    """Create a new alert"""
    try:
        alert_data = {
            "symbol": symbol,
            "condition": condition,
            "target_price": target_price
        }
        response = requests.post(f"{API_BASE_URL}/api/alerts", json=alert_data)
        return response.status_code == 200
    except:
        return False

def create_smart_alert(symbol, alert_type, parameters):
    """Create a smart alert"""
    try:
        alert_data = {
            "symbol": symbol,
            "type": alert_type,
            "parameters": parameters
        }
        response = requests.post(f"{API_BASE_URL}/api/smart-alerts", json=alert_data)
        return response.status_code == 200
    except:
        return False

def get_alerts():
    """Get all alerts"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/alerts")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_smart_alerts():
    """Get smart alerts"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/smart-alerts")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def delete_alert(alert_id):
    """Delete an alert"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/alerts/{alert_id}")
        return response.status_code == 200
    except:
        return False

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Crypto Price Alert Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Real-time Cryptocurrency Monitoring & Smart Alerts")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["📊 Dashboard", "🔔 Alerts", "🤖 Smart Alerts", "📈 Analytics", "💼 Portfolio", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        
        # Get market sentiment
        sentiment = get_market_sentiment()
        if sentiment:
            sentiment_score = sentiment.get("overall_score", 50)
            sentiment_label = sentiment.get("sentiment", "Neutral")
            
            # Color based on sentiment
            if sentiment_score >= 70:
                color = "#28a745"  # Green
            elif sentiment_score >= 40:
                color = "#ffc107"  # Yellow
            else:
                color = "#dc3545"  # Red
            
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                <h3>Market Sentiment</h3>
                <h2>{sentiment_score:.1f}/100</h2>
                <p>{sentiment_label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Active alerts count
        alerts = get_alerts()
        smart_alerts = get_smart_alerts()
        total_alerts = len(alerts) + len(smart_alerts)
        
        st.metric("Active Alerts", total_alerts)
        
        st.markdown("---")
        
        # Real-time updates toggle
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)", value=True)
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Main content based on selected page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔔 Alerts":
        show_alerts()
    elif page == "🤖 Smart Alerts":
        show_smart_alerts()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "💼 Portfolio":
        show_portfolio()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Main dashboard view"""
    st.markdown("## 📊 Real-time Dashboard")
    
    # Top cryptocurrencies
    coins = get_supported_coins()
    if coins:
        top_coins = coins[:10]  # Top 10 by market cap
        symbols = [coin["id"] for coin in top_coins]
        prices = get_current_prices(symbols)
        
        # Create metrics grid
        cols = st.columns(5)
        for i, coin in enumerate(top_coins[:5]):
            with cols[i]:
                symbol = coin["id"]
                if symbol in prices:
                    price_data = prices[symbol]
                    current_price = price_data["current_price"]
                    change_24h = price_data["price_change_24h"]
                    
                    # Color based on change
                    color = "#28a745" if change_24h >= 0 else "#dc3545"
                    arrow = "↗️" if change_24h >= 0 else "↘️"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{coin["symbol"].upper()}</h4>
                        <h3>${current_price:,.4f}</h3>
                        <p style="color: white;">{arrow} {change_24h:+.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Second row
        cols = st.columns(5)
        for i, coin in enumerate(top_coins[5:10]):
            with cols[i]:
                symbol = coin["id"]
                if symbol in prices:
                    price_data = prices[symbol]
                    current_price = price_data["current_price"]
                    change_24h = price_data["price_change_24h"]
                    
                    # Color based on change
                    color = "#28a745" if change_24h >= 0 else "#dc3545"
                    arrow = "↗️" if change_24h >= 0 else "↘️"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{coin["symbol"].upper()}</h4>
                        <h3>${current_price:,.4f}</h3>
                        <p style="color: white;">{arrow} {change_24h:+.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Bitcoin Price Chart")
        btc_chart = get_chart_data("bitcoin", days=7)
        if btc_chart and "prices" in btc_chart:
            df = pd.DataFrame(btc_chart["prices"])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='BTC Price',
                line=dict(color='#f7931a', width=2)
            ))
            
            fig.update_layout(
                title="Bitcoin Price (7 Days)",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Ethereum Price Chart")
        eth_chart = get_chart_data("ethereum", days=7)
        if eth_chart and "prices" in eth_chart:
            df = pd.DataFrame(eth_chart["prices"])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='ETH Price',
                line=dict(color='#627eea', width=2)
            ))
            
            fig.update_layout(
                title="Ethereum Price (7 Days)",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Market sentiment section
    st.markdown("---")
    st.markdown("### 🧠 AI Market Analysis")
    
    sentiment = get_market_sentiment()
    if sentiment:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Overall Sentiment")
            score = sentiment.get("overall_score", 50)
            st.metric("Sentiment Score", f"{score:.1f}/100")
            st.write(sentiment.get("sentiment", "Neutral"))
        
        with col2:
            st.markdown("#### Components")
            components = sentiment.get("components", {})
            for name, data in components.items():
                if isinstance(data, dict) and "score" in data:
                    st.write(f"**{name.title()}**: {data['score']:.1f}")
        
        with col3:
            st.markdown("#### Recommendation")
            recommendation = sentiment.get("recommendation", "Hold - Neutral market conditions")
            st.info(recommendation)

def show_alerts():
    """Alerts management page"""
    st.markdown("## 🔔 Price Alerts")
    
    # Create new alert section
    with st.expander("➕ Create New Alert", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            coins = get_supported_coins()
            coin_options = {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in coins[:50]}
            selected_coin = st.selectbox("Select Cryptocurrency", list(coin_options.keys()))
            symbol = coin_options[selected_coin] if selected_coin else ""
        
        with col2:
            condition = st.selectbox("Condition", ["above", "below"])
        
        with col3:
            target_price = st.number_input("Target Price ($)", min_value=0.0001, step=0.01, format="%.4f")
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("🚨 Create Alert", type="primary"):
                if symbol and target_price > 0:
                    if create_alert(symbol, condition, target_price):
                        st.success(f"Alert created: {selected_coin} {condition} ${target_price:.4f}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create alert")
                else:
                    st.error("Please fill all fields")
    
    # Active alerts
    st.markdown("### 📋 Active Alerts")
    alerts = get_alerts()
    
    if alerts:
        for alert in alerts:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            
            with col1:
                st.write(f"**{alert['symbol'].upper()}**")
            
            with col2:
                st.write(alert['condition'].title())
            
            with col3:
                st.write(f"${alert['target_price']:.4f}")
            
            with col4:
                created_at = datetime.fromisoformat(alert['created_at'].replace('Z', '+00:00'))
                st.write(f"Created: {created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col5:
                if st.button("🗑️", key=f"delete_{alert['id']}", help="Delete alert"):
                    if delete_alert(alert['id']):
                        st.success("Alert deleted")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No active alerts. Create your first alert above!")

def show_smart_alerts():
    """Smart alerts page with AI features"""
    st.markdown("## 🤖 Smart AI Alerts")
    st.markdown("Create intelligent alerts powered by AI analysis, sentiment monitoring, and pattern recognition.")
    
    # Create smart alert section
    with st.expander("🧠 Create Smart Alert", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            coins = get_supported_coins()
            coin_options = {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in coins[:50]}
            selected_coin = st.selectbox("Select Cryptocurrency", list(coin_options.keys()), key="smart_coin")
            symbol = coin_options[selected_coin] if selected_coin else ""
            
            alert_type = st.selectbox(
                "Alert Type",
                ["price", "volume", "sentiment", "pattern"],
                format_func=lambda x: {
                    "price": "💰 Smart Price Alert",
                    "volume": "📊 Volume Spike Alert", 
                    "sentiment": "😊 Sentiment Change Alert",
                    "pattern": "📈 Pattern Detection Alert"
                }[x]
            )
        
        with col2:
            if alert_type == "price":
                condition = st.selectbox("Condition", ["above", "below"], key="smart_condition")
                target_price = st.number_input("Target Price ($)", min_value=0.0001, step=0.01, format="%.4f", key="smart_price")
                parameters = {"condition": condition, "target_price": target_price}
                
            elif alert_type == "volume":
                multiplier = st.slider("Volume Spike Multiplier", 1.5, 5.0, 2.0, 0.1)
                parameters = {"multiplier": multiplier}
                
            elif alert_type == "sentiment":
                target_sentiment = st.slider("Target Sentiment Score", 0, 100, 70, 5)
                parameters = {"target_sentiment": target_sentiment}
                
            elif alert_type == "pattern":
                pattern_type = st.selectbox("Pattern Type", ["any", "bullish", "bearish"])
                min_confidence = st.slider("Minimum Confidence", 0.5, 0.95, 0.7, 0.05)
                parameters = {"pattern_type": pattern_type, "min_confidence": min_confidence}
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Create Smart Alert", type="primary"):
                if symbol:
                    if create_smart_alert(symbol, alert_type, parameters):
                        st.success(f"Smart {alert_type} alert created for {selected_coin}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create smart alert")
                else:
                    st.error("Please select a cryptocurrency")
    
    # Active smart alerts
    st.markdown("### 🎯 Active Smart Alerts")
    smart_alerts = get_smart_alerts()
    
    if smart_alerts:
        for alert in smart_alerts:
            # Create alert card
            priority_colors = {
                "low": "#6c757d",
                "medium": "#ffc107", 
                "high": "#fd7e14",
                "critical": "#dc3545"
            }
            
            color = priority_colors.get(alert.get("priority", "medium"), "#ffc107")
            
            st.markdown(f"""
            <div class="alert-card" style="border-left: 4px solid {color};">
                <h4>{alert['symbol'].upper()} - {alert['category'].title()} Alert</h4>
                <p><strong>Condition:</strong> {alert['condition']}</p>
                <p><strong>Threshold:</strong> {alert['threshold']}</p>
                <p><strong>Current Value:</strong> {alert['current_value']}</p>
                <p><strong>AI Confidence:</strong> {alert['confidence']:.0%}</p>
                <p><strong>Priority:</strong> {alert['priority'].title()}</p>
                <p><strong>Message:</strong> {alert['message']}</p>
                <small>Created: {alert['created_at']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active smart alerts. Create your first AI-powered alert above!")
    
    # AI Insights section
    st.markdown("---")
    st.markdown("### 🔮 AI Market Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Market Sentiment Breakdown")
        sentiment = get_market_sentiment()
        if sentiment and "components" in sentiment:
            components = sentiment["components"]
            
            # Create sentiment chart
            labels = []
            values = []
            for name, data in components.items():
                if isinstance(data, dict) and "score" in data:
                    labels.append(name.title())
                    values.append(data["score"])
            
            if labels and values:
                fig = go.Figure(data=go.Bar(x=labels, y=values, marker_color='#667eea'))
                fig.update_layout(
                    title="Sentiment Components",
                    yaxis_title="Score",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Prediction Accuracy")
        # In a real app, you'd track prediction accuracy over time
        # For demo, we'll show simulated accuracy metrics
        
        accuracy_data = {
            "Short Term (24h)": 78,
            "Medium Term (7d)": 65,
            "Long Term (30d)": 52
        }
        
        for timeframe, accuracy in accuracy_data.items():
            st.metric(timeframe, f"{accuracy}%")

def show_analytics():
    """Advanced analytics page"""
    st.markdown("## 📈 Advanced Analytics")
    
    # Symbol selection
    coins = get_supported_coins()
    coin_options = {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in coins[:20]}
    selected_coin = st.selectbox("Select Cryptocurrency for Analysis", list(coin_options.keys()))
    symbol = coin_options[selected_coin] if selected_coin else "bitcoin"
    
    if symbol:
        # Get data
        chart_data = get_chart_data(symbol, days=30)
        predictions = get_price_predictions(symbol)
        
        # Price chart with volume
        if chart_data and "prices" in chart_data:
            st.markdown("### 📊 Price & Volume Analysis")
            
            price_df = pd.DataFrame(chart_data["prices"])
            volume_df = pd.DataFrame(chart_data["volumes"])
            
            price_df['date'] = pd.to_datetime(price_df['timestamp'], unit='ms')
            volume_df['date'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('Price', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # Price chart
            fig.add_trace(
                go.Scatter(
                    x=price_df['date'],
                    y=price_df['price'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#667eea', width=2)
                ),
                row=1, col=1
            )
            
            # Volume chart
            fig.add_trace(
                go.Bar(
                    x=volume_df['date'],
                    y=volume_df['volume'],
                    name='Volume',
                    marker_color='#764ba2',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f"{selected_coin} - 30 Day Analysis",
                height=600,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Predictions
        if predictions:
            st.markdown("### 🔮 AI Price Predictions")
            
            col1, col2, col3 = st.columns(3)
            
            pred_data = predictions.get("predictions", {})
            
            with col1:
                st.markdown("#### 24 Hours")
                short_term = pred_data.get("short_term", {})
                if short_term:
                    direction = short_term.get("direction", "neutral")
                    confidence = short_term.get("confidence", 0)
                    change = short_term.get("price_change", 0)
                    
                    color = "#28a745" if direction == "up" else "#dc3545" if direction == "down" else "#6c757d"
                    arrow = "↗️" if direction == "up" else "↘️" if direction == "down" else "➡️"
                    
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3>{arrow} {direction.upper()}</h3>
                        <p>Change: {change:+.1%}</p>
                        <p>Confidence: {confidence:.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 7 Days")
                medium_term = pred_data.get("medium_term", {})
                if medium_term:
                    direction = medium_term.get("direction", "neutral")
                    confidence = medium_term.get("confidence", 0)
                    change = medium_term.get("price_change", 0)
                    
                    color = "#28a745" if direction == "up" else "#dc3545" if direction == "down" else "#6c757d"
                    arrow = "↗️" if direction == "up" else "↘️" if direction == "down" else "➡️"
                    
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3>{arrow} {direction.upper()}</h3>
                        <p>Change: {change:+.1%}</p>
                        <p>Confidence: {confidence:.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("#### 30 Days")
                long_term = pred_data.get("long_term", {})
                if long_term:
                    direction = long_term.get("direction", "neutral")
                    confidence = long_term.get("confidence", 0)
                    change = long_term.get("price_change", 0)
                    
                    color = "#28a745" if direction == "up" else "#dc3545" if direction == "down" else "#6c757d"
                    arrow = "↗️" if direction == "up" else "↘️" if direction == "down" else "➡️"
                    
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3>{arrow} {direction.upper()}</h3>
                        <p>Change: {change:+.1%}</p>
                        <p>Confidence: {confidence:.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Technical Analysis
            st.markdown("### 📊 Technical Analysis")
            tech_analysis = predictions.get("technical_analysis", {})
            if tech_analysis:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("RSI", f"{tech_analysis.get('rsi', 50):.1f}")
                    st.metric("Support Level", f"{tech_analysis.get('support_level', 1):.2f}x")
                    st.metric("Trend", tech_analysis.get('trend', 'sideways').title())
                
                with col2:
                    st.metric("MACD Signal", tech_analysis.get('macd_signal', 'neutral').title())
                    st.metric("Resistance Level", f"{tech_analysis.get('resistance_level', 1):.2f}x")
                    st.metric("Model Accuracy", f"{predictions.get('model_accuracy', 0.7):.0%}")

def show_portfolio():
    """Portfolio management page"""
    st.markdown("## 💼 Portfolio Management")
    st.info("Portfolio management features coming soon! This will include portfolio tracking, P&L analysis, and performance metrics.")
    
    # Placeholder for portfolio features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Portfolio Overview")
        st.metric("Total Value", "$0.00")
        st.metric("24h P&L", "$0.00 (0.00%)")
        st.metric("Total P&L", "$0.00 (0.00%)")
    
    with col2:
        st.markdown("### 🏆 Top Holdings")
        st.info("No holdings added yet")

def show_settings():
    """Settings and configuration page"""
    st.markdown("## ⚙️ Settings & Configuration")
    
    # Notification settings
    st.markdown("### 🔔 Notification Settings")
    
    with st.expander("📧 Email Configuration"):
        email_enabled = st.checkbox("Enable Email Notifications")
        if email_enabled:
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            email_username = st.text_input("Email Username")
            email_password = st.text_input("Email Password", type="password")
            from_email = st.text_input("From Email")
            
            if st.button("💾 Save Email Settings"):
                config = {
                    "email": {
                        "smtp_server": smtp_server,
                        "smtp_port": smtp_port,
                        "username": email_username,
                        "password": email_password,
                        "from_email": from_email
                    }
                }
                
                try:
                    response = requests.post(f"{API_BASE_URL}/api/notifications/configure", json=config)
                    if response.status_code == 200:
                        st.success("Email settings saved successfully!")
                    else:
                        st.error("Failed to save email settings")
                except:
                    st.error("Failed to connect to API")
    
    with st.expander("🔗 Webhook Configuration"):
        webhook_enabled = st.checkbox("Enable Webhook Notifications")
        if webhook_enabled:
            discord_webhook = st.text_input("Discord Webhook URL")
            telegram_webhook = st.text_input("Telegram Bot URL")
            
            if st.button("💾 Save Webhook Settings"):
                config = {
                    "webhooks": {
                        "discord": discord_webhook,
                        "telegram": telegram_webhook
                    }
                }
                
                try:
                    response = requests.post(f"{API_BASE_URL}/api/notifications/configure", json=config)
                    if response.status_code == 200:
                        st.success("Webhook settings saved successfully!")
                    else:
                        st.error("Failed to save webhook settings")
                except:
                    st.error("Failed to connect to API")
    
    # API Settings
    st.markdown("### 🔧 API Configuration")
    st.info(f"API Base URL: {API_BASE_URL}")
    
    # Test API connection
    if st.button("🔍 Test API Connection"):
        try:
            response = requests.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                st.success("✅ API connection successful!")
            else:
                st.error("❌ API connection failed")
        except:
            st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
    
    # System Status
    st.markdown("### 📊 System Status")
    try:
        response = requests.get(f"{API_BASE_URL}/api/engine-status")
        if response.status_code == 200:
            status = response.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Active Alerts", status.get("active_alerts", 0))
            with col2:
                st.metric("Total Alerts", status.get("total_alerts", 0))
            with col3:
                st.metric("Market Context", "Updated" if status.get("market_context") else "Pending")
            
            # Market context details
            if status.get("market_context"):
                st.json(status["market_context"])
        else:
            st.error("Failed to get system status")
    except:
        st.error("Cannot connect to API for system status")

if __name__ == "__main__":
    main()
