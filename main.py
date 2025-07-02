'''
Prompt user for name, sex, age, conditions, dietary restrictions, cuisine preference, nutrition goal
Save to table_1 
Prompt user for meal suggestion
    Prompt what they have in their pantry 
Prompt user for nutritional requirements left for the day
    Prompt user to enter meals eaten
    Send meal to Nutritionix API
Store nutritional info in DB 
Call openAI API chat endpoint to clean the user input and structure it in accordance to our schema/info we’re looking for 
Save to a table_2 (stores nutritional info for a user)
Output to user in command line a library that beautifies cmdline text

https://trackapi.nutritionix.com/v2/natural/nutrients
'''
import requests
import json
import db 
import ast
from datetime import date

NUTRIENTS = ["calories", "protein", "fat", "carbs", "fiber", "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
 "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium", "zinc", "potassium", "sodium", "phosphorus"]
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
    ingredients = input("What ingredients do you have? Enter as a string separated by a single space. eg: oats, bananas, apples: ")
    # get remaining nutrients from nutri_goals
    rem_nutrients = nutrient_breakdown(conn, username)
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
    4. 2 tips to achieve the nutritional requirements, including 

    Return the response in the following JSON format:

    {
    "suggested_meal": "<string>",
    "ideal_meal": "<string>",
    "evaluation": "<string>",
    "tips": ["<string>", "<string>"]
    }
    """
    pass


def nutrient_breakdown(conn, username):

    user_id = get_user_id(conn, username)

    # get the user's daily requirements
    daily_req = db.get_daily_reqs(conn, user_id)[0]
    print(daily_req)

    # remove the first two (rec_id and user_id)
    new_daily_req = daily_req[2:]
    # add up all nutrients so far
    today = date.today().isoformat()
    meals_so_far = db.get_meals_for_today(conn, user_id, today)
    print(meals_so_far)

    # remove the first three (meal_id, user_id, and date)
    new_meals = [t[3:] for t in list(meals_so_far)]

    # subtract and return
    remaining = list(new_daily_req)
    for meal in new_meals:
        for i in range(len(remaining)):
            remaining[i] = remaining[i] - meal[i]

    print(remaining)
    # display the remaining with the nutrients


def get_user_id(conn, username):
    user_info = db.get_user_info(conn, username)
    user_id = user_info["user_id"]
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
    # print(response.json())
    full_nutrients =  response.json()['foods'][0]['full_nutrients']
    data_dict = {item['attr_id']: item['value'] for item in full_nutrients}

    nutrient_vals = [data_dict.get(attr_id, None) for attr_id in ATTR_IDS]
    return nutrient_vals


# ask chat for a user's daily requirements - takes in a dict with the user's info 
def get_daily_requirement(user_info):
    # TO DO: make get_user_info return a dict
    user_info.pop('user_id')
    user_info.pop('username')
    user_info.pop('allergies')

    # daily_requirements = [
    #     "calories", "protein", "fat", "carbs", "fiber",
    #     "vitamin_a", "vitamin_c", "vitamin_d", "vitamin_e", "vitamin_k",
    #     "vitamin_b6", "vitamin_b12", "iron", "calcium", "magnesium",
    #     "zinc", "potassium", "sodium", "phosphorus"
    # ]
    # url = "https://api.openai.com/v1/chat/completions"
    # api_key = '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'
    # headers = {
    #     "Authorization": f"Bearer {api_key}",
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "model": "gpt-3.5-turbo",
    #     "messages": [
    #         {"role": "system", "content": f"Generate a dictionary for daily requirements of the following: {daily_requirements} based on this user: {user_info}"}
    #     ]
    # }
    #TODO: write system message in chat array explaining the assistant is a nutrition expert 

    #response = requests.post(url, headers=headers, json=data)
    #print(response.json())
    # string is in the format of a dictionary
    returned_json = {
        'choices': [
            {
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': """{
        'calories': 1600,
        'protein': 60,
        'fat': 40,
        'carbs': 200,
        'fiber': 30,
        'vitamin_a': 700,
        'vitamin_c': 75,
        'vitamin_d': 600,
        'vitamin_e': 15,
        'vitamin_k': 90,
        'vitamin_b6': 1.3,
        'vitamin_b12': 2.4,
        'iron': 18,
        'calcium': 1000,
        'magnesium': 310,
        'zinc': 8,
        'potassium': 4700,
        'sodium': 2300,
        'phosphorus': 700
    }"""
                },
                'refusal': None,
                'annotations': []
            }
        ],
        'id': 'chatcmpl-Box05FwrwbxeUprF3jxJdFRGZouNJ',
        'object': 'chat.completion',
        'created': 1751482897,
        'model': 'gpt-3.5-turbo-0125',
        'usage': {
            'prompt_tokens': 140,
            'completion_tokens': 169,
            'total_tokens': 309,
            'prompt_tokens_details': {'cached_tokens': 0, 'audio_tokens': 0},
            'completion_tokens_details': {
                'reasoning_tokens': 0,
                'audio_tokens': 0,
                'accepted_prediction_tokens': 0,
                'rejected_prediction_tokens': 0
            }
        },
        'service_tier': 'default',
        'system_fingerprint': None
    }

    
    #returned_json = response.json()['choices'][0]['message']['content']
    #return returned_json
    
    return returned_json['choices'][0]['message']['content']


#welcome user
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t")
print("  Welcome to your Pantry Pal! Let's work together today to meet your health needs <3 ")
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t\n")


# set up database and connection
con = db.get_connection(test_mode=False)
conn = db.setup_db(con)
db.add_new_user(
            conn,
            username="Alisha",
            sex="F",
            age=28,
            allergies="none",
            conditions=0,
            restrictions="vegan",
            nutri_goal="lose weight"
        )
user_info = db.get_user_info(conn, "Alisha")
print(user_info)


username = "Alisha"

first_time = input("Is this your first time with us? Enter Y / N: ")
if (first_time == "y" or first_time == "Y"):
    print("Yay, we're so glad you're here!")
    #get username
    username = input("To start, please enter a username: ")
    while validate_name(username) == False and db.user_in_db(conn, username):
        if (db.user_in_db(conn, username)):
            username = input("That username was already taken. Please try again: ")
        else:
            username = input("You inputted an invalid username. Please try again: ")

        
    #get sex
    sex = input("Enter your sex (F / M): ") 
    while sex_validation(sex) == False:
        sex = input("Wrong format inputted, please enter F or M: ")

    # get age 
    age = input("Enter your age (number): ")
    while age_validation(age) == False:
        age = input("Age input invalid, please try again (insert digits): ")

    #get allergies
    allergies = input("Do you have any allergies we should be aware of? (eg. peanuts) Enter Y / N : ")
    while open_ended_validation(allergies) == False:
        allergies = input("Allergy input is invalid, please try again: ")
    if allergies == "Y" or allergies == "y":
        allergies = input("What are you allergic to? ")

    #get conditions
    conditions = input("Do you have any conditions we should be aware of? (eg. diabetes, heart problems)  Enter Y / N: ")
    while open_ended_validation(conditions) == False:
        conditions = input("Conditions input is invalid, please try again: ")
    if conditions == "Y" or conditions == "y":
        conditions = input("What are your conditions? ")

    #get restrictions
    restrictions = input("Do you have any dietary restrictions? (e.g. halal/ vegan/ kosher) Enter Y / N: ")
    while open_ended_validation(restrictions) == False:
        restrictions = input("Restrictions input is invalid, please try again: ")
    if restrictions == "Y" or restrictions == "y":
        restrictions = input("What are your restrictions? ")

    #get nutrition goals 
    nutri_goal = input("Enter your nutrition goal: ")

    #add user to USER database
    db.add_new_user(conn, username, sex, age, allergies, conditions, restrictions, nutri_goal, None)
    
    # add their daily requirments to daily_requirments database
    user_info = db.get_user_info(conn, username)
    reqs = get_daily_requirement(user_info)
    real_dict = ast.literal_eval(reqs)
    user_id = user_info["user_id"]
    db.save_daily_reqs(conn, user_id, real_dict)

else: 
    # TODO: NEED TO FIX THIS AS WELL AS ERROR HANDLING ABOVE
    username = input("Please enter your username: ")
    if (not db.user_in_db(conn, username)):
        print("{username} was not found. Please try again.")
    else:
        print(f"Welcome back! It's great to see you, {username}")



keep_going = True
option = input(f"Hi {username}! Would you like a meal suggestion (m), or a breakdown of your remaining nutritional requirements today (n), or to quit (q)?")
while (option != "m" and option != "n" and option != "q"):
    print("EROORRRRRRR!")
    option = input("Invalid input. Please try again. Would you like a meal suggestion (m), or a breakdown of your remaining nutritional requirements today (n), or to quit (q)?")

user_ate = False
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
    print(nutrients)
    # get the user id from the user info db 
    user_info = db.get_user_info(conn, username)
    user_id = user_info["user_id"]
    # add this meal to the db with add_meal()
    print(nutrients)
    db.add_meal(conn, user_id, nutrients)
    

if option == "m":
    meal_suggestion()
    pass
elif option == "n":
    nutrient_breakdown(conn, username)
    pass
else:
    print("Thanks for chatting with us! Bye bye!")
    keep_going = False


while (keep_going):
    #TODO: meal suggestion or nutrition goal help
    option = input(f"Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)? ")
    while (option != 'm' and option != 'n' and option != 'q'):
        option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)?")

if option == "m":
    meal_suggestion()
    pass
elif option == "n":
    nutrient_breakdown(conn, username)
    pass
else:
    print("Thanks for chatting with us! Bye bye!")
    keep_going = False
