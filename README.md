## How to start 

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

**3. Add `.env` file to store apikey and apisecret**
- on your project root directory. create a file and name it `.env`
- paste the binance api-key and secret (i can pass you the format in private)
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
| /portfolio     | GET    | portfolio                            | Get the current holding                                                                    |



<img width="750" alt="Screenshot 2024-08-15 at 22 24 24" src="https://github.com/user-attachments/assets/feec6d6e-1062-4030-ac70-d8b5495a9d12">


## User Story

## Trigger
## .env example 
## endpoint result and parameters (check other api documentation sample)
