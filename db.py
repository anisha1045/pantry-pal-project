import sqlite3

def get_connection(test_mode=False):
    if test_mode:
        return sqlite3.connect(":memory:", check_same_thread=False)
    return sqlite3.connect("USER", check_same_thread=False)

def setup_db(conn):
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            sex TEXT,
            age INTEGER,
            allergies TEXT,
            conditions TEXT,
            medications TEXT,
            restrictions TEXT,
            nutri_goal TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date DATE,
            calories FLOAT,
            protein FLOAT,
            fat FLOAT,
            carbs FLOAT,
            fiber FLOAT,
            vitamin_a FLOAT,
            vitamin_c FLOAT,
            vitamin_d FLOAT,
            vitamin_e FLOAT,
            vitamin_k FLOAT,
            vitamin_b6 FLOAT,
            vitamin_b12 FLOAT,
            iron FLOAT,
            calcium FLOAT,
            magnesium FLOAT,
            zinc FLOAT,
            potassium FLOAT,
            sodium FLOAT,
            phosphorus FLOAT,
            FOREIGN KEY(user_id) REFERENCES user_info(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_requirements (
            rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            calories FLOAT,
            protein FLOAT,
            fat FLOAT,
            carbs FLOAT,
            fiber FLOAT,
            vitamin_a FLOAT,
            vitamin_c FLOAT,
            vitamin_d FLOAT,
            vitamin_e FLOAT,
            vitamin_k FLOAT,
            vitamin_b6 FLOAT,
            vitamin_b12 FLOAT,
            iron FLOAT,
            calcium FLOAT,
            magnesium FLOAT,
            zinc FLOAT,
            potassium FLOAT,
            sodium FLOAT,
            phosphorus FLOAT,
            FOREIGN KEY(user_id) REFERENCES user_info(user_id)
        )
    """)

    conn.commit()
    return conn

def user_in_db(conn, username):
    c = conn.cursor()
    c.execute("SELECT * FROM user_info WHERE username = ?", (username,))
    return c.fetchone() is not None

def add_new_user(conn, username, sex, age, allergies, conditions, medications, restrictions, nutri_goal):
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO user_info (username, sex, age, allergies, conditions, medications, restrictions, nutri_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, sex, int(age), allergies, str(conditions), medications, restrictions, nutri_goal))
        conn.commit()
    except Exception as e:
        print("Error adding user:", e)

def get_user_info(conn, username):
    c = conn.cursor()
    c.execute("SELECT * FROM user_info WHERE username = ?", (username,))
    row = c.fetchone()
    if row:
        columns = [col[0] for col in c.description]
        return dict(zip(columns, row))
    return None
    
def add_meal(conn, user_id, nutrients):
    c = conn.cursor()
    c.execute("""
        INSERT INTO meals (
            user_id, date, calories, protein, fat, carbs, fiber,
            vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_k,
            vitamin_b6, vitamin_b12, iron, calcium, magnesium,
            zinc, potassium, sodium, phosphorus
        )
        VALUES (?, CURRENT_DATE, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, *nutrients))
    conn.commit()

def get_meals_for_user(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT * FROM meals WHERE user_id = ?", (user_id,))
    return c.fetchall()

def get_meals_for_day(conn, user_id, today):
    c = conn.cursor()
    c.execute("SELECT * FROM meals WHERE user_id = ? AND date = ?", (user_id, today,))
    return c.fetchall()

def save_daily_reqs(conn, user_id, requirements_dict):
    c = conn.cursor()
    c.execute("""
        INSERT INTO daily_requirements (
            user_id, calories, protein, fat, carbs, fiber,
            vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_k,
            vitamin_b6, vitamin_b12, iron, calcium, magnesium,
            zinc, potassium, sodium, phosphorus
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        requirements_dict['calories'],
        requirements_dict['protein'],
        requirements_dict['fat'],
        requirements_dict['carbs'],
        requirements_dict['fiber'],
        requirements_dict['vitamin_a'],
        requirements_dict['vitamin_c'],
        requirements_dict['vitamin_d'],
        requirements_dict['vitamin_e'],
        requirements_dict['vitamin_k'],
        requirements_dict['vitamin_b6'],
        requirements_dict['vitamin_b12'],
        requirements_dict['iron'],
        requirements_dict['calcium'],
        requirements_dict['magnesium'],
        requirements_dict['zinc'],
        requirements_dict['potassium'],
        requirements_dict['sodium'],
        requirements_dict['phosphorus']
    ))
    conn.commit()

def get_daily_reqs(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT * FROM daily_requirements WHERE user_id = ?", (user_id,))
    return c.fetchall()