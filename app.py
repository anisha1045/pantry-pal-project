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
    header = {
        'Content-Type': 'application/json',
        'x-app-id': '6b8a82ea',
        'x-app-key': 'c585212505ab717d1d2a11b2afb9da84'
    }

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
    daily_requirements = [
        "calories", "protein", "fat", "carbs", "fiber",
        "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
        "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium",
        "zinc", "potassium", "sodium", "phosphorus"
    ]

    url = "https://api.openai.com/v1/chat/completions"
    api_key = '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'

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"Generate a dictionary of ints for daily requirements of the following: {daily_requirements} based on this user: {user_info}. Do not include units."}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    returned_json = response.json()['choices'][0]['message']['content']
    return returned_json

# Meal suggestion function for web


def meal_suggestion_web(ingredients, rem_nutrients):
    prompt = f"""
        Given these inputs:
        - Ingredients: {ingredients}
        - Nutritional requirements: {rem_nutrients}
        generate:

        1. a suggested meal given the ingredients and nutritional requirements
        2. an ideal meal for the nutritional requirements, ignoring ingredient constraints
        3. a short evaluation of the ingredients in meeting the nutritional needs
        4. 2 tips to achieve the nutritional requirements including how to achieve maximum 
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": prompt}
        ]
    }

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
