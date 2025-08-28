import MetaTrader5 as mt5
import logging
import os
from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger(__name__)

class MT5Handler:
    def __init__(self):
        self.is_connected = False
        load_dotenv()
        
        # Load credentials from .env file
        self.mt5_account = int(os.getenv("MT5_ACCOUNT"))
        self.mt5_password = os.getenv("MT5_PASSWORD")
        self.mt5_server = os.getenv("MT5_SERVER")
        self.mt5_path = os.getenv("MT5_PATH")

    def connect(self):
        """Initialize connection to MetaTrader 5 terminal"""
        if not mt5.initialize(path=self.mt5_path, login=self.mt5_account, password=self.mt5_password, server=self.mt5_server):
            logger.error(f"initialize() failed, error code = {mt5.last_error()}")
            self.is_connected = False
            return False
        
        logger.info("Successfully connected to MT5")
        self.is_connected = True
        return True

    def shutdown(self):
        """Shutdown connection to the MetaTrader 5 terminal"""
        mt5.shutdown()
        logger.info("Disconnected from MT5")
        self.is_connected = False

    def place_market_order(self, symbol, volume, order_type, tp=None, sl=None):
        """Places a market order (BUY or SELL)"""
        if not self.is_connected:
            logger.error("MT5 is not connected. Cannot place order.")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found.")
            return None

        if order_type.upper() == 'BUY':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        elif order_type.upper() == 'SELL':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            logger.error(f"Invalid market order type: {order_type}")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": trade_type,
            "price": price,
            "sl": float(sl) if sl else 0.0,
            "tp": float(tp) if tp else 0.0,
            "magic": 202401,
            "comment": "Webhook Market Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Market order executed successfully: {order_type} {volume} {symbol} @ {price}, Ticket: {result.order}")
            return result
        else:
            error_message = f"Market order failed: {result.comment if result else 'No result'} (retcode: {result.retcode if result else 'N/A'})"
            logger.error(error_message)
            return None

    def place_pending_order(self, symbol, volume, price, order_type, tp=None, sl=None):
        """
        Places all types of pending orders (LIMIT and STOP).
        """
        if not self.is_connected:
            logger.error("MT5 is not connected. Cannot place order.")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found.")
            return None

        order_type_map = {
            'BUY_LIMIT': mt5.ORDER_TYPE_BUY_LIMIT,
            'SELL_LIMIT': mt5.ORDER_TYPE_SELL_LIMIT,
            'BUY_STOP': mt5.ORDER_TYPE_BUY_STOP,
            'SELL_STOP': mt5.ORDER_TYPE_SELL_STOP
        }

        trade_type = order_type_map.get(order_type.upper())
        if trade_type is None:
            logger.error(f"Invalid pending order type: {order_type}")
            return None

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(volume),
            "type": trade_type,
            "price": float(price),
            "sl": float(sl) if sl else 0.0,
            "tp": float(tp) if tp else 0.0,
            "magic": 202401,
            "comment": "Webhook Pending Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        result = mt5.order_send(request)

        if result is None:
            logger.error("order_send failed, result is None")
            return None
            
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment} (retcode: {result.retcode})")
            return None
        
        logger.info(f"Pending order placed successfully: {order_type} {volume} {symbol} @ {price}, Ticket: {result.order}")
        return result

    def close_position(self, symbol, volume_to_close):
        """Closes a position for a given symbol by a specific volume."""
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            logger.warning(f"No open positions found for {symbol} to close.")
            return None

        position = positions[0]
        
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume_to_close),
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "magic": 202401,
            "comment": "Webhook Close Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Closed {volume_to_close} lots for position {position.ticket} on {symbol}")
            return result
        else:
            logger.error(f"Failed to close position for {symbol}: {result.comment if result else 'No result'}")
            return None
