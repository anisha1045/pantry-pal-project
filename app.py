<<<<<<< HEAD
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import db
import json
import ast
import requests
from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Your existing constants
NUTRIENTS = ["calories", "protein", "fat", "carbs", "fiber", "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
             "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium", "zinc", "potassium", "sodium", "phosphorus"]
UNITS = ["kcal", "g", "g", "g", "g", "µg", "mg", "µg", "mg",
         "µg", "mg", "µg", "mg", "mg", "mg", "mg", "mg", "mg", "mg"]
ATTR_IDS = [208, 203, 204, 205, 291, 318, 401, 324, 323,
            430, 415, 418, 303, 301, 304, 309, 306, 307, 305]

# Initialize database
con = db.get_connection(test_mode=False)
conn = db.setup_db(con)

# Your existing nutrition function


def nutrition(eaten):
    data = {'query': eaten}
=======
from flask import Flask, request, render_template
import requests
import json
import db 
import ast
from datetime import date, timedelta


NUTRIENTS = ["calories", "protein", "fat", "carbs", "fiber", "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
 "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium", "zinc", "potassium", "sodium", "phosphorus"]
UNITS = ["kcal", "g", "g", "g", "g", "µg", "mg", "µg", "mg", "µg", "mg", "µg", "mg", "mg", "mg", "mg", "mg", "mg", "mg"]
ATTR_IDS = [208, 203, 204, 205, 291, 318, 401, 324, 323, 430, 415, 418, 303, 301, 304, 309, 306, 307, 305]

app = Flask(__name__)

con = db.get_connection(test_mode=False)
conn = db.setup_db(con)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/library')
def library():
    return render_template('library.html')

@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

@app.route('/hello')
def hello():
    print("hi")
    return "Hello from Flask!"


def get_user_id(username):
    user_info = db.get_user_info(conn, username)
    user_id = user_info['user_id']
    return user_id

@app.route('/check_user/<username>')
def check_user(username):
    # Check if a user exists in the database. Returns True if the user exists, False otherwise.
    user_exists = db.user_in_db(conn, username)
    return {'exists': user_exists}


@app.route('/one_time_setup', methods=['POST'])
def one_time_setup():

    data = request.get_json()
    username = data.get('username')
    sex = data.get('sex')
    age = data.get('age')
    allergies = data.get('allergies')
    conditions = data.get('conditions')
    medications = data.get('medications')
    restrictions = data.get('restrictions')
    nutri_goal = data.get('nutri_goal')

    #add user to USER database
    db.add_new_user(conn, username, sex, age, allergies, conditions, medications, restrictions, nutri_goal)
    
    # add their daily requirments to daily_requirments database
    user_info = db.get_user_info(conn, username)
    user_id = user_info.pop('user_id')
    user_info.pop('username')
    user_info.pop('restrictions')
    reqs = get_daily_requirement(user_info)

    real_dict = ast.literal_eval(reqs)
    print(real_dict)
    daily_reqs = real_dict['daily_requirements']
    adjustments = real_dict['adjustments']

    print("Daily Requirements:", daily_reqs)
    print("Adjustments:", adjustments)

    db.save_daily_reqs(conn, user_id, daily_reqs)
    return username, adjustments

# returns a list of nutrient values in the order of NUTRIENTS for a given meal "eaten"
@app.route('/log_meal', methods=['POST'])
def log_meal():
    data = request.get_json()
    username = data.get('username')
    meal = data.get('meal')
    nutrients = nutrition(meal)
    # get the user id from the user info db 
    user_info = db.get_user_info(username)
    user_id = user_info["user_id"]
    # add this meal to the db with add_meal()
    db.add_meal(user_id, nutrients)

# get nutritional info for a given meal
def nutrition(eaten):
    data = {
        'query' : eaten
    }
>>>>>>> main
    header = {
        'Content-Type': 'application/json',
        'x-app-id': '6b8a82ea',
        'x-app-key': 'c585212505ab717d1d2a11b2afb9da84'
    }
<<<<<<< HEAD

    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    response = requests.post(url, headers=header, data=json.dumps(data))

    if response.status_code == 200:
        full_nutrients = response.json()['foods'][0]['full_nutrients']
        data_dict = {item['attr_id']: item['value'] for item in full_nutrients}
        nutrient_vals = [data_dict.get(attr_id, None) for attr_id in ATTR_IDS]
        return nutrient_vals
    else:
        raise Exception("Failed to get nutrition data")

# Your existing daily requirement function


def get_daily_requirement(user_info):
=======
    
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    response = requests.post(url, headers=header, data=json.dumps(data))

    full_nutrients =  response.json()['foods'][0]['full_nutrients']
    data_dict = {item['attr_id']: item['value'] for item in full_nutrients}

    nutrient_vals = [data_dict.get(attr_id, None) for attr_id in ATTR_IDS]
    return nutrient_vals


# ask chat for a user's daily requirements - takes in a dict with the user's info 
def get_daily_requirement(user_info):
    print(user_info)
>>>>>>> main
    daily_requirements = [
        "calories", "protein", "fat", "carbs", "fiber",
        "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
        "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium",
        "zinc", "potassium", "sodium", "phosphorus"
    ]
<<<<<<< HEAD

    url = "https://api.openai.com/v1/chat/completions"
    api_key = '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'

=======
    url = "https://api.openai.com/v1/chat/completions"
    api_key = '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'
>>>>>>> main
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
<<<<<<< HEAD

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"Generate a dictionary of ints for daily requirements of the following: {daily_requirements} based on this user: {user_info}. Do not include units."}
=======
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"""Generate a dict of ints for daily needs of: {daily_requirements}, personalized for: {user_info}. No units.

            For any nutrient changed from standard values, also give:
            - default value
            - new value
            - short reason

            Format:
            {{
            "daily_requirements": {{}},
            "adjustments": {{
                "NutrientX": {{"default": x, "personalized": y, "explanation": "..."}}
            }}
            }}
            """}
>>>>>>> main
        ]
    }

    response = requests.post(url, headers=headers, json=data)
<<<<<<< HEAD
    returned_json = response.json()['choices'][0]['message']['content']
    return returned_json

# Meal suggestion function for web


def meal_suggestion_web(ingredients, rem_nutrients):
=======
    print("Response from OpenAI API:")
    print(response.json())

    returned_json = response.json()['choices'][0]['message']['content']
#     daily_requirements = parsed_content['daily_requirements']
# adjustments = parsed_content['adjustments']

# # Example usage
# print("Daily Requirements:", daily_requirements)
# print("Adjustments:", adjustments)
    return returned_json


@app.route('/nutrient_breakdown/<username>/<recent_days>')
def nutrient_breakdown(conn, username, recent_days=1):

    user_id = get_user_id(conn, username)

    # get the user's daily requirements
    daily_req = db.get_daily_reqs(conn, user_id)[0]

    print("DAILY REQ", daily_req)

    # remove the first two (rec_id and user_id)
    new_daily_req = daily_req[2:]
    day = date.today()
    rem_dict = {}
    for k in range(len(NUTRIENTS)):
        rem_dict[NUTRIENTS[k]] = [0, new_daily_req[k] * 7, UNITS[k]]
    for i in range(1, recent_days):
        # add up all nutrients so far
        if (i != 1):
            day = date.today() - timedelta(days=i - 1)

        print(day.isoformat())
        meals_so_far = db.get_meals_for_day(conn, user_id, day.isoformat())
        print("MEALS SO FAR", meals_so_far)
        # remove the first three (meal_id, user_id, and date)
        new_meals = [t[3:] for t in list(meals_so_far)]

        for meal in new_meals:
            for j in range(len(NUTRIENTS)):
                rem_dict[NUTRIENTS[j]][0] += meal[j] if meal[j] is not None else 0
    # display the remaining with the nutrients
    return rem_dict

def get_user_id(conn, username):
    user_info = db.get_user_info(conn, username)
    user_id = user_info['user_id']
    return user_id

@app.route('/get_meal_plan/<username>')
def get_meal_plan(conn, username):
    # ask user for things they have in their fridge
    ingredients = input("What ingredients do you have? Enter as a string separated by a comma and a single space. eg: oats, bananas, apples: ")
    # get remaining nutrients from nutri_goals
    rem_nutrients = nutrient_breakdown(conn, username, recent_days=1)
    # ask chat for:
    # suggested meal, ideal meal, a sentence of feedback regarding groceries, and tips such as what to and not to consume to maximize absorption
>>>>>>> main
    prompt = f"""
        Given these inputs:
        - Ingredients: {ingredients}
        - Nutritional requirements: {rem_nutrients}
        generate:

        1. a suggested meal given the ingredients and nutritional requirements
        2. an ideal meal for the nutritional requirements, ignoring ingredient constraints
        3. a short evaluation of the ingredients in meeting the nutritional needs
<<<<<<< HEAD
        4. 2 tips to achieve the nutritional requirements including how to achieve maximum 
=======
        4. 2 tips to achieve the nutritional requirements including how to acheive maximum 
>>>>>>> main
            absorption of needed nutrients 

        Return the response in the following JSON format:

        {{
            "suggested_meal": "<string>",
            "ideal_meal": "<string>",
            "evaluation": "<string>",
            "tips": ["<string>", "<string>"]
        }}
        """

    url = "https://api.openai.com/v1/chat/completions"
    api_key = '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'
<<<<<<< HEAD

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

=======
    
>>>>>>> main
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": prompt}
        ]
    }
<<<<<<< HEAD

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    content = response_json['choices'][0]['message']['content']
    content_dict = json.loads(content)
    return content_dict

# Simple validation functions from your original code


def validate_name(name):
    if name.isdigit():
        return False
    elif len(name) < 1 or len(name) > 50:
        return False
    return True


def sex_validation(sex):
    return sex.upper() in ["M", "F"]


def age_validation(age):
    return age.isdigit()

# ROUTES


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()

        try:
            # Basic validation
            username = data.get('username', '').strip()
            sex = data.get('sex', '').strip()
            age = data.get('age', '').strip()

            if not validate_name(username):
                return jsonify({'success': False, 'error': 'Invalid username'})

            if db.user_in_db(conn, username):
                return jsonify({'success': False, 'error': 'Username already exists'})

            if not sex_validation(sex):
                return jsonify({'success': False, 'error': 'Sex must be M or F'})

            if not age_validation(age):
                return jsonify({'success': False, 'error': 'Age must be a number'})

            # Create user
            db.add_new_user(conn,
                            username,
                            sex.upper(),
                            age,
                            data.get('allergies', ''),
                            data.get('conditions', ''),
                            data.get('restrictions', ''),
                            data.get('nutri_goal', ''))

            # Generate daily requirements
            user_info = db.get_user_info(conn, username)
            user_id = user_info['user_id']
            reqs = get_daily_requirement(user_info)
            real_dict = ast.literal_eval(reqs)
            db.save_daily_reqs(conn, user_id, real_dict)

            session['username'] = username
            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()

        if db.user_in_db(conn, username):
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'User not found'})

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])
# Camera route - integrating your team's existing camera.html


@app.route('/camera')
def camera():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('camera.html')

# Debug route to check templates


@app.route('/test-templates')
def test_templates():
    import os
    template_dir = os.path.join(app.root_path, 'templates')
    files = os.listdir(template_dir)
    return f"Template directory: {template_dir}<br>Files: {files}"

# API ENDPOINTS


@app.route('/api/log_meal', methods=['POST'])
def log_meal():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    meal_description = data.get('meal', '').strip()

    if not meal_description:
        return jsonify({'success': False, 'error': 'Meal description required'}), 400

    try:
        nutrients = nutrition(meal_description)
        username = session['username']
        user_info = db.get_user_info(conn, username)
        user_id = user_info['user_id']

        db.add_meal(conn, user_id, nutrients)
        return jsonify({'success': True, 'message': 'Meal logged successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/meal_suggestion', methods=['POST'])
def get_meal_suggestion():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    ingredients = data.get('ingredients', '').strip()

    try:
        username = session['username']
        user_id = db.get_user_info(conn, username)['user_id']

        # Get remaining nutrients
        daily_req = db.get_daily_reqs(conn, user_id)[0]
        new_daily_req = daily_req[2:]

        today = date.today().isoformat()
        meals_so_far = db.get_meals_for_today(conn, user_id, today)
        new_meals = [t[3:] for t in list(meals_so_far)]

        remaining = list(new_daily_req)
        for meal in new_meals:
            for i in range(len(remaining)):
                if meal[i] is not None:
                    remaining[i] = remaining[i] - int(meal[i])

        rem_dict = {NUTRIENTS[i]: remaining[i] for i in range(len(NUTRIENTS))}

        suggestion = meal_suggestion_web(ingredients, rem_dict)
        return jsonify({'success': True, **suggestion})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/nutrient_breakdown')
def get_nutrient_breakdown():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        username = session['username']
        user_id = db.get_user_info(conn, username)['user_id']

        daily_req = db.get_daily_reqs(conn, user_id)[0]
        new_daily_req = daily_req[2:]

        today = date.today().isoformat()
        meals_so_far = db.get_meals_for_today(conn, user_id, today)
        new_meals = [t[3:] for t in list(meals_so_far)]

        remaining = list(new_daily_req)
        for meal in new_meals:
            for i in range(len(remaining)):
                if meal[i] is not None:
                    remaining[i] = remaining[i] - int(meal[i])

        formatted_nutrients = []
        for i, nutrient in enumerate(NUTRIENTS):
            formatted_nutrients.append({
                'name': nutrient,
                'amount': remaining[i],
                'unit': UNITS[i]
            })

        return jsonify({'success': True, 'nutrients': formatted_nutrients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
=======
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()

    content = response_json['choices'][0]['message']['content']
    content_dict = json.loads(content)

    # parse whatever chat gave us
    suggested_meal = content_dict["suggested_meal"]
    ideal_meal = content_dict["ideal_meal"]
    evaluation = content_dict["evaluation"]
    tips = content_dict["tips"]

    #print suggested meal and other output to the user
    print_meal_response(suggested_meal, ideal_meal, evaluation, tips)



if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> main
