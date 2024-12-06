import pandas as pd

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


    result = pd.read_sql(sql_query, conn)
    print(result)
