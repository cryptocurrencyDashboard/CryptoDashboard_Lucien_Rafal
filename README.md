
## Introduction

This API provides endpoints to manage users, perform cryptocurrency transactions, and retrieve user portfolios. It interacts with the Binance API for current cryptocurrency prices and uses MySQL for data storage. The API is designed to support user registration, updates, deletion, and management of transactions and portfolios.
Authentication



## How to start 

**prerequisites: you should have `docker` installed in your local machiine** 

- pull this github repo to your local machine `git clone https://github.com/cryptocurrencyDashboard/CryptoDashboard_Lucien_Rafal.git`
- In the command line, direct to the project directory and run `cp .env_example .env` to duplicate .env_example and rename the duplicate file to ".env"
- Enter all required creditial in .env file (except "MYSQL_DATABASE=crypto_data" which do not need to change)
- run `docker-compose -f docker-compose.yaml up` on your terminal
- The application should be up and running!

**Access Swagger**
- In Swagger you can find the structure of APIs endpoint
- if your application is running on http://127.0.0.1:5001.  Go to your browser and enter `http://127.0.0.1:5001/apidocs/` in the url bar

**Access MySQL database**
- first check the name of your mysql container name by running `docker ps`
  
<img width="1268" alt="Screenshot 2024-08-18 at 10 03 58" src="https://github.com/user-attachments/assets/ef627e0e-6986-4770-bb7b-cf68a79133dc">

- run `docker exec -it mysql_container mysql -u root -p` remember to replace `mysql_container` if you have customised container name.
  

## Base URL 

```arduino
http://localhost:5001/
```
## Endpoints

1. User Management
Register a New User
**Endpoint:** `/user/register`
**Method:** `POST`
**Description:** Registers a new user.
**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```
**Responses:**
200 OK: User successfully registered.
400 Bad Request: Invalid input.

2. Update User Information
**Endpoint:** `/user/update/<int:id>/`
**Method:** `PUT`
**Description:** Updates the user information based on user ID.
**Path Parameters:**
**id:** The ID of the user to update.
**Request Body (optional fields):**
```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```
**Responses:**
200 OK: User data updated successfully.
400 Bad Request: No valid fields to update or invalid input.
404 Not Found: User not found.

3. Delete User
Endpoint: /user/delete/<int:id>/
Method: DELETE
Description: Deletes a user based on the user ID.
Path Parameters:
id: The ID of the user to delete.
Responses:
200 OK: User deleted successfully.
404 Not Found: User not found.
Get User Information
Endpoint: /user/<int:id>/
Method: GET
Description: Retrieves information of a user by their ID.
Path Parameters:
id: The ID of the user to retrieve.
Responses:
200 OK: User information retrieved successfully.
404 Not Found: User not found.
2. Transaction Management
Create a New Transaction
Endpoint: /transactions/
Method: POST
Description: Creates a new cryptocurrency transaction (buy or sell).
Request Body:
json
Copy code
{
  "user_id": "integer",
  "crypto_id": "integer",
  "transaction_type": "string",
  "amount": "decimal"
}
Responses:
200 OK: Transaction successfully created.
400 Bad Request: Invalid input or transaction error.
Get Transactions by User ID
Endpoint: /transactions/<int:id>/
Method: GET
Description: Retrieves all transactions for a user by their ID.
Path Parameters:
id: The ID of the user whose transactions to retrieve.
Responses:
200 OK: List of transactions retrieved successfully.
404 Not Found: User not found.
3. Portfolio Management
Get Portfolio by User ID
Endpoint: /portfolio/<int:id>/
Method: GET
Description: Retrieves the cryptocurrency portfolio for a user by their ID.
Path Parameters:
id: The ID of the user whose portfolio to retrieve.
Responses:
200 OK: Portfolio retrieved successfully.
404 Not Found: User not found.
Error Handling

400 Bad Request: Indicates that the server could not understand the request due to invalid syntax or missing required fields.
404 Not Found: The requested resource could not be found, typically when a user ID or transaction ID does not exist.

## Backend EndPoint

| endPoint       | type   | table used                         | details                                                                                    |
| -------------- | ------ | ---------------------------------- | ------------------------------------------------------------------------------------------ |
| /user/register | POST   | User                               | user enter the username, password...etc                                                    |
| /user/edit/{id}     | PUT    | User                               | edit the user information                                                                  |
| /user/delete/{id}     | DELETE | User                               | delete user                                                                                |
| /user          | GET    | User                               | get all the user                                                                           |
| /transactions         | POST   | transactions, portfolio, crypto_price, User | Enter coin, type of trade amount to create the transaction. Result will be save to Holding |
| /transaction/{id} |GET    |transactions, crypto_price | user can view their transaction history |
| /portfolio     | GET    | portfolio, crypto_price, user                           | Get the current holding                                                                    |



<img width="750" alt="Screenshot 2024-08-15 at 22 24 24" src="https://github.com/user-attachments/assets/feec6d6e-1062-4030-ac70-d8b5495a9d12">


## User Story

## Trigger

## endpoint result and parameters (check other api documentation sample)
