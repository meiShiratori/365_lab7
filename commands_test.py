
import importlib  
import mysql.connector
from commands import *
import pandas as pd

conn = mysql.connector.connect(user="hpena02", password="365-fall24-028577009",
                            host='mysql.labthreesixfive.com',
                            database='hpena02')
cursor = conn.cursor()


def test_fr1():
    list_rooms(conn)

if __name__ == "__main__":    
    test_fr1()