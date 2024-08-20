from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd
from sqlalchemy import create_engine, text 
from sqlalchemy.orm import sessionmaker
from flask import Flask,jsonify,request
from flasgger import Swagger
import pymysql

#----------------`----------------------------------------------------------------------------------------------------
# => Lucien
#.env setup 
load_dotenv('../.env')

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

client = Client(api_key, api_secret)
app = Flask(__name__)
swagger = Swagger(app)

#--------------------------------------------------------------------------------------------------------------------
# => Lucien
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
# => Lucien
# SQLAchemy engine create all the tables and store in Mysql

DATABASE_URL = f"mysql+pymysql://{username}:{password}@db/{os.getenv('MYSQL_DATABASE')}"
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
# Rafal 
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
    """
    Register a new user
    ---
    tags:
      - User
    parameters:
      - in: body
        name: body
        schema:
          id: User
          required:
            - username
            - password
            - email
          properties:
            username:
              type: string
            password:
              type: string
            email:
              type: string
    responses:
      200:
        description: User successfully registered
      400:
        description: Invalid input
    """
    data = request.get_json()
    username = data.get("username") 
    password = data.get("password") 
    email = data.get("email")
    insertData(username, password, email)
    print(data)
    return "data added",200


@app.route("/user/update/<int:id>/", methods=["PUT"])
def update_user_by_id(id):
    """
    Update user information by ID
    ---
    tags:
      - User
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the user to update
      - in: body
        name: body
        schema:
          id: UserUpdate
          properties:
            username:
              type: string
              description: The new username for the user
              example: new_username
            password:
              type: string
              description: The new password for the user
              example: new_password123
            email:
              type: string
              description: The new email for the user
              example: user@example.com
          description: User data to update. You can provide any combination of username, password, and email.
    responses:
      200:
        description: User data updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User data updated successfully
      400:
        description: No valid fields to update or Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: No valid fields to update
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
    """
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


@app.route("/user/delete/<int:id>/", methods=["DELETE"])
def delete_user_by_id(id):
    """
    Delete a user by ID
    ---
    tags:
      - User
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the user to delete
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User deleted successfully
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
    """

    existing_user = session.execute(
        text("SELECT * FROM user WHERE user_id=:id"),
        {"id": id}
    ).fetchone()
    
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user
    delete_query = text("DELETE FROM user WHERE user_id=:id")
    session.execute(delete_query, {"id": id})
    session.commit()
    
    return jsonify({"message": "User deleted successfully"}), 200

@app.route("/user/<int:id>/", methods=["GET"])
def get_user_by_id(id):
    """
    Get user information by ID
    ---
    tags:
      - User
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the user to retrieve
    responses:
      200:
        description: User information retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
    """
    existing_user = session.execute(
        text("SELECT * FROM user WHERE user_id=:id"),
        {"id": id}
    ).fetchone()
    
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    # Extract user data
    user_data = {
        "id": existing_user.user_id,
        "username": existing_user.username,
        "email": existing_user.email,
        # Add other relevant fields if necessary
    }

    return jsonify(user_data), 200


@app.route("/transactions/", methods=["POST"])
def coin_transactions():
    """
    Create a new transaction
    ---
    tags:
      - Transactions
    parameters:
      - in: body
        name: body
        schema:
          id: Transaction
          required:
            - user_id
            - crypto_id
            - transaction_type
            - amount
          properties:
            user_id:
              type: integer
              description: The ID of the user making the transaction
            crypto_id:
              type: integer
              description: The ID of the cryptocurrency
            transaction_type:
              type: string
              enum: ['buy', 'sell']
              description: Type of the transaction (buy or sell)
            amount:
              type: number
              format: decimal
              description: Amount of cryptocurrency involved in the transaction
    responses:
      200:
        description: Transaction successfully created
        schema:
          type: object
          properties:
            message:
              type: string
              example: Transaction successfully created
      400:
        description: Invalid input or transaction error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Error message
    """
    data = request.get_json()
    user_id = data.get("user_id") 
    crypto_id = data.get("crypto_id") 
    transaction_type = data.get("transaction_type") 
    amount = data.get("amount") 

    transaction_query = text("INSERT INTO transactions (user_id, crypto_id, transaction_type, amount) VALUES (:user_id, :crypto_id, :transaction_type, :amount)"
    )
  
    session.execute(transaction_query, {"user_id": user_id , "crypto_id": crypto_id, "transaction_type": transaction_type, "amount":amount})
    session.commit()
    return jsonify({"message": "Transaction successfully"}), 200


@app.route("/transactions/<int:id>/", methods=["GET"])
def get_transaction_by_id(id):
    """
    Get all transactions for a user by ID
    ---
    tags:
      - Transactions
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the user whose transactions to retrieve
    responses:
      200:
        description: List of transactions retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              symbol:
                type: string
              transaction_type:
                type: string
                enum: ['buy', 'sell']
              amount:
                type: number
                format: decimal
              price_at_transaction:
                type: number
                format: decimal
              transaction_date:
                type: string
                format: date-time
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
    """
    existing_user = session.execute(
        text("SELECT * FROM user WHERE user_id=:id"),
        {"id": id}
    ).fetchone()
    
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    transaction_query = text("""
    SELECT c.symbol, t.transaction_type, t.amount, t.price_at_transaction, t.transaction_date 
    FROM transactions t 
    JOIN crypto_prices c ON c.crypto_id = t.crypto_id 
    WHERE t.user_id = :id
    """)
    transactions = session.execute(transaction_query, {"id": id}).fetchall()

    transaction_history = [
        {
            "symbol": transaction.symbol, 
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount), 
            "price_at_transaction": float(transaction.price_at_transaction),
            "transaction_date": transaction.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        } 
        for transaction in transactions
    ]
    return jsonify(transaction_history), 200


@app.route("/portfolio/<int:id>/", methods=["GET"])
def get_portfolio_by_id(id):
    """
    Get the portfolio for a user by ID
    ---
    tags:
      - Portfolio
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: The ID of the user whose portfolio to retrieve
    responses:
      200:
        description: Portfolio retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              symbol:
                type: string
              amount:
                type: number
                format: decimal
              total_value:
                type: number
                format: decimal
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
    """
    existing_user = session.execute(
        text("SELECT * FROM user WHERE user_id=:id"),
        {"id": id}
    ).fetchone()
    
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    portfolio_query = text("""
    SELECT c.symbol, p.amount, p.total_value
    FROM portfolio p 
    JOIN crypto_prices c ON c.crypto_id = p.crypto_id 
    WHERE p.user_id = :id
    """)
    transactions = session.execute(portfolio_query, {"id": id}).fetchall()

    transaction_history = [
        {
            "symbol": transaction.symbol, 
            "amount": float(transaction.amount),
            "total_value": float(transaction.total_value)
        } 
        for transaction in transactions
    ]
    return jsonify(transaction_history), 200


#-----------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

session.close()


