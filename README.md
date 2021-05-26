# Restful-API-with-Falcon-and-SQLAlchemy
MVC structure for a Restful API using python, Falcon, and SQLAclhemy

If you want to use this install the requierements: pip3 install -r requirements.txt

Create a folder with name files

Create a config.ini file with the below info and update it with yours:

[ROUTES]
context = api
root = api/profile
host = http://127.0.0.1:3306

[DATABASE]
host = 
port = 3306
user = 
password = 
database = 

[SMTP]
username = 
password = 
port = 465
server = smtp.gmail.com 

[EXPIRATION_TIMES]
session = 10080
otp = 1440
email_code = 1440

[FILES]
accepted_files = ["image/png", "image/jpg", "image/jpeg", "application/pdf"]
storage_path = ./files
max_file_size = 4000000 # 1,000,000 bytes = 1 MB
