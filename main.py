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

nutrition("grape")

#welcome user
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t")
print("  Welcome to your Pantry Pal! Let's work together today to meet your health needs <3 ")
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t\n")
# prompt user for necessary details
name = input("Enter your name: ")
while validate_name(name) == False:
    name = input("Enter your name: ")
sex = input("Enter your sex (F / M): ")
age = input("Enter your age (number): ")
allergies = input("Do you have any allergies we should be aware of? (eg. peanuts, lactose intolerance) Enter Y / N : ")
conditions = input("Do you have any conditions we should be aware of? (eg. diabetes, heart problems)  Enter Y / N: ")
restrictions = input("Do you have any dietary restrictions? (e.g. halal/ vegan/ kosher) Enter Y / N: ")
nutri_goal = input("Enter your nutrition goal: ")

#TODO: input validation 

#TODO: save to database

#Plan of action
option = input(f"Hi {name}! Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)? ")
while (option != "m" and option != "n" and option != "q"):
    print(" EROORRRRRRRing ")
    option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)?")

if option == 'm':
    eaten = input("What did you eat today? (eg: three eggs, muffin): ")
    nutrition(eaten)
elif option == 'n':
    pass
else:
    print("Thanks for chatting with us! Bye bye!")


while (True):
    #TODO: meal suggestion or nutrition goal help
    option = input(f"Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or both(b)? ")
    while (option != 'm' and option != 'n' and option != 'q'):
        option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or quit(q)?")

    if option == 'm':
        pass
    elif option == 'n':
        pass
    else:
        print("Thanks for chatting with us! Bye bye!")