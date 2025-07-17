# Since auth.py calls app.py and app.py calls auth.py we need a shared module 
# that both can import without circular dependencies.
import db

con = db.get_connection(test_mode=False)
conn = db.setup_db(con)
