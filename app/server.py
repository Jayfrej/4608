from flask import Flask, request, jsonify
import logging
from app.mt5_handler import MT5Handler

# Setup logging
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the MT5 handler
mt5_handler = MT5Handler()

def initialize_mt5():
    """Function to be called from main.py to connect to MT5."""
    return mt5_handler.connect()

@app.route('/trade', methods=['POST'])
def webhook():
    """Main webhook endpoint to process trading signals."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        logger.info(f"Received webhook: {data}")

        action = data.get('action', '').upper()
        symbol = data.get('symbol')
        volume = data.get('volume')

        # --- NEW: Handle flexible tp/sl key names ---
        tp = data.get('tp') or data.get('take_profit')
        sl = data.get('sl') or data.get('stop_loss')

        # --- Market Orders ---
        if action in ['BUY', 'SELL', 'LONG', 'SHORT']:
            trade_action = 'BUY' if action in ['BUY', 'LONG'] else 'SELL'
            
            result = mt5_handler.place_market_order(
                symbol, 
                float(volume), 
                trade_action, 
                tp=tp, 
                sl=sl
            )

            if result:
                return jsonify({"status": "success", "message": "Market order placed", "ticket": result.order}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to place market order"}), 500

        # --- Pending Orders (LIMIT and STOP) ---
        elif action in ['BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP']:
            price = data.get('price')

            if not all([symbol, volume, price]):
                return jsonify({"error": "Missing required fields for pending order: symbol, volume, price"}), 400
            
            result = mt5_handler.place_pending_order(symbol, float(volume), float(price), action, tp, sl)
            
            if result:
                return jsonify({"status": "success", "message": "Pending order placed", "ticket": result.order}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to place pending order"}), 500
        
        # --- Close Order ---
        elif action == 'CLOSE':
            if not all([symbol, volume]):
                return jsonify({"error": "Missing required fields for close action: symbol, volume"}), 400
            
            result = mt5_handler.close_position(symbol, float(volume))
            if result:
                return jsonify({"status": "success", "message": "Close order executed"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to close position"}), 500

        # --- Unknown Action ---
        else:
            error_msg = f"Unknown or unsupported action: '{data.get('action')}'"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

    except ValueError as ve:
        error_msg = f"Invalid data format, likely for volume, price, sl, or tp: {ve}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({"status": "ok"}), 200
