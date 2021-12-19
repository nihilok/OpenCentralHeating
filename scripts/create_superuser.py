import configparser
import json
import os
import sqlite3
from getpass import getpass
from pathlib import Path

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


config = configparser.ConfigParser()
path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "../api_v2/secrets/secrets.ini")
db_path = os.path.join(ROOT_DIR, "../db.sqlite3")
config.read(config_path)


def get_password_hash(password):
    return pwd_context.hash(password)


def check_for_first_household():
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()
    q = curs.execute("SELECT * FROM household")
    if not len(list(q)):
        curs.execute(f"INSERT INTO household DEFAULT VALUES")
    conn.commit()
    conn.close()


def create_superuser(household: int = 1):
    check_for_first_household()
    name = input("name: ")
    password = getpass("password: ")
    confirm_password = getpass("confirm_password: ")
    if password != confirm_password:
        print("**PASSWORDS DO NOT MATCH, please try again**")
        return create_superuser()
    password = get_password_hash(password)
    del confirm_password
    conn = sqlite3.connect(db_path)
    curs = conn.cursor()
    values = f'("{name}", "{password}", {household})'
    curs.execute(
        f"INSERT INTO household_member(name, password_hash, household_id) VALUES {values}"
    )
    conn.commit()
    superuser_id = curs.lastrowid
    conn.close()
    superuser_conf = config["SUPERUSERS"]
    if superuser_conf.get("superuser_list"):
        superusers = json.loads(superuser_conf["superuser_list"])
        superusers.append(superuser_id)
    else:
        superusers = [superuser_id]
    superuser_conf["superuser_list"] = json.dumps(superusers)
    with open(config_path, "w") as f:
        config.write(f)


if __name__ == "__main__":
    create_superuser()
