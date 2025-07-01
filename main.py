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

def meal_suggestion():
    pass

def nutri_goals():
    pass

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
    print(response.json())

# ask chat for a user's daily requirements - takes in a dict with the user's info 
def get_daily_requirement(user_info):
    # TO DO: make get_user_info return a dict
    user_info.pop('user_id')
    user_info.pop('username')
    user_info.pop('allergies')
    user_info.pop('daily_requirements')

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
            {"role": "system", "content": f"Generate a dictionary for daily requirements of the following: {daily_requirements} based on this user: {user_info}"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    # string is in the format of a dictionary
    returned_string = response.json()['choices']['message']['content']

#welcome user
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t")
print("  Welcome to your Pantry Pal! Let's work together today to meet your health needs <3 ")
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t\n")


# set up database and connection

conn = db.get_connection(test_mode=True)
db.setup_db(conn)
db.add_new_user(
            conn,
            username="Alisha",
            sex="F",
            age=28,
            allergies="none",
            conditions=0,
            restrictions="vegan",
            nutri_goal="lose weight",
            daily_requirements=None
        )
user_info = db.get_user_info(conn, "Alisha")
print(user_info)
get_daily_requirement(user_info)


# first_time = input("Is this your first time with us? Enter Y / N: ")
# if (first_time):
#     print("Yay, we're so glad you're here!")
#     username = input("To start, please enter a username: ")
#     while validate_name(username) == False and user_in_db(username):
#         if (user_in_db(username)):
#             username = input("That username was already taken. Please try again: ")
#         else:
#             username = input("You inputted an invalid username. Please try again: ")
#     sex = input("Enter your sex (F / M): ")
#     age = input("Enter your age (number): ")
#     allergies = input("Do you have any allergies we should be aware of? (eg. peanuts, lactose intolerance) Enter Y / N : ")
#     conditions = input("Do you have any conditions we should be aware of? (eg. diabetes, heart problems)  Enter Y / N: ")
#     restrictions = input("Do you have any dietary restrictions? (e.g. halal/ vegan/ kosher) Enter Y / N: ")
#     nutri_goal = input("Enter your nutrition goal: ")
#     add_new_user(username, sex, age, allergies, conditions, restrictions, nutri_goal, None)
# else: 
#     username = input("Please enter your username: ")
#     if (not user_in_db):
#         print("{username} was not found. Please try again.")
#     else:
#         print(f"Welcome back! It's great to see you, {username}")

    
# # prompt user for necessary details

# #TODO: input validation 

# #TODO: save to database

# #Plan of action
# keep_going = True
# option = input(f"Hi {username}! Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)? ")
# while (option != "m" and option != "n" and option != "q"):
#     print(" EROORRRRRRRing ")
#     option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)?")

# if option == 'm':
#     eaten = input("What did you eat today? (eg: three eggs, muffin): ")
#     nutrition(eaten)
# elif option == 'n':
#     pass
# else:
#     print("Thanks for chatting with us! Bye bye!")
#     keep_going = False


# while (keep_going):
#     #TODO: meal suggestion or nutrition goal help
#     option = input(f"Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or both(b)? ")
#     while (option != 'm' and option != 'n' and option != 'q'):
#         option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)?")

#     if option == 'm':
#         pass
#     elif option == 'n':
#         pass
#     else:
#         print("Thanks for chatting with us! Bye bye!")
#         break