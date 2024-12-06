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
            print("List")
            list_rooms(conn)

        # FR2
        if command.upper() == "B" or command == "Book": 
            print("Book")

        # FR3
        if command.upper() == "C" or command == "Cancel": 
            print("Cancel")

        # FR4
        if command.upper() == "S" or command == "Search": 
            print("Search")
            get_revenue(conn)

        # FR5
        if command.upper() == "R" or command == "Revenue": 
            print("Revenue")
            get_revenue(conn)

        # Exit
        if command.upper() == "E":
            break

if __name__ == "__main__":
    main()