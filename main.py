'''
This program runs a nutrition helper app that is customized to a user's needs.

Authors: Yara Shobut and Anisha Bhaskar Torres
'''
import requests
import json
import db 
import ast
from datetime import date, timedelta

NUTRIENTS = ["calories", "protein", "fat", "carbs", "fiber", "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
 "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium", "zinc", "potassium", "sodium", "phosphorus"]
UNITS = ["kcal", "g", "g", "g", "g", "µg", "mg", "µg", "mg", "µg", "mg", "µg", "mg", "mg", "mg", "mg", "mg", "mg", "mg"]
ATTR_IDS = [208, 203, 204, 205, 291, 318, 401, 324, 323, 430, 415, 418, 303, 301, 304, 309, 306, 307, 305]

def validate_name(name):
    if (name.isdigit()):
        return False
    elif (len(name)<1 or len(name)>50):
        return False
    return True 

def sex_validation(sex):
    if (sex != "M" and sex != "F" and sex != "f" and sex != "m"):
        return False
    return True

def age_validation(age):
    if (age.isdigit() == False):
        return False
    return True 

def open_ended_validation(user_input):
    if (user_input.isdigit()):
        return False 
    elif (user_input != 'Y' and user_input != 'N' and user_input != 'y' and user_input != 'n'):
        return False
    return True

def meal_suggestion(conn):
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
    
# print response to user
def print_meal_response(suggested_meal, ideal_meal, evaluation, tips):
    divider = "~" * 60

    plate = r"""
            (っ◔◡◔)っ ♥  Meal Suggestion ♥
            ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
            ┃       🥗  🐔  🍞  🥚  🍊       ┃
            ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
    """

    stars = r"✧･ﾟ: *✧･ﾟ:* 　　 *:･ﾟ✧*:･ﾟ✧"

    print(divider)
    print(plate)
    print("Suggested Meal:")
    print(f"  🍽️  {suggested_meal}\n")

    print(divider)
    print("Ideal Meal (if your pantry was magic ✨):")
    print(f"  🧑‍🍳  {ideal_meal}\n")

    print(divider)
    print("Pantry Pal's Thoughts 💭")
    print(f"  📝  {evaluation}\n")

    print(divider)
    print("Tips for You 🌱")
    for i, tip in enumerate(tips, 1):
        print(f"  💡 Tip {i}: {tip}")
    print(stars)

def print_nutrient_breakdown(rem_dict):
    divider = "~" * 60
    hearts_banner = "♥" * 10 + " Remaining Nutrients " + "♥" * 10
    stars = r"✧･ﾟ: *✧･ﾟ:* 　　 *:･ﾟ✧*:･ﾟ✧"

    print(hearts_banner.center(len(divider)))
    print(divider)
    for i in range(len(NUTRIENTS)):
        nutrient = NUTRIENTS[i]
        amount = rem_dict[nutrient]
        unit = UNITS[i]
        print(f"  ♥ {nutrient:<15} : {amount:>6} {unit}")

    print(divider)
    print(stars)

# returns a dict of keys (nutrients) and values (a tuple with consumed amount, required amount, and unit)
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

# returns a list of nutrient values in the order of NUTRIENTS for a given meal "eaten"
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
    
def one_time_setup(conn):
    print("Yay, we're so glad you're here!")
    #get username
    username = input("To start, please enter a username: ")
    user_in_db = db.user_in_db(conn, username)
    while ((not validate_name(username)) or (user_in_db)):
        if (user_in_db):
            username = input("That username was already taken. Please try again: ")
            user_in_db = db.user_in_db(conn, username)
        else:
            username = input("Username input invalid. Please try again: ")
        
    #get sex
    sex = input("Enter your sex (F / M): ") 
    while sex_validation(sex) == False:
        sex = input("Wrong format inputted, please enter F or M: ")

    # get age 
    age = input("Enter your age (number): ")
    while age_validation(age) == False:
        age = input("Age input invalid, please try again (insert digits): ")

    #get allergies
    allergies = input("Do you have any allergies we should be aware of? (eg. peanuts) Enter y / n : ")
    while open_ended_validation(allergies) == False:
        allergies = input("Allergy input is invalid, please try again: ")
    if allergies == "Y" or allergies == "y":
        allergies = input("What are you allergic to? ")

    #get conditions
    conditions = input("Do you have any conditions we should be aware of? (eg. diabetes, heart problems)  Enter y / n: ")
    while open_ended_validation(conditions) == False:
        conditions = input("Conditions input is invalid, please try again: ")
    if conditions == "Y" or conditions == "y":
        conditions = input("What are your conditions? ")

    #get medications
    medications = input("Are you on any regular medications? (eg. aspirin)  Enter y / n: ")
    while open_ended_validation(conditions) == False:
        medications = input("Medication input is invalid, please try again: ")
    if medications == "Y" or medications == "y":
        medications = input("What medications are you taking? ")

    #get restrictions
    restrictions = input("Do you have any dietary restrictions? (e.g. halal/ vegan/ kosher) Enter y / n: ")
    while open_ended_validation(restrictions) == False:
        restrictions = input("Restrictions input is invalid, please try again: ")
    if restrictions == "Y" or restrictions == "y":
        restrictions = input("What are your restrictions? ")

    #get nutrition goals 
    nutri_goal = input("Enter your nutrition goal: ")

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

def log_meal(conn, username, user_ate):
    if (not user_ate):
        log = input("Have you had anything to eat today? y / n: ")
    else:
        log = input("Have you had anything else to eat today? y / n: ")
    while (log != "y" and log != "Y" and log != "n" and log != "N"):
        if (not user_ate):
            log = input("Invalid input, please try again. Have you had anything to eat today? y / n: ")
        else:
            log = input("Invalid input, please try again. Have you had anything else to eat today? y / n: ")
    if (log == "y" or log == "Y"):
        user_ate = True
        meal = input("What did you eat today? (eg: three eggs, one muffin): ")
        nutrients = nutrition(meal)
        # get the user id from the user info db 
        user_info = db.get_user_info(conn, username)
        user_id = user_info["user_id"]
        # add this meal to the db with add_meal()
        db.add_meal(conn, user_id, nutrients)
        meals = db.get_meals_for_user(conn, user_id)
        print("MEALS")
        print(meals)
    return user_ate
    

def say_goodbye():
    goodbye = r"""
   ・。.・゜✭・.・✫・゜・。. ✧･ﾟ: *✧･ﾟ:* ✫*:･ﾟ✧*:･ﾟ✧ .・。.・゜✭・.・✫

          (｡♥‿♥｡) Thanks for using Pantry Pal!
          Wishing you health & good meals ✿
               ✦ See you again soon! ✦

   .・。.・゜✭・.・✫・゜・。. ✧･ﾟ: *✧･ﾟ:* ✫*:･ﾟ✧*:･ﾟ✧ .・。.・゜✭・.・✫
    """
    print(goodbye)

# MAIN PROGRAM HERE
# welcome user
divider = "~" * 60
hearts_banner = r"""
   .・。.・゜✭・.・✫・゜・。. ♥ Welcome to Pantry Pal! ♥ .・。.・゜✫・.・✭・゜・。.
"""
print(hearts_banner)

# set up database and connection
con = db.get_connection(test_mode=False)
conn = db.setup_db(con)

#connect user to account / their saved profile
while (True):
    first_time = input("\nIs this your first time with us? Enter y / n: ")
    while (first_time != 'y' and first_time != "Y" and first_time != "n" and first_time != "N"):
        first_time = input("Invalid input, please try again. Is this your first time with us? Enter y / n: ")
    if (first_time == "y" or first_time == "Y"):
        username = one_time_setup(conn)
        break
    else: 
        username = input("Please enter your username: ")
        if (not db.user_in_db(conn, username)):
            print("{username} was not found. Please try again.")
        else:
            print(f"Welcome back! It's great to see you, {username}!")
            break
user_ate = False
while (True):
    option = input(f"\nWould you like a meal suggestion (m), or a breakdown of your remaining nutritional requirements today (n), or to quit (q)? ")
    while (option != "m" and option != "n" and option != "q"):
        option = input("Invalid input. Please try again. Would you like a meal suggestion (m), or a breakdown of your remaining nutritional requirements today (n), or to quit (q)? ")

    if (option == "q"):
       say_goodbye()
       break
    else:
        user_ate = log_meal(conn, username, user_ate)
        if option == "m":
            meal_suggestion(conn)
        elif option == "n":
            rem_dict = nutrient_breakdown(conn, username)
            print()
            print("REM DICT: ", rem_dict)
            # print_nutrient_breakdown(rem_dict)

            print("WEEKLY BREAKDOWN")

            rem_dict = nutrient_breakdown(conn, username, 7)
            print("REM DICT: ", rem_dict)
            print()
            # print_nutrient_breakdown(rem_dict)