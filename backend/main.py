from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine, text   # Import the create_engine function
from sqlalchemy.orm import sessionmaker
from flask import Flask,jsonify,request

#------------------------------------------
#.env setup 
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

client = Client(api_key, api_secret)
app = Flask(__name__)



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
Session = sessionmaker(bind=engine)
session = Session()


# SQLAchemy inject "crypto_prices" table to database
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
    created_at DATETIME
);
"""

with engine.connect() as connection:
    connection.execute(text(create_table_query))
    connection.execute(text(create_user_table))
    
df.to_sql('crypto_prices', con=engine, if_exists='append', index=False)



def insertData(name, password, email):
   
    sql_query = text("INSERT INTO user (username, password, email) VALUES (:username, :password, :email)")
    session.execute(sql_query, {"username": name, "password": password, "email": email})
    session.commit()
    print("User successfully added")

@app.route("/user/register", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username") 
    password = data.get("password") 
    email = data.get("email")
    insertData(username, password, email)
    print(data)
    return "data added",200


# ----- rafal code 

@app.route("/user/update/<int:id>/", methods=["PUT"])
def update_user_by_id(id):
    data = request.get_json()
    
    # Check if user exists
    existing_user = session.execute(
        text("SELECT * FROM user WHERE user_id=:id"),
        {"id": id}
    ).fetchone()
    
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    # Build the update query dynamically based on the provided fields
    update_fields = []
    update_values = {"id": id}

    if "username" in data:
        update_fields.append("username=:username")
        update_values["username"] = data["username"]
    
    if "password" in data:
        update_fields.append("password=:password")
        update_values["password"] = data["password"]

    if "email" in data:
        update_fields.append("email=:email")
        update_values["email"] = data["email"]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    update_query = text(
        f"UPDATE user SET {', '.join(update_fields)} WHERE user_id=:id"
    )
    
    session.execute(update_query, update_values)
    session.commit()
    
    return jsonify({"message": "User data updated successfully"}), 200



#-----


app.run()

session.close()
print(df) 

