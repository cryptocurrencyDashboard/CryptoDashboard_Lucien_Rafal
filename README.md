## How to start 

### Option1: Docker 
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


### Option2: Without Docker and build your own enviornment in local machine

-  pull this github repo to your local machine `git clone https://github.com/cryptocurrencyDashboard/CryptoDashboard_Lucien_Rafal.git`
   
**1. Set up Environemnt on VS code**
-  Open it with Visual Studio Code. (terminal need to be in the project root directory).  Set up the enviornment `python3 -m venv venv`
-  VS studio code will prompt if you want to create a venv2934 file. click `yes`
-  Activate the environment `source venv/bin/activate`
- To check if the envornment is activate - you can see (venv) in your terminal prompt as per below image
<img width="398" alt="Screenshot 2024-08-14 at 09 52 08" src="https://github.com/user-attachments/assets/6e66d5b0-8fc1-4a79-8fb7-bf3634492a0b">

**2. install dependancies from requirement.txt**
- once environment activated, install all dependancies mentioned in `requirement.txt` by running ` pip3 install -r requirements.txt`
- You should now have `venv` folder in your root directory

**3. Set up environment creditial: Copy`.env_example ` to `.env` file to store apikey and apisecret**
- on your project root director, Copy `.env_example` to `.env`.
-  Fill in your own credentials in the `.env` file.
- **Important**: The api-key and secret should NEVER upload to the github or commit. it can only exist in your local environment.  To ensure apikey doesn't upload to github. you should see an `.gitignore` file on your root directory.  Everything mentioned in this file WON"T be upload to github nor in git commit history.  so if you see `.env` written in the `.gitignore` file then you are safe 

**4. Run the program**
- on the project root directory. run in terminal `python3 backend/main.py`

**5.Before push your code to github**
- run `pip3 freeze > requirements.txt` to update requirements.txt file (so your new added dependencies are in the files"


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
