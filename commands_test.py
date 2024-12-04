

import mysql.connector
from commands import *
import pandas as pd

sql_user = "hpena02"
sql_password = "password"
conn = mysql.connector.connect(user=sql_user, password=sql_password,
                            host='mysql.labthreesixfive.com',
                            database=sql_user)
cursor = conn.cursor()


def test_fr1():
    list_rooms(conn)

if __name__ == "__main__":    
    test_fr1()