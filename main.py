import getpass
import mysql.connector
from commands import *
import warnings

def main():
    warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")

    db_user = input("Enter Database User: ")
    db_password = getpass.getpass()

    while(True):
        command = input(":> ")
        # FR1
        if command.upper() == "L" or command == "List":
            conn = new_connection(db_user, db_password)
            list_rooms(conn)
            conn.close()

        # FR2
        if command.upper() == "B" or command == "Book":
            conn = new_connection(db_user, db_password)
            reserve_room(conn)
            conn.close()

        # FR3
        if command.upper() == "C" or command == "Cancel":
            conn = new_connection(db_user, db_password)
            cancel_reservation(conn)
            conn.close()


        # FR4
        if command.upper() == "S" or command == "Search":
            conn = new_connection(db_user, db_password)
            search(conn)
            conn.close()

        # FR5
        if command.upper() == "R" or command == "Revenue":
            conn = new_connection(db_user, db_password)
            get_revenue(conn)
            conn.close()

        # Exit
        if command.upper() == "E":
            break

if __name__ == "__main__":
    main()