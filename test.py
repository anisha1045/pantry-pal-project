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
            nutri_goal="lose weight",
            daily_requirements=None
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
            nutri_goal="gain muscle",
            daily_requirements=None
        )
        # Get user_id
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM user_info WHERE username = ?", ("bob",))
        user_id = c.fetchone()[0]
        #fake values, no need for api call
        db.add_meal(
            self.conn,
            user_id=user_id,
            calories=700,
            protein=35,
            fat=20,
            carbs=80,
            fiber=8,
            vitamin_a=900, vitamin_c=60, vitamin_d=15, vitamin_e=10, vitamin_k=80,
            vitamin_b6=1.3, vitamin_b12=2.4, iron=18, calcium=1000, magnesium=400,
            zinc=11, potassium=4700, sodium=1500, phosphorus=700
        )

        meals = db.get_meals_for_user(self.conn, user_id)
        self.assertEqual(len(meals), 1)
        self.assertAlmostEqual(float(meals[0][3]), 700)  # calories
    
    def test_wrong_name(self): 
        name = "123"
        self.assertFalse(validate_name(name))

if __name__ == '__main__':
    unittest.main()