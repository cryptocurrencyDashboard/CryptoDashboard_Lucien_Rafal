from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine, text   # Import the create_engine function
from sqlalchemy.orm import sessionmaker
from flask import Flask,jsonify,request
import pymysql

#--------------------------------------------------------------------------------------------------------------------
#.env setup 
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

client = Client(api_key, api_secret)
app = Flask(__name__)



#--------------------------------------------------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------------------------------------------
# SQLAchemy engine create all the tables and store in Mysql

DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost/crypto_data"
engine = create_engine(DATABASE_URL)
 
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

create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    crypto_id INT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    amount DECIMAL(15, 8) NOT NULL,
    price_at_transaction DECIMAL(15, 2) NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (crypto_id) REFERENCES crypto_prices(crypto_id)
);
"""

drop_before_insert_trigger = "DROP TRIGGER IF EXISTS before_insert_transaction;"
drop_after_insert_trigger = "DROP TRIGGER IF EXISTS after_insert_transaction;"

create_before_insert_transaction_trigger = """

CREATE TRIGGER before_insert_transaction
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
    DECLARE currentPrice DECIMAL(15, 8);
 
    SELECT current_price INTO currentPrice 
    FROM crypto_prices 
    WHERE crypto_id = NEW.crypto_id;

    SET NEW.price_at_transaction = currentPrice;
END;

"""

create_portfolio_table = """
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    crypto_id INT NOT NULL,
    amount DECIMAL(15, 8) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (crypto_id) REFERENCES crypto_prices(crypto_id)
);
"""

create_after_insert_transaction_trigger = """


CREATE TRIGGER after_insert_transaction
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    DECLARE new_amount DECIMAL(15, 8);
    DECLARE new_total_value DECIMAL(15, 2);
    DECLARE adjusted_amount DECIMAL(15, 8);

    IF NEW.transaction_type = 'buy' THEN
        SET adjusted_amount = NEW.amount; 
    ELSEIF NEW.transaction_type = 'sell' THEN
        SET adjusted_amount = -NEW.amount; 
    END IF;


    IF EXISTS (SELECT 1 FROM portfolio WHERE user_id = NEW.user_id AND crypto_id = NEW.crypto_id) THEN
    
        SELECT amount + adjusted_amount
        INTO new_amount
        FROM portfolio
        WHERE user_id = NEW.user_id AND crypto_id = NEW.crypto_id;

   
        IF new_amount < 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient holdings: transaction would result in negative balance';
        ELSE
      
            SET new_total_value = new_amount * NEW.price_at_transaction;
            UPDATE portfolio
            SET amount = new_amount, 
                total_value = new_total_value
            WHERE user_id = NEW.user_id AND crypto_id = NEW.crypto_id;
        END IF;
    ELSE
        -- Insert new holding, only if the transaction is a buy (initial holding)
        IF NEW.transaction_type = 'buy' THEN
            INSERT INTO portfolio (user_id, crypto_id, amount, total_value)
            VALUES (NEW.user_id, NEW.crypto_id, NEW.amount, NEW.amount * NEW.price_at_transaction);
        ELSE
            -- Raise an error if there's an attempt to sell without an existing holding
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot sell: no holdings available for this cryptocurrency';
        END IF;
    END IF;
END;

"""


# with engine.connect() as connection:
#     connection.execute(text(create_table_query))
#     connection.execute(text(create_user_table))
#     connection.execute(text(create_transactions_table))
#     connection.execute(text(drop_before_insert_trigger))
#     connection.execute(text(drop_after_insert_trigger))
#     connection.execute(text(create_before_insert_transaction_trigger))
#     connection.execute(text(create_portfolio_table))
#     connection.execute(text(create_after_insert_transaction_trigger))


connection = engine.raw_connection()
try:
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    cursor.execute(create_user_table)
    cursor.execute(create_transactions_table)
    cursor.execute(drop_before_insert_trigger)
    cursor.execute(drop_after_insert_trigger)
    cursor.execute(create_before_insert_transaction_trigger)
    cursor.execute(create_portfolio_table)
    cursor.execute(create_after_insert_transaction_trigger)
    connection.commit()  # Commit the transaction
finally:
    cursor.close()
    connection.close()




    
df.to_sql('crypto_prices', con=engine, if_exists='append', index=False)


#--------------------------------------------------------------------------------------------------------------------
# Flask session create end point

Session = sessionmaker(bind=engine)
session = Session()

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



#-----





app.run()

session.close()
print(df) 

