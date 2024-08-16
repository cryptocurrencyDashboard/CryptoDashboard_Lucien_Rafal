from dotenv import load_dotenv
import os
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request, make_response
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Load environment variables
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

# Initialize Binance Client and Flask App
client = Client(api_key, api_secret)
app = Flask(__name__)

# Database Connection Setup
DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost/crypto_data"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create tables if not exist
create_table_query = """
CREATE TABLE IF NOT EXISTS crypto_prices (
    crypto_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    current_price DECIMAL(15, 8)
);
"""
create_user_table = """
CREATE TABLE IF NOT EXISTS user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

with engine.connect() as connection:
    connection.execute(text(create_table_query))
    connection.execute(text(create_user_table))

# Insert Initial Crypto Data
def load_crypto_data():
    coins = (
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT',
        'DOTUSDT', 'LUNAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'SHIBUSDT',
        'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ALGOUSDT', 'TRXUSDT',
        'LINKUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT'
    )
    prices = []
    for coin in coins:
        price_data = client.get_symbol_ticker(symbol=coin)
        prices.append({
            'symbol': price_data['symbol'],
            'current_price': float(price_data['price'])
        })
    df = pd.DataFrame(prices)
    df['name'] = [
        'Bitcoin', 'Ethereum', 'Binance Coin', 'Solana', 'Cardano', 'XRP',
        'Polkadot', 'Luna', 'Dogecoin', 'Avalanche', 'Shiba Inu',
        'Polygon', 'Litecoin', 'Uniswap', 'Algorand', 'TRON',
        'Chainlink', 'Decentraland', 'Cosmos', 'VeChain'
    ]
    df = df[['symbol', 'name', 'current_price']]
    df.to_sql('crypto_prices', con=engine, if_exists='replace', index=False)

load_crypto_data()

# Insert User Data
def insert_data(username, password, email):
    session = Session()
    try:
        sql_query = text("""
            INSERT INTO user (username, password, email)
            VALUES (:username, :password, :email)
        """)
        session.execute(sql_query, {"username": username, "password": password, "email": email})
        session.commit()
        return {"message": "User successfully added"}
    except SQLAlchemyError as e:
        session.rollback()
        return {"error": str(e)}, 500
    finally:
        session.close()

@app.route("/user/register", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    result = insert_data(username, password, email)
    return jsonify(result), (200 if "message" in result else 500)

# Update User Data
def update_data(user_id, username, password, email):
    session = Session()
    try:
        sql_query = text("""
            UPDATE user 
            SET username = :username, password = :password, email = :email 
            WHERE user_id = :user_id
        """)
        session.execute(sql_query, {"username": username, "password": password, "email": email, "user_id": user_id})
        session.commit()
        return {"message": "User updated successfully"}
    except SQLAlchemyError as e:
        session.rollback()
        return {"error": str(e)}, 500
    finally:
        session.close()

@app.route("/user/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    result = update_data(user_id, username, password, email)
    return jsonify(result), (200 if "message" in result else 500)

# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
