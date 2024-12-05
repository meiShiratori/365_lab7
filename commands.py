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
        ('{first_name}' = '' OR res.FirstName LIKE '%{first_name}%')
        AND ('{last_name}' = '' OR res.LastName LIKE '%{last_name}%')
        AND (
            ('{checkin}' = '' AND '{checkout}' = '')
            OR (res.CheckIn BETWEEN '{checkin}' AND '{checkout}')
        )
        AND ('{room_code}' = '' OR res.Room LIKE '%{room_code}%')
        AND ('{reservation_code}' = '' OR res.CODE = '{reservation_code}');
    """


    result = pd.read_sql(sql_query, conn)
    print(result)
