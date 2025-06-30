import sqlite3


conn = sqlite3.connect('USER_INFO')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS user_info (
        username TEXT PRIMARY KEY,
        sex TEXT,
        age INTEGER,
        allergies TEXT,
        conditions INTEGER,
        restrictions TEXT,
        nutri_goal TEXT,
        daily_requirements TEXT
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS daily_requirements (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, 
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
        FOREIGN KEY(username) REFERENCES user_info(username)
    )
""")

def user_in_db(username):
    c.execute(f"SELECT * from user_info WHERE username = ?", (username,))
    conn.commit()
    rows = c.fetchall()

    for row in rows:
        print(row)
    return c.fetchall() == None
        

def add_new_user(username, sex, age, allergies, conditions, restrictions, nutri_goal, daily_requirements):
    c.execute("""
        INSERT INTO user_info (username, sex, age, allergies, conditions, restrictions, nutri_goal, daily_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, sex, age, allergies, conditions, restrictions, nutri_goal, daily_requirements))
    conn.commit()
    rows = c.fetchall()

    for row in rows:
        print(row)
    return user_in_db(username)


def add_meal(username, calories, protein, fat, carbs, fiber, vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_k,
    vitamin_b6, vitamin_b12, iron, calcium, magnesium, zinc, potassium, sodium, phosphorus):
    print("IN ADD MEAL")
    c.execute("""
        INSERT INTO daily_requirements (
            username, calories, protein, fat, carbs, fiber,
            vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_k,
            vitamin_b6, vitamin_b12, iron, calcium, magnesium,
            zinc, potassium, sodium, phosphorus
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username, calories, protein, fat, carbs, fiber,
        vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_k,
        vitamin_b6, vitamin_b12, iron, calcium, magnesium,
        zinc, potassium, sodium, phosphorus
    ))
    conn.commit()
    rows = c.fetchall()

    for row in rows:
        print("ROW")
        print(row)

def close():
    conn.close()

