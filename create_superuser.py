import sqlite3
from getpass import getpass

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def check_for_first_household():
    conn = sqlite3.connect("db.sqlite3")
    curs = conn.cursor()
    q = curs.execute("SELECT * FROM household")
    if not len(list(q)):
        curs.execute(f"INSERT INTO household DEFAULT VALUES")
    conn.commit()
    conn.close()


def create_superuser(household: int = 1):
    check_for_first_household()
    name = input("name: ")
    password = get_password_hash(getpass("password: "))
    conn = sqlite3.connect("db.sqlite3")
    curs = conn.cursor()
    vals = f'("{name}", "{password}", {household})'
    curs.execute(
        f"INSERT INTO householdmember(name, password_hash, household_id) VALUES {vals}"
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_superuser()
