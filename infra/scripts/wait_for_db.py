import time
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(".env.development")


def check_mysql():
    host = os.getenv("MYSQL_HOST") or "127.0.0.1"
    if host == "localhost":
        host = "127.0.0.1"

    while True:
        try:
            client = mysql.connector.connect(
                host=host,
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
                connection_timeout=5,
            )
            client.close()
            print("\n 🟢 MySQL está pronto e aceitando conexões.")
            return
        except mysql.connector.Error:
            time.sleep(1)


print("🔴 Aguardando o MySQL aceitar conexões...")
check_mysql()
