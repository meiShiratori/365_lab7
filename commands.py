import pandas as pd
from datetime import datetime, timedelta

def list_rooms(conn):
    sql_query = """
        WITH popularity AS (
            SELECT 
                RoomCode,
                ROUND(SUM(LEAST(Checkout, CURDATE()) 
                        - GREATEST(CheckIn, CURDATE() - INTERVAL 180 DAY) + 1)/180,2) 
                        AS PopScore
            FROM 
                hpena02.lab7_rooms
            JOIN 
                hpena02.lab7_reservations ON hpena02.lab7_rooms.RoomCode = hpena02.lab7_reservations.Room
            WHERE 
                Checkout >= CURDATE() - INTERVAL 180 DAY
                AND CheckIn <= CURDATE()                
            GROUP BY 
                RoomCode, RoomName
        ), next_available AS (
            SELECT 
                RoomCode,
                CASE 
                    WHEN 
                        DATEDIFF(MAX(Checkout),CURDATE()) < 0 THEN CURDATE() 
                    ELSE 
                        MAX(Checkout)                        
                END AS NextAvailableCheckIn
            FROM 
                hpena02.lab7_rooms 
            JOIN 
                hpena02.lab7_reservations ON RoomCode = Room 
            WHERE 
                Checkin < CURDATE()
            GROUP BY 
                RoomCode
        ), completed_stay AS (   
            SELECT 
                r.RoomCode,
                DATEDIFF(
                    MAX(res.Checkout), 
                    MAX(res.CheckIn)
                ) + 1 AS LatestReservationLength
            FROM 
                hpena02.lab7_rooms r
            JOIN 
                hpena02.lab7_reservations res ON r.RoomCode = res.Room
            WHERE 
                res.Checkout <= CURDATE()
            GROUP BY 
                r.RoomCode
        )
        SELECT 
            r.RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor, PopScore, NextAvailableCheckIn, LatestReservationLength
        FROM 
            hpena02.lab7_rooms r
        JOIN
            popularity p ON p.RoomCode = r.RoomCode
        JOIN
            next_available na ON na.RoomCode = r.RoomCode
        JOIN
            completed_stay cs ON cs.RoomCode = r.RoomCode
        ORDER BY
            PopScore DESC
    """

    df = pd.read_sql(sql_query, conn)

    print(df)

    # cursor.execute("SELECT * FRoM hpena02.lab7_rooms")
    # result = cursor.fetchall()
    # return result

def reserve_room(conn):
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    room_code = input("Room Code (Enter or \"Any\" for no preference): ")
    bed_type = input("Bed Type (Enter or \"Any\" for no preference): ")
    check_in = input("Check-In Date (YYYY-MM-DD): ")
    check_out = input("Check-Out Date (YYYY-MM-DD): ")
    adults = int(input("Number of Adult: "))
    kids = int(input("Number of Children: "))
    guest_count = kids + adults
    args = [check_out, check_in, guest_count]

    preferences = """"""
    # Room Code Given
    if room_code != "Any" and room_code != "":
        args.append(room_code)
        preferences = preferences + "AND Room=%s"
    # Bed Type Given
    if bed_type != "Any" and bed_type != "":
        args.append(bed_type)
        preferences = preferences + "AND bedType=%s"

    sql_query = f"""
        WITH available_rooms AS (
            SELECT
                Room
            FROM 
                hpena02.lab7_reservations AS res
            EXCEPT
            SELECT 
                Room
            FROM 
                hpena02.lab7_reservations AS res
            WHERE
                NOT (
                    CheckOut <= %s OR
                    CheckIn >= %s
                )
        )
        SELECT 
            RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor
        FROM 
            available_rooms ar
        JOIN
            hpena02.lab7_rooms AS r
        ON
            ar.Room = r.RoomCode
        WHERE
            maxOcc>=%s {preferences}
    """
   
    cursor = conn.cursor()
    cursor.execute(sql_query, args)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(result, columns=columns)
    print("\n<----- Available Rooms ----->")
    print(df)

    print("\n")
    selected_index = input(f"Select a room from 0-{len(result)-1} or [C]ancel: ")
    if selected_index == "C" or selected_index == "Cancel":
        return
    selected_room = result[ int(selected_index)]
    
    #print(selected_room)

    insert_query = """
        INSERT INTO 
            hpena02.lab7_reservations (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids) 
        VALUES 
            (UUID(), %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    insert_args = [selected_room[0], check_in, check_out, calculate_total_cost(check_in, check_out, float(selected_room[5])), last_name, first_name, adults, kids]
    print(insert_args)
    cursor.execute(insert_query, insert_args)
    conn.commit()

def cancel_reservation(conn):
    cursor = conn.cursor()
    del_query = """
        DELETE FROM hpena02.lab7_reservations
        WHERE CODE = %s;
    """
    room_code = input("Reservation Code: ")
    answer = input("Are you sure? (y/N): ")
    if answer.upper() != "Y":
        return
    cursor.execute(del_query, [room_code])
    conn.commit()
    print("Reservation successfully cancelled.")


def calculate_total_cost(check_in, check_out, base_rate):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
    total_days = (check_out_date - check_in_date).days
    weekdays = 0
    weekends = 0

    for i in range(total_days):
        current_day = check_in_date + timedelta(days=i)
        if current_day.weekday() < 5:
            weekdays += 1
        else: 
            weekends += 1

    weekday_cost = weekdays * base_rate
    weekend_cost = weekends * (base_rate * 1.1)
    return round(weekday_cost + weekend_cost, 2)


