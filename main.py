import getpass
import mysql.connector
from commands import *
import warnings

def main():
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

    db_user = input("Enter Database User: ")
    db_password = getpass.getpass()
    conn = mysql.connector.connect(user=db_user, password=db_password,
                                host='mysql.labthreesixfive.com',
                                database=db_user)

    cursor = conn.cursor()
    if cursor:
        print("Connection established.")
    print("Welcome to the Inn Management System.")

    while(True):
        command = input(":> ")
        # FR1
        if command.upper() == "L" or command == "List": 
            list_rooms(conn)

        # FR2
        if command.upper() == "B" or command == "Book": 
            reserve_room(conn)

        # FR3
        if command.upper() == "C" or command == "Cancel": 
            cancel_reservation(conn)

        # FR4
        if command.upper() == "S" or command == "Search": 
            search(conn)

        # FR5
        if command.upper() == "R" or command == "Revenue": 
            get_revenue(conn)

        # Exit
        if command.upper() == "E":
            break

if __name__ == "__main__":
    main()