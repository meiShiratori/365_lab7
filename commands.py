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

def reserve_room(conn):
    room_code = input("Room Code (Enter or \"Any\" for no preference): ")
    bed_type = input("Bed Type (Enter or \"Any\" for no preference): ")
    check_in = input("Check-In Date (YYYY-MM-DD): ")
    check_out = input("Check-Out Date (YYYY-MM-DD): ")
    guest_count = int(input("Number of Children: ")) + int(input("Number of Adult: "))
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
    print(args)
    cursor.execute(sql_query, args)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
   
    df = pd.DataFrame(result, columns=columns)

    print(df)


