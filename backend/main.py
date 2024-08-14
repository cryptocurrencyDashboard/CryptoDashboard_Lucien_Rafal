from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine  # Import the create_engine function
#import cryptography



load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")



client = Client(api_key, api_secret)

coins = ('BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 
         'DOTUSDT', 'LUNAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'SHIBUSDT', 
         'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ALGOUSDT', 'TRXUSDT', 
         'LINKUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT')

# Fetch current prices from Binance
prices = []
for coin in coins:
    price_data = client.get_symbol_ticker(symbol=coin)
    prices.append({
        'symbol': price_data['symbol'],
        'current_price': float(price_data['price'])
    })

# Create a DataFrame with the current prices

df = pd.DataFrame(prices)

# Add the name and crypto_id manually or programmatically
df['crypto_id'] = range(1, len(df) + 1)
df['name'] = ['Bitcoin', 'Ethereum', 'Binance Coin', 'Solana', 'Cardano', 'XRP', 
              'Polkadot', 'Luna', 'Dogecoin', 'Avalanche', 'Shiba Inu', 
              'Polygon', 'Litecoin', 'Uniswap', 'Algorand', 'TRON', 
              'Chainlink', 'Decentraland', 'Cosmos', 'VeChain']

# Reorder the DataFrame columns
df = df[['crypto_id', 'symbol', 'name', 'current_price']]
# Database connection string 
DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost/crypto_data"
engine = create_engine(DATABASE_URL)

df.to_sql('crypto_prices', con=engine, if_exists='replace', index=False)
# Create the engine
print(df)  # Display the DataFrame to verify the data



# price_data = client.get_symbol_ticker(symbol="BTCUSDT")
# current_price = float(price_data['price'])

# print(f"The current price of BTC is {current_price} USDT.")



