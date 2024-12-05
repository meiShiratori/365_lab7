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


def get_revenue(conn):
    sql_query = """
        WITH RECURSIVE date_range AS (
            SELECT '2024-01-01' AS dt
            UNION ALL
            SELECT DATE_ADD(dt, INTERVAL 1 DAY)
            FROM date_range
            WHERE dt < '2024-12-31'
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
                hpena02.lab7_reservations rsv ON d.dt >= rsv.CheckIn AND d.dt < rsv.CheckOut
            JOIN
                hpena02.lab7_rooms r ON r.RoomCode = rsv.Room
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
            SUM(CASE WHEN month = '2024-01' THEN monthly_total ELSE 0 END) AS Jan,
            SUM(CASE WHEN month = '2024-02' THEN monthly_total ELSE 0 END) AS Feb,
            SUM(CASE WHEN month = '2024-03' THEN monthly_total ELSE 0 END) AS Mar,
            SUM(CASE WHEN month = '2024-04' THEN monthly_total ELSE 0 END) AS Apr,
            SUM(CASE WHEN month = '2024-05' THEN monthly_total ELSE 0 END) AS May,
            SUM(CASE WHEN month = '2024-06' THEN monthly_total ELSE 0 END) AS Jun,
            SUM(CASE WHEN month = '2024-07' THEN monthly_total ELSE 0 END) AS Jul,
            SUM(CASE WHEN month = '2024-08' THEN monthly_total ELSE 0 END) AS Aug,
            SUM(CASE WHEN month = '2024-09' THEN monthly_total ELSE 0 END) AS Sep,
            SUM(CASE WHEN month = '2024-10' THEN monthly_total ELSE 0 END) AS Oct,
            SUM(CASE WHEN month = '2024-11' THEN monthly_total ELSE 0 END) AS Nov,
            SUM(CASE WHEN month = '2024-12' THEN monthly_total ELSE 0 END) AS Dec,
            SUM(monthly_total) AS Total
        FROM
            monthly_revenue
        GROUP BY
            RoomCode, RoomName
        WITH ROLLUP;
    """

    df = pd.read_sql(sql_query, conn)
    print(df)