import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv(".env.development")


def check_mysql():

    result = subprocess.run(
        [
            "docker",
            "exec",
            "mysql-dev",
            "mysqladmin",
            "ping",
            f"--host={os.getenv('MYSQL_HOST')}",
            f"--user={os.getenv('MYSQL_ROOT_USER')}",
            f"--password={os.getenv('MYSQL_ROOT_PASSWORD')}",
            "--silent",
        ],
        capture_output=True,
        text=True,
    )

    if "mysqld is alive" not in (result.stdout or ""):
        time.sleep(0.5)
        check_mysql()
        return

    print("\n 🟢 MySQL está pronto e aceitando conexões.")


print("🔴 Aguardando o MySQL aceitar conexões...")
check_mysql()
