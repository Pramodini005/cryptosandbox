import asyncio
import logging
from typing import Dict, List
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.notification_channels = {
            "email": True,
            "webhook": True,
            "telegram": False,  # Requires bot token
            "discord": False,   # Requires webhook URL
            "push": False       # Requires push service setup
        }
        
        # Configuration (in production, use environment variables)
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",  # Set your email
            "password": "",  # Set your app password
            "from_email": ""  # Set your email
        }
        
        self.webhook_urls = {
            "discord": "",  # Set Discord webhook URL
            "telegram": ""  # Set Telegram bot API URL
        }
    
    async def send_alert_notification(self, alert_data: Dict, user_preferences: Dict = None):
        """Send notification through configured channels"""
        try:
            # Default preferences if none provided
            if user_preferences is None:
                user_preferences = {
                    "email": True,
                    "webhook": True,
                    "sound": True,
                    "push": True
                }
            
            # Format the notification message
            message = self.format_alert_message(alert_data)
            
            # Send through enabled channels
            tasks = []
            
            if user_preferences.get("email") and self.notification_channels["email"]:
                tasks.append(self.send_email_notification(message, alert_data))
            
            if user_preferences.get("webhook") and self.notification_channels["webhook"]:
                tasks.append(self.send_webhook_notification(message, alert_data))
            
            if user_preferences.get("telegram") and self.notification_channels["telegram"]:
                tasks.append(self.send_telegram_notification(message, alert_data))
            
            if user_preferences.get("discord") and self.notification_channels["discord"]:
                tasks.append(self.send_discord_notification(message, alert_data))
            
            # Execute all notification tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"Sent notifications for {alert_data.get('type', 'unknown')} alert")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def format_alert_message(self, alert_data: Dict) -> Dict:
        """Format alert data into notification message"""
        alert_type = alert_data.get("type", "unknown")
        symbol = alert_data.get("symbol", "")
        
        if alert_type == "price_alert":
            subject = f"🚨 Price Alert: {symbol}"
            body = f"""
            Price Alert Triggered!
            
            Symbol: {symbol}
            Condition: {alert_data.get('condition', '')} ${alert_data.get('target_price', 0):.4f}
            Current Price: ${alert_data.get('current_price', 0):.4f}
            24h Change: {alert_data.get('price_change_24h', 0):.2f}%
            
            Time: {alert_data.get('timestamp', '')}
            """
            
        elif alert_type == "volume_spike":
            subject = f"📊 Volume Spike: {symbol}"
            body = f"""
            Volume Spike Detected!
            
            Symbol: {symbol}
            Current Volume: {alert_data.get('current_volume', 0):,.0f}
            Average Volume: {alert_data.get('average_volume', 0):,.0f}
            Spike Ratio: {alert_data.get('spike_ratio', 0):.1f}x
            
            Time: {alert_data.get('timestamp', '')}
            """
            
        elif alert_type == "pattern_detection":
            pattern = alert_data.get('pattern', {})
            subject = f"📈 Pattern Alert: {symbol}"
            body = f"""
            Technical Pattern Detected!
            
            Symbol: {symbol}
            Pattern: {pattern.get('pattern', '')}
            Type: {pattern.get('type', '')}
            Confidence: {pattern.get('confidence', 0):.0%}
            Description: {pattern.get('description', '')}
            
            Time: {alert_data.get('timestamp', '')}
            """
            
        elif alert_type == "price_movement":
            subject = f"🚨 Price Movement: {symbol}"
            body = f"""
            Significant Price Movement!
            
            Symbol: {symbol}
            Direction: {alert_data.get('direction', '').upper()}
            Change: {alert_data.get('price_change', 0):.2f}%
            Current Price: ${alert_data.get('current_price', 0):.4f}
            
            Time: {alert_data.get('timestamp', '')}
            """
            
        else:
            subject = f"🔔 Crypto Alert: {symbol}"
            body = alert_data.get('message', 'Alert triggered')
        
        return {
            "subject": subject,
            "body": body,
            "html_body": self.create_html_notification(alert_data, subject, body)
        }
    
    def create_html_notification(self, alert_data: Dict, subject: str, body: str) -> str:
        """Create HTML version of notification"""
        symbol = alert_data.get("symbol", "")
        alert_type = alert_data.get("type", "unknown")
        
        # Color scheme based on alert type
        colors = {
            "price_alert": "#f59e0b",  # amber
            "volume_spike": "#3b82f6",  # blue
            "pattern_detection": "#10b981",  # emerald
            "price_movement": "#ef4444",  # red
            "default": "#6b7280"  # gray
        }
        
        color = colors.get(alert_type, colors["default"])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, {color}20, {color}10); border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                <h1 style="color: {color}; margin: 0 0 10px 0; font-size: 24px;">{subject}</h1>
                <div style="background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <pre style="white-space: pre-wrap; margin: 0; font-family: Arial, sans-serif;">{body}</pre>
                </div>
            </div>
            
            <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                <p>Crypto Price Alert Assistant</p>
                <p>Powered by AI-driven market analysis</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def send_email_notification(self, message: Dict, alert_data: Dict):
        """Send email notification"""
        try:
            if not self.email_config["username"] or not self.email_config["password"]:
                logger.warning("Email configuration not set, skipping email notification")
                return
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message["subject"]
            msg['From'] = self.email_config["from_email"]
            msg['To'] = self.email_config["username"]  # Send to self for demo
            
            # Add text and HTML parts
            text_part = MIMEText(message["body"], 'plain')
            html_part = MIMEText(message["html_body"], 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls()
                server.login(self.email_config["username"], self.email_config["password"])
                server.send_message(msg)
            
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def send_webhook_notification(self, message: Dict, alert_data: Dict):
        """Send webhook notification (generic HTTP POST)"""
        try:
            # This is a generic webhook - you can customize for your needs
            webhook_data = {
                "text": message["subject"],
                "alert_type": alert_data.get("type"),
                "symbol": alert_data.get("symbol"),
                "timestamp": alert_data.get("timestamp"),
                "data": alert_data
            }
            
            # Log webhook data (in production, send to actual webhook URL)
            logger.info(f"Webhook notification: {json.dumps(webhook_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def send_telegram_notification(self, message: Dict, alert_data: Dict):
        """Send Telegram notification"""
        try:
            if not self.webhook_urls["telegram"]:
                logger.warning("Telegram bot token not configured")
                return
            
            # Format message for Telegram
            telegram_message = f"🚨 *{alert_data.get('symbol', '')}*\n\n{message['body']}"
            
            # Send to Telegram (implement with your bot token and chat ID)
            logger.info(f"Telegram notification: {telegram_message}")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    async def send_discord_notification(self, message: Dict, alert_data: Dict):
        """Send Discord notification"""
        try:
            if not self.webhook_urls["discord"]:
                logger.warning("Discord webhook URL not configured")
                return
            
            # Format message for Discord
            discord_data = {
                "embeds": [{
                    "title": message["subject"],
                    "description": message["body"],
                    "color": 0xf59e0b,  # Orange color
                    "timestamp": alert_data.get("timestamp"),
                    "footer": {
                        "text": "Crypto Price Alert Assistant"
                    }
                }]
            }
            
            # Send to Discord (implement with your webhook URL)
            logger.info(f"Discord notification: {json.dumps(discord_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
    
    async def send_push_notification(self, message: Dict, alert_data: Dict):
        """Send push notification (requires push service setup)"""
        try:
            # Implement push notifications using services like:
            # - Firebase Cloud Messaging (FCM)
            # - Apple Push Notification Service (APNs)
            # - Web Push Protocol
            
            push_data = {
                "title": message["subject"],
                "body": alert_data.get("message", ""),
                "icon": "/icon-192x192.png",
                "badge": "/badge-72x72.png",
                "data": alert_data
            }
            
            logger.info(f"Push notification: {json.dumps(push_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        """Configure email settings"""
        self.email_config.update({
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_email": from_email
        })
        self.notification_channels["email"] = True
        logger.info("Email configuration updated")
    
    def configure_webhook(self, webhook_type: str, url: str):
        """Configure webhook URLs"""
        if webhook_type in self.webhook_urls:
            self.webhook_urls[webhook_type] = url
            self.notification_channels[webhook_type] = True
            logger.info(f"{webhook_type.title()} webhook configured")
    
    def get_notification_status(self) -> Dict:
        """Get status of all notification channels"""
        return {
            "channels": self.notification_channels,
            "email_configured": bool(self.email_config["username"]),
            "webhooks_configured": {
                name: bool(url) for name, url in self.webhook_urls.items()
            }
        }
