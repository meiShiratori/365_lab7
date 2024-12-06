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
                Checkin <= CURDATE()
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
            r.RoomCode, RoomName, Beds,  bedType, maxOcc, basePrice, decor, PopScore, NextAvailableCheckIn, LatestReservationLength
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

def search(conn):
    first_name = input("Enter first name:\n:> ").strip()
    last_name = input("Enter last name :\n:> ").strip()
    checkin = input("Enter check-in date (YYYY-MM-DD):\n:> ").strip()
    while not checkin:
        print("Check-in cannot be blank\n")
        checkin = input("Enter check-in date (YYYY-MM-DD):\n:> ").strip()
    checkout = input("Enter check-out date (YYYY-MM-DD):\n:> ").strip()
    while not checkout:
        print("Check-out cannot be blank\n")
        checkout = input("Enter check-out date (YYYY-MM-DD):\n:> ").strip()
    reservation_code = input("Enter reservation code:\n:> ").strip()
    room_code = input("Enter room code:\n:> ").strip()

    sql_query = f"""
    SELECT 
        res.*,
        rooms.RoomName,
        rooms.Beds,
        rooms.bedType,
        rooms.maxOcc,
        rooms.basePrice,
        rooms.decor
    FROM 
        hpena02.lab7_reservations res
    JOIN 
        hpena02.lab7_rooms rooms ON res.Room = rooms.RoomCode
    WHERE
        (%s = '' OR res.FirstName LIKE %s)
        AND (%s = '' OR res.LastName LIKE %s)
        AND (
            (%s = '' AND %s = '')
            OR (res.CheckIn BETWEEN %s AND %s)
        )
        AND (%s = '' OR res.Room LIKE %s)
        AND (%s = '' OR res.CODE = %s);
    """

    cursor = conn.cursor()
    first_name_wildcard = f"%{first_name}%" if first_name else ""
    last_name_wildcard = f"%{last_name}%" if last_name else ""
    room_code_wildcard = f"%{room_code}%" if room_code else ""

    insert_args = [
        first_name, first_name_wildcard,
        last_name, last_name_wildcard,
        checkin, checkout, checkin, checkout,
        room_code, room_code_wildcard,
        reservation_code, reservation_code
    ]
    cursor.execute(sql_query, insert_args)
    result = cursor.fetchall()
    result = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
    conn.commit()
    print(result)

def get_revenue(conn):
    sql_query = """
        WITH RECURSIVE date_range AS (
            SELECT DATE_FORMAT(CURDATE(), '%Y-01-01') AS dt
            UNION ALL
            SELECT DATE_ADD(dt, INTERVAL 1 DAY)
            FROM date_range
            WHERE dt < DATE_FORMAT(CURDATE(), '%Y-12-31')
        ),
        daily_revenue AS (
            SELECT
                r.RoomCode,
                r.RoomName,
                DATE_FORMAT(d.dt, '%Y-%m') AS month,
                ROUND(rsv.Rate, 0) AS daily_rate
            FROM
                date_range d
            JOIN
                hpena02.lab7_reservations rsv 
                ON d.dt >= rsv.CheckIn AND d.dt < rsv.CheckOut
            JOIN
                hpena02.lab7_rooms r 
                ON r.RoomCode = rsv.Room
        ),
        monthly_revenue AS (
            SELECT
                RoomCode,
                RoomName,
                month,
                SUM(daily_rate) AS monthly_total
            FROM
                daily_revenue
            GROUP BY
                RoomCode, RoomName, month
        )
        SELECT
            RoomCode,
            RoomName,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-01') THEN monthly_total ELSE 0 END) AS Jan,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-02') THEN monthly_total ELSE 0 END) AS Feb,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-03') THEN monthly_total ELSE 0 END) AS Mar,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-04') THEN monthly_total ELSE 0 END) AS Apr,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-05') THEN monthly_total ELSE 0 END) AS May,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-06') THEN monthly_total ELSE 0 END) AS Jun,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-07') THEN monthly_total ELSE 0 END) AS Jul,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-08') THEN monthly_total ELSE 0 END) AS Aug,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-09') THEN monthly_total ELSE 0 END) AS Sep,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-10') THEN monthly_total ELSE 0 END) AS Oct,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-11') THEN monthly_total ELSE 0 END) AS Nov,
            SUM(CASE WHEN month = DATE_FORMAT(CURDATE(), '%Y-12') THEN monthly_total ELSE 0 END) AS `Dec`,
            SUM(monthly_total) AS Total
        FROM
            monthly_revenue
        GROUP BY
            RoomCode, RoomName;
    """

    df = pd.read_sql(sql_query, conn)
    print(df)

