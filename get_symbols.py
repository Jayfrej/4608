import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load settings from your .env file
load_dotenv()

# --- MT5 Connection Details ---
# Read credentials from the .env file
account = int(os.getenv("MT5_ACCOUNT"))
password = os.getenv("MT5_PASSWORD")
server = os.getenv("MT5_SERVER")
path = os.getenv("MT5_PATH")

print("Connecting to MT5...")

# Initialize connection to the MetaTrader 5 terminal
if not mt5.initialize(path=path, login=account, password=password, server=server):
    print(f"initialize() failed, error code = {mt5.last_error()}")
    mt5.shutdown()
else:
    print("Connection to MT5 successful.")
    
    # Get all symbols available from the broker
    symbols = mt5.symbols_get()
    
    if symbols:
        print(f"\nFound {len(symbols)} symbols. Listing them below:")
        print("---------------------------------")
        # Loop through and print the name of each symbol
        for s in symbols:
            print(s.name)
        print("---------------------------------")
    else:
        print("No symbols found.")
        
    # Disconnect from MT5
    mt5.shutdown()
    print("\nDisconnected from MT5. Script finished.")