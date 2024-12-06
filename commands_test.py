

import mysql.connector
from commands import *
import pandas as pd

sql_user = "hpena02"
sql_password = "365-fall24-028577009"
conn = mysql.connector.connect(user=sql_user, password=sql_password,
                            host='mysql.labthreesixfive.com',
                            database=sql_user)
cursor = conn.cursor()


def test_fr1():
    list_rooms(conn)

def test_fr2():
    # Any RoomCode
    # Queen
    # 1 Kid
    # 1 adult
    #CHECKIN: 2023-10-15
    #CHECKOUT: 2023-10-17
    reserve_room(conn)

def test_fr3():
    # Any RoomCode
    # Queen
    # 1 Kid
    # 1 adult
    #CHECKIN: 2023-10-15
    #CHECKOUT: 2023-10-17
    cancel_reservation(conn)

if __name__ == "__main__":    
    #print(calculate_total_cost("2026-06-27", "2026-06-28", float(Decimal('175.00'))))
    test_fr3()
    #test_fr2()
    