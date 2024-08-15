from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine, text   # Import the create_engine function
from sqlalchemy.orm import sessionmaker

#------------------------------------------
#.env setup 
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

client = Client(api_key, api_secret)


#------------------------------------------
#prepare "crypto_prices" table data (using pandas)
coins = ('BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 
         'DOTUSDT', 'LUNAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'SHIBUSDT', 
         'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ALGOUSDT', 'TRXUSDT', 
         'LINKUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT')
prices = []
for coin in coins:
    price_data = client.get_symbol_ticker(symbol=coin)
    prices.append({
        'symbol': price_data['symbol'],
        'current_price': float(price_data['price'])
    })
df = pd.DataFrame(prices)
df['name'] = ['Bitcoin', 'Ethereum', 'Binance Coin', 'Solana', 'Cardano', 'XRP', 
              'Polkadot', 'Luna', 'Dogecoin', 'Avalanche', 'Shiba Inu', 
              'Polygon', 'Litecoin', 'Uniswap', 'Algorand', 'TRON', 
              'Chainlink', 'Decentraland', 'Cosmos', 'VeChain']
df = df[['symbol', 'name', 'current_price']]

#------------------------------------------
# Database connection string 
DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost/crypto_data"
engine = create_engine(DATABASE_URL)

# SQLAchemy inject "crypto_prices" table to database
create_table_query = """
CREATE TABLE IF NOT EXISTS crypto_prices (
    crypto_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    current_price DECIMAL(15, 8)
);
"""
with engine.connect() as connection:
    connection.execute(text(create_table_query))
df.to_sql('crypto_prices', con=engine, if_exists='append', index=False)





print(df) 

