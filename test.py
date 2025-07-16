import unittest
import db 
from main import validate_name
class TestPantryPalDB(unittest.TestCase):

    def setUp(self):
        self.conn = db.get_connection(test_mode=True)
        db.setup_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_add_and_check_user(self):
        db.add_new_user(
            self.conn,
            username="Alisha",
            sex="F",
            age=28,
            allergies="none",
            conditions=0,
            restrictions="vegan",
            nutri_goal="lose weight"
        )
        self.assertTrue(db.user_in_db(self.conn, "Alisha"))
        self.assertFalse(db.user_in_db(self.conn, "bob"))

    def test_add_meal_for_user(self):
        # Add a user first
        db.add_new_user(
            self.conn,
            username="bob",
            sex="M",
            age=32,
            allergies="peanuts",
            conditions=1,
            restrictions="halal",
            nutri_goal="gain muscle"
        )
        # Get user_id
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM user_info WHERE username = ?", ("bob",))
        user_id = c.fetchone()[0]
        #fake values, no need for api call
        # nutrients = []
        nutrients = [
    700,    # calories
    35,     # protein
    20,     # fat
    80,     # carbs
    8,      # fiber
    900,    # vitamin_a
    60,     # vitamin_c
    15,     # vitamin_d
    10,     # vitamin_e
    80,     # vitamin_k
    1.3,    # vitamin_b6
    2.4,    # vitamin_b12
    18,     # iron
    1000,   # calcium
    400,    # magnesium
    11,     # zinc
    4700,   # potassium
    1500,   # sodium
    700     # phosphorus
]
        db.add_meal(
            self.conn,
            user_id=user_id,
            nutrients=nutrients
        )

        meals = db.get_meals_for_user(self.conn, user_id)
        self.assertEqual(len(meals), 1)
        self.assertAlmostEqual(float(meals[0][3]), 700)  # calories

        meals = db.get_meals_for_day(self.conn, user_id, "2025-07-14")
        print(meals)
        self.assertEqual(len(meals), 1)
        self.assertAlmostEqual(float(meals[0][3]), 700)  # calories
    

    def test_wrong_name(self): 
        name = "123"
        self.assertFalse(validate_name(name))

if __name__ == '__main__':
    unittest.main()