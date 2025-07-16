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
    header = {
        'Content-Type': 'application/json',
        'x-app-id': '6b8a82ea',
        'x-app-key': 'c585212505ab717d1d2a11b2afb9da84'
    }
    
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    response = requests.post(url, headers=header, data=json.dumps(data))

    full_nutrients =  response.json()['foods'][0]['full_nutrients']
    data_dict = {item['attr_id']: item['value'] for item in full_nutrients}

    nutrient_vals = [data_dict.get(attr_id, None) for attr_id in ATTR_IDS]
    return nutrient_vals


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
    prompt = f"""
        Given these inputs:
        - Ingredients: {ingredients}
        - Nutritional requirements: {rem_nutrients}
        generate:

        1. a suggested meal given the ingredients and nutritional requirements
        2. an ideal meal for the nutritional requirements, ignoring ingredient constraints
        3. a short evaluation of the ingredients in meeting the nutritional needs
        4. 2 tips to achieve the nutritional requirements including how to acheive maximum 
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
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": prompt}
        ]
    }
    
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