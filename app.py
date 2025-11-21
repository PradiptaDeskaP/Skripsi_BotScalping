#!/usr/bin/env python3
"""
TradingView to Telegram Webhook Alert System
Professional Grade - Developed by Senior Trader & Engineer

Features:
- Real-time trading alerts from TradingView to Telegram
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime
import json
import time
import sys

# =============================================
# FIX UNICODE ENCODING FOR WINDOWS
# =============================================

# Fix untuk Windows encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# =============================================
# CONFIGURATION SETUP
# =============================================

# Setup comprehensive logging dengan encoding fix
class UnicodeSafeHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Encode ke UTF-8 dan replace characters yang problematic
            msg = msg.encode('utf-8', 'replace').decode('utf-8')
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Setup logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handler dengan Unicode support
handler = UnicodeSafeHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Remove default handlers jika ada
for h in logger.handlers[:]:
    logger.removeHandler(h)
logger.addHandler(handler)

app = Flask(__name__)

# Environment variables dengan fallback values - GUNAKAN DEFAULT YANG BERBEDA
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

# Jika environment variables tidak ada, gunakan hardcoded values
if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    TELEGRAM_BOT_TOKEN = '7696273057:AAHQuPoHXTDgK8tfZM_XZFDQ2MnuOxbN3Qw'
    
if TELEGRAM_CHAT_ID == 'YOUR_CHAT_ID_HERE':
    TELEGRAM_CHAT_ID = '1087807405'

# =============================================
# TRADING ALERT MANAGER CLASS
# =============================================

class TradingAlertManager:
    """
    Professional trading alert management system
    Handle semua jenis alert dari TradingView dengan format professional
    """
    
    def __init__(self):
        self.alert_count = 0
        self.last_alert_time = None
        self.alert_history = []
        
    def validate_alert_data(self, data):
        """
        Validasi data alert dari TradingView
        Memastikan data lengkap dan valid untuk trading decisions
        """
        logger.info("Validating alert data...")
        
        # Required fields untuk trading alert
        required_fields = ['symbol', 'action']
        
        for field in required_fields:
            if field not in data:
                error_msg = f"Missing required field: {field}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        # Validate action type
        valid_actions = ['buy', 'sell', 'entry', 'exit', 'close', 'long', 'short']
        if data['action'].lower() not in valid_actions:
            error_msg = f"Invalid action: {data['action']}. Valid actions: {valid_actions}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Alert data validation passed")
        return True
    
    def determine_trading_signal(self, action):
        """
        Determine trading signal type dengan detail professional
        """
        action = action.lower()
        
        signal_map = {
            'buy': {
                'emoji': '🟢',
                'signal_text': 'LONG ENTRY',
                'sentiment': 'BULLISH',
                'urgency': 'HIGH'
            },
            'long': {
                'emoji': '🟢', 
                'signal_text': 'LONG POSITION',
                'sentiment': 'BULLISH',
                'urgency': 'HIGH'
            },
            'sell': {
                'emoji': '🔴',
                'signal_text': 'SHORT ENTRY', 
                'sentiment': 'BEARISH',
                'urgency': 'HIGH'
            },
            'short': {
                'emoji': '🔴',
                'signal_text': 'SHORT POSITION',
                'sentiment': 'BEARISH', 
                'urgency': 'HIGH'
            },
            'exit': {
                'emoji': '⚪',
                'signal_text': 'POSITION EXIT',
                'sentiment': 'NEUTRAL',
                'urgency': 'MEDIUM'
            },
            'close': {
                'emoji': '⚪',
                'signal_text': 'POSITION CLOSE',
                'sentiment': 'NEUTRAL',
                'urgency': 'MEDIUM'
            }
        }
        
        return signal_map.get(action, {
            'emoji': '⚪',
            'signal_text': action.upper(),
            'sentiment': 'NEUTRAL',
            'urgency': 'LOW'
        })
    
    def format_professional_alert(self, data):
        """
        Format alert message dengan style professional trader
        Menggunakan emojis dan struktur yang mudah dibaca
        """
        # Extract data dengan safe defaults
        symbol = data.get('symbol', 'UNKNOWN')
        action = data.get('action', '')
        price = data.get('price', 'N/A')
        contracts = data.get('contracts', '1')
        position_size = data.get('position_size', '0')
        strategy_name = data.get('strategy', 'Unknown Strategy')
        timeframe = data.get('timeframe', 'N/A')
        custom_message = data.get('message', '')
        
        # Get trading signal details
        signal_info = self.determine_trading_signal(action)
        
        # Timestamp untuk audit trail
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        timestamp_epoch = int(current_time.timestamp())
        
        # Update alert counters
        self.alert_count += 1
        self.last_alert_time = formatted_time
        
        # Store alert in history (max 100 alerts)
        alert_record = {
            'alert_id': self.alert_count,
            'symbol': symbol,
            'action': action,
            'price': price,
            'timestamp': formatted_time,
            'epoch': timestamp_epoch
        }
        self.alert_history.append(alert_record)
        if len(self.alert_history) > 100:
            self.alert_history.pop(0)
        
        # =============================================
        # PROFESSIONAL ALERT MESSAGE FORMATTING
        # =============================================
        
        emoji = signal_info['emoji']
        signal_text = signal_info['signal_text']
        sentiment = signal_info['sentiment']
        urgency = signal_info['urgency']
        
        # Header berdasarkan urgency
        if urgency == 'HIGH':
            header = f"🚨 {emoji} URGENT TRADING ALERT #{self.alert_count} {emoji} 🚨"
        else:
            header = f"{emoji} TRADING ALERT #{self.alert_count} {emoji}"
        
        # Format message dengan struktur professional
        formatted_message = f"""
{header}
──────────────────────────────────

SYMBOL: {symbol}
SIGNAL: {signal_text}
PRICE: {price}
CONTRACTS: {contracts}
POSITION SIZE: {position_size}

TIMEFRAME: {timeframe}
TIME: {formatted_time}
STRATEGY: {strategy_name}

SENTIMENT: {sentiment}
URGENCY: {urgency}

NOTES: {custom_message}

#{sentiment} #{symbol.replace('/', '').replace('.', '')} #{action}
        """
        
        return formatted_message.strip()
    
    def send_telegram_alert(self, message):
        """
        Send formatted alert ke Telegram dengan error handling
        """
        logger.info("Sending alert to Telegram...")
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
            'disable_notification': False
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=15)
            processing_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                logger.info(f"Alert sent successfully in {processing_time}ms")
                return True
            else:
                error_msg = f"Telegram API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Telegram API timeout - alert not delivered")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - check internet connection")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Telegram: {e}")
            return False

# =============================================
# FLASK APPLICATION ROUTES
# =============================================

# Initialize trading alert manager
alert_manager = TradingAlertManager()

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint dengan comprehensive system status
    """
    status_info = {
        "status": "active",
        "service": "Professional TradingView to Telegram Webhook",
        "version": "2.0.0",
        "developer": "Senior Trader & Engineer - 45+ Years Experience",
        "alerts_processed": alert_manager.alert_count,
        "last_alert_time": alert_manager.last_alert_time,
        "uptime": "running",
        "endpoints": {
            "webhook": "POST /webhook - Main TradingView webhook",
            "test_alert": "GET /test - Test alert functionality", 
            "test_scalping": "GET /test/scalping - Test MACD scalping alerts",
            "health": "GET /health - System health check",
            "status": "GET /status - Detailed system status"
        },
        "supported_strategies": [
            "MACD Scalping",
            "Moving Average Cross", 
            "RSI Strategy",
            "Bollinger Bands",
            "Custom Strategies"
        ]
    }
    return jsonify(status_info)

@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """
    Main webhook endpoint untuk menerima alert dari TradingView
    """
    start_time = time.time()
    
    try:
        # Log request details untuk audit
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        logger.info(f"📨 WEBHOOK REQUEST FROM: {client_ip}")
        logger.info(f"🔹 Method: {request.method}")
        logger.info(f"🔹 Content-Type: {request.content_type}")
        logger.info(f"🔹 Headers: {dict(request.headers)}")
        
        data = None
        
        # Handle different content types
        if request.content_type and 'application/json' in request.content_type:
            # JSON content type
            data = request.get_json()
            logger.info("✅ Data received as application/json")
            
        elif request.content_type and 'text/plain' in request.content_type:
            # TradingView usually sends text/plain with JSON inside
            raw_data = request.get_data(as_text=True)
            logger.info(f"📝 Raw text data: {raw_data}")
            
            if raw_data:
                try:
                    data = json.loads(raw_data)
                    logger.info("✅ Successfully parsed text/plain as JSON")
                except json.JSONDecodeError:
                    # Jika bukan JSON, coba parse sebagai form data
                    try:
                        data = request.form.to_dict()
                        logger.info("✅ Parsed as form data")
                    except:
                        data = {'raw_message': raw_data}
                        logger.info("✅ Stored as raw message")
        
        elif request.form:
            # Form data
            data = request.form.to_dict()
            logger.info("✅ Data received as form-data")
            
        else:
            # Try to get raw body and parse as JSON
            raw_body = request.get_data(as_text=True)
            logger.info(f"🔍 Raw request body: {raw_body}")
            
            if raw_body:
                try:
                    data = json.loads(raw_body)
                    logger.info("✅ Successfully parsed raw body as JSON")
                except:
                    data = {'raw_message': raw_body}
                    logger.info("✅ Stored raw body as message")
        
        # Jika masih tidak ada data
        if not data:
            logger.error("❌ NO DATA RECEIVED")
            return jsonify({
                "status": "error",
                "message": "No data received",
                "content_type": request.content_type,
                "supported_types": ["application/json", "text/plain", "form-data"]
            }), 400
        
        logger.info(f"📊 Parsed data: {json.dumps(data, indent=2)}")
        
        # Handle case where data might be nested or have different structure
        processed_data = data
        
        # Jika data adalah string dalam 'raw_message', coba parse ulang
        if isinstance(processed_data, dict) and 'raw_message' in processed_data:
            try:
                raw_msg = processed_data['raw_message']
                if raw_msg.startswith('{') and raw_msg.endswith('}'):
                    processed_data = json.loads(raw_msg)
                    logger.info("✅ Parsed raw_message as JSON")
            except:
                pass
        
        # Validasi data alert
        alert_manager.validate_alert_data(processed_data)
        
        # Format professional alert message
        alert_message = alert_manager.format_professional_alert(processed_data)
        logger.info(f"📋 Formatted alert message ready")
        
        # Kirim ke Telegram
        logger.info("📤 Sending to Telegram...")
        success = alert_manager.send_telegram_alert(alert_message)
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        if success:
            logger.info(f"✅ Alert sent successfully in {processing_time}ms")
            return jsonify({
                "status": "success",
                "message": "Trading alert processed and delivered to Telegram",
                "symbol": processed_data.get('symbol'),
                "action": processed_data.get('action'),
                "alert_id": alert_manager.alert_count,
                "processing_time_ms": processing_time,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            logger.error(f"❌ Failed to send alert to Telegram")
            return jsonify({
                "status": "error", 
                "message": "Alert processed but failed to send to Telegram",
                "processing_time_ms": processing_time
            }), 500
            
    except ValueError as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Validation error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Data validation failed: {str(e)}",
            "required_fields": ["symbol", "action"],
            "valid_actions": ["buy", "sell", "entry", "exit", "close", "long", "short"],
            "processing_time_ms": processing_time
        }), 400
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "processing_time_ms": processing_time
        }), 500

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook_format():
    """
    Test endpoint untuk membantu debugging format data TradingView
    """
    if request.method == 'GET':
        return jsonify({
            "status": "test_endpoint",
            "message": "Send POST request to test webhook format",
            "example_payload": {
                "symbol": "BTCUSDT",
                "action": "buy",
                "price": "50000",
                "strategy": "Test_Strategy"
            },
            "content_types_supported": [
                "application/json", 
                "text/plain", 
                "application/x-www-form-urlencoded"
            ]
        })
    
    # Handle POST request
    result = {
        "received_headers": dict(request.headers),
        "content_type": request.content_type,
        "method": request.method,
        "parsed_data": None
    }
    
    # Try different parsing methods
    if request.content_type and 'application/json' in request.content_type:
        result['parsed_data'] = request.get_json()
        result['parse_method'] = 'application/json'
    elif request.content_type and 'text/plain' in request.content_type:
        raw_data = request.get_data(as_text=True)
        result['raw_data'] = raw_data
        try:
            result['parsed_data'] = json.loads(raw_data)
            result['parse_method'] = 'text/plain -> json'
        except:
            result['parse_method'] = 'text/plain (raw)'
    else:
        result['parsed_data'] = request.form.to_dict()
        result['parse_method'] = 'form-data'
    
    return jsonify(result)

@app.route('/test', methods=['GET'])
def test_alert():
    """
    Test endpoint untuk verify system functionality
    """
    logger.info("Test alert requested")
    
    test_data = {
        "symbol": "BBCA.JK",
        "action": "buy",
        "price": "8500",
        "contracts": "500",
        "position_size": "500",
        "strategy": "RSI_Oversold_Strategy",
        "timeframe": "1H",
        "message": "System Test - Trading alert system is functioning normally. RSI oversold condition detected."
    }
    
    try:
        # Validate test data
        alert_manager.validate_alert_data(test_data)
        
        # Format and send test alert
        alert_message = alert_manager.format_professional_alert(test_data)
        success = alert_manager.send_telegram_alert(alert_message)
        
        if success:
            logger.info("Test alert sent successfully")
            return jsonify({
                "status": "success",
                "message": "Test alert sent successfully",
                "alert_data": test_data,
                "alert_id": alert_manager.alert_count
            })
        else:
            logger.error("Failed to send test alert")
            return jsonify({
                "status": "error",
                "message": "Failed to send test alert to Telegram"
            }), 500
            
    except Exception as e:
        logger.error(f"Test alert failed: {e}")
        return jsonify({
            "status": "error",
            "message": f"Test failed: {str(e)}"
        }), 500

@app.route('/test/scalping', methods=['GET'])
def test_scalping_alert():
    """
    Test endpoint khusus untuk MACD Scalping strategy
    """
    logger.info("Testing MACD Scalping alerts")
    
    test_scenarios = [
        {
            "symbol": "DEWA.JK",
            "action": "buy",
            "contracts": "1000",
            "position_size": "1000",
            "price": "258",
            "strategy": "Ryan_MACD_Scalping",
            "timeframe": "5",
            "message": "MACD Bullish Crossover detected. Fast EMA crosses above Slow EMA. Entry signal confirmed."
        },
        {
            "symbol": "DEWA.JK",
            "action": "sell", 
            "contracts": "1000",
            "position_size": "0",
            "price": "262",
            "strategy": "Ryan_MACD_Scalping",
            "timeframe": "5",
            "message": "Take Profit target reached. MACD showing overbought conditions. Exit position."
        }
    ]
    
    results = []
    for i, test_data in enumerate(test_scenarios):
        try:
            alert_manager.validate_alert_data(test_data)
            alert_message = alert_manager.format_professional_alert(test_data)
            success = alert_manager.send_telegram_alert(alert_message)
            
            results.append({
                "scenario": f"{i+1}. {test_data['action'].upper()} {test_data['symbol']}",
                "status": "success" if success else "failed",
                "symbol": test_data['symbol'],
                "action": test_data['action']
            })
            
            # Small delay antara test alerts
            time.sleep(1)
            
        except Exception as e:
            results.append({
                "scenario": f"{i+1}. {test_data['action'].upper()} {test_data['symbol']}",
                "status": "error",
                "error": str(e)
            })
    
    logger.info(f"MACD Scalping test completed: {results}")
    
    return jsonify({
        "status": "test_completed",
        "strategy": "Ryan_MACD_Scalping",
        "results": results,
        "total_scenarios": len(test_scenarios),
        "successful": len([r for r in results if r['status'] == 'success'])
    })

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint untuk monitoring dan uptime checks
    """
    bot_configured = TELEGRAM_BOT_TOKEN not in ['YOUR_BOT_TOKEN_HERE', '']
    chat_configured = TELEGRAM_CHAT_ID not in ['YOUR_CHAT_ID_HERE', '']
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "tradingview-telegram-webhook",
        "version": "2.0.0",
        "alerts_processed": alert_manager.alert_count,
        "last_alert": alert_manager.last_alert_time,
        "telegram_configured": bot_configured and chat_configured,
        "environment": "production"
    }
    return jsonify(health_status)

@app.route('/status', methods=['GET'])
def detailed_status():
    """
    Detailed system status dengan alert history
    """
    # Recent alerts (last 10)
    recent_alerts = alert_manager.alert_history[-10:] if alert_manager.alert_history else []
    
    status_details = {
        "system": {
            "status": "operational",
            "uptime": "running",
            "flask_environment": os.environ.get('FLASK_ENV', 'production'),
            "python_version": os.sys.version
        },
        "alerts": {
            "total_processed": alert_manager.alert_count,
            "last_alert_time": alert_manager.last_alert_time,
            "recent_alerts": recent_alerts
        },
        "telegram": {
            "bot_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != '7696273057:AAHQuPoHXTDgK8tfZM_XZFDQ2MnuOxbN3Qw'),
            "chat_configured": bool(TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID != '1087807405')
        },
        "endpoints": {
            "webhook": "active",
            "health": "active", 
            "test": "active",
            "status": "active"
        }
    }
    return jsonify(status_details)

# =============================================
# ERROR HANDLERS
# =============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

# REMOVE THE PROBLEMATIC 405 HANDLER TEMPORARILY
# @app.errorhandler(405)
# def method_not_allowed(error):
#     return jsonify({
#         "status": "error", 
#         "message": "Method not allowed"
#     }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
# =============================================
# APPLICATION STARTUP - WITHOUT EMOJIS FOR WINDOWS
# =============================================

if __name__ == '__main__':
    # Startup message tanpa emojis untuk Windows compatibility
    logger.info("Starting Professional TradingView to Telegram Webhook Service")
    logger.info("Developed by Senior Trader & Engineer - 45+ Years Experience")
    logger.info("Configuration Check:")
    
    # Fix logic comparison - cek apakah menggunakan hardcoded values atau environment variables
    bot_configured = TELEGRAM_BOT_TOKEN not in ['YOUR_BOT_TOKEN_HERE', '']
    chat_configured = TELEGRAM_CHAT_ID not in ['YOUR_CHAT_ID_HERE', '']
    
    logger.info(f"   - Telegram Bot: {'✅ Configured' if bot_configured else '❌ Not Configured'}")
    logger.info(f"   - Telegram Chat: {'✅ Configured' if chat_configured else '❌ Not Configured'}")
    
    # Validasi configuration
    if not bot_configured or not chat_configured:
        logger.error("❌ Telegram configuration missing! Please set environment variables.")
        logger.info("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
    else:
        logger.info("✅ Telegram configuration verified")
        
    logger.info("🚀 Ready to receive trading alerts!")
    
    # Get port from environment variable (for Render/Heroku)
    port = int(os.environ.get('PORT', 5000))
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )