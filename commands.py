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

