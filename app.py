app.py

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from auth import auth_bp
import db
import json
import ast
import requests
from datetime import date, timedelta
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.register_blueprint(auth_bp, url_prefix="/auth")


#config OAuth (Google sign in API)
client_id = "1157250652-tmr0ju9g9a3rb0vosg3r3v9ipi45hv86.apps.googleusercontent.com"
client_secret = "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"
redirect_uri = "http://localhost:5000/callback"

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

NUTRIENTS = ["calories", "protein", "fat", "carbs", "fiber", "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
 "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium", "zinc", "potassium", "sodium", "phosphorus"]
UNITS = ["kcal", "g", "g", "g", "g", "µg", "mg", "µg", "mg", "µg", "mg", "µg", "mg", "mg", "mg", "mg", "mg", "mg", "mg"]
ATTR_IDS = [208, 203, 204, 205, 291, 318, 401, 324, 323, 430, 415, 418, 303, 301, 304, 309, 306, 307, 305]

con = db.get_connection(test_mode=False)
conn = db.setup_db(con)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/old_dash')
def old_dash():
    return render_template('old_dash.html')

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not validate_name(username):
            return jsonify({'success': False, 'error': 'Invalid username'})

        if db.user_in_db(conn, username):
            return jsonify({'success': False, 'error': 'Username already exists'})

        # Add user with empty/default values for profile fields
        db.add_new_user(conn, username, '', '', '', '', '', '', '')

        # Save session
        session['username'] = username
        return jsonify({'success': True, 'redirect': '/one_time_setup'})

    return render_template('signup.html')


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
    # reqs = get_daily_requirement(user_info)
    # TODO: PUT THIS BACK
    daily_reqs = {'calories': 2300, 'protein': 34, 'fat': 44, 'carbs': 130, 'fiber': 15, 'vitamin_a': 600, 'vitamin_c': 45, 'vitamin_d': 600, 'vitamin_e': 11, 'vitamin_k': 55, 'vitamin_b6': 1.2, 'vitamin_b12': 2.4, 'iron': 8, 'calcium': 1300, 'magnesium': 240, 'zinc': 11, 'potassium': 4500, 'sodium': 1500, 'phosphorus': 1250}
    adjustments = {}
    # real_dict = ast.literal_eval(reqs)
    # print(real_dict)
    # daily_reqs = real_dict['daily_requirements']
    # adjustments = real_dict['adjustments']

    print("Daily Requirements:", daily_reqs)
    print("Adjustments:", adjustments)

    db.save_daily_reqs(conn, user_id, daily_reqs)
    session['username'] = username
    print("USername saved", session['username'])
    # return username, adjustments
    return jsonify({'success': True})
    # return render_template('signup.html')

# get nutritional info for a given meal
def nutrition(eaten):
    data = {
        'query' : eaten
    }
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


# ask chat for a user's daily requirements - takes in a dict with the user's info 
def get_daily_requirement(user_info):
    print(user_info)
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

        ]
    }

    response = requests.post(url, headers=headers, json=data)
    returned_json = response.json()['choices'][0]['message']['content']
    return returned_json


@app.route('/nutrient_breakdown/<recent_days>')
def get_nutrient_breakdown(recent_days=1):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    try:
        username = session['username']
        rem_dict = nutrient_breakdown(username, int(recent_days))
        return jsonify(rem_dict)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def nutrient_breakdown(username, recent_days):

    user_id = get_user_id(username)

    # get the user's daily requirements
    daily_req = db.get_daily_reqs(conn, user_id)[0]

    print("DAILY REQ", daily_req)
    print(type(daily_req), daily_req)
    new_daily_req = list(daily_req)
    print(type(new_daily_req), new_daily_req)
    print(new_daily_req[0])
    # remove the first two (rec_id and user_id)
    new_daily_req = new_daily_req[2:]
    day = date.today()
    rem_dict = {}
    for k in range(len(NUTRIENTS)):
        rem_dict[NUTRIENTS[k]] = [0, new_daily_req[k] * 7, UNITS[k]]
    print("hi")
    print("recent_days =", recent_days)
    for i in range(0, recent_days):
        # add up all nutrients so far
        print("here")
        day = date.today() - timedelta(days=i)

        print(day.isoformat())
        meals_so_far = db.get_meals_for_day(conn, user_id, day.isoformat())
        print("MEALS SO FAR", meals_so_far)
        # remove the first three (meal_id, user_id, and date)
        if (len(meals_so_far) > 0):
            new_meals = [t[3:] for t in list(meals_so_far)]
            for meal in new_meals:
                for j in range(len(NUTRIENTS)):
                    rem_dict[NUTRIENTS[j]][0] += meal[j] if meal[j] is not None else 0

    # display the remaining with the nutrients
    print(rem_dict)
    return rem_dict



@app.route('/api/meal_suggestion', methods=['POST'])
def get_meal_plan():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    ingredients = data.get('ingredients', '').strip()

    try:
        username = session['username']
        # get remaining nutrients from nutri_goals
        rem_nutrients = nutrient_breakdown(username, recent_days=1)
        print("REM NUTRIENTS", rem_nutrients)
        # ask chat for:
        # suggested meal, ideal meal, a sentence of feedback regarding groceries, and tips such as what to and not to consume to maximize absorption
        prompt = f"""
            Given these inputs:
            - Ingredients: {ingredients}
            - Nutritional requirements: {rem_nutrients}
            generate:

            1. a suggested meal given the ingredients and nutritional requirements
            2. an ideal meal for the nutritional requirements, ignoring ingredient constraints
            3. a short evaluation of the ingredients in meeting the nutritional needs and specific ingredients to buy to fulfill the specific nutritional requirements
            5. 2 tips to achieve the nutritional requirements including how to achieve maximum 
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
        # TODO: comment this back in
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        print(content)
        if isinstance(content, str):
            content = json.loads(content)
        return jsonify({'success': True, **content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
                            data.get('medications', ''),
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


@app.route('/log_meal', methods=['POST'])
def log_meal():
    print("IN LOG MEAL")
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()

    print("Received meal data:", data)

    meal_string_parts = []
    for food, qty in data.items():
        part = f"{qty} {food}".strip() if qty else food
        meal_string_parts.append(part)

    meal_description = ', '.join(meal_string_parts)
    print("Meal string:", meal_description)

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


@app.route('/identify_food', methods=['POST'])
def identify_food():
    print("identifying food")
    if 'mealImage' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['mealImage']
    file_bytes = file.read()
    # Your PAT (Personal Access Token) can be found in the Account's Security section
    PAT = '1e5f77d736174440b16593d07b98a512'
    # Specify the correct user_id/app_id pairings
    # Since you're making inferences outside your app's scope
    USER_ID = 'clarifai'
    APP_ID = 'main'
    # Change these to whatever model and image URL you want to use
    MODEL_ID = 'food-item-recognition'
    MODEL_VERSION_ID = '1d5fd481e0cf4826aa72ec3ff049e044'
    IMAGE_URL = 'https://samples.clarifai.com/food.jpg'

    from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
    from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
    from clarifai_grpc.grpc.api.status import status_code_pb2

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ]
            
        ),
        metadata=metadata,
        timeout=10  # seconds
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    print("Predicted concepts:")
    index = 5
    for concept in output.data.concepts:
        if (index == 0):
            break
        print("%s %.2f" % (concept.name, concept.value))
        index -= 1

    filtered_concepts = [
    {"name": concept.name, "value": concept.value}
    for concept in output.data.concepts
    if concept.value > 0.5
]

    return jsonify(predicted_concepts=filtered_concepts)

        

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#debugging purposes
@app.route('/debug-routes')
def debug_routes():
    return "<br>".join([str(rule) for rule in app.url_map.iter_rules()])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    

