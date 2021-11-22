import sqlite3
from getpass import getpass


def new_user(household: int = 1):
    name = input('name: ')
    password = getpass('password: ')
    conn = sqlite3.connect('server/api/db/db.sqlite3')
    curs = conn.cursor()
    vals = f'("{name}", "{password}", {household})'
    curs.execute(f'INSERT INTO householdmember VALUES {vals}')
    conn.commit()
    conn.close()
