import mysql.connector
from colorama import Fore, Style

try:
    save = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        port=8889,
        database="db-name"
    )
except mysql.connector.Error as err:
    raise Exception(Fore.RED + "Failed to connect to the database" + Style.RESET_ALL)

print(Fore.GREEN + "Connected to the database successfully" + Style.RESET_ALL)

def get_db():
    db = save.cursor(dictionary=True)
    try:
        yield db
    finally:
        db.close()