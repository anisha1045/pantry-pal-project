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
'''

def validate_string_input(user_input):
    if (type(user_input) != str):
        return False
    
def meal_suggestion():
    pass

def nutri_goals():
    pass
    


#welcome user
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t")
print("  Welcome to your Pantry Pal! Let's work together today to meet your health needs <3 ")
print(" *\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t*\t\n")
# prompt user for necessary details
name = input("Enter your name: ")
while not validate_string_input(name):
    name = input("Enter your name: ")
sex = input("Enter your age: ")
age = input("Enter your age: ")
allergies = input("Do you have any allergies we should be aware of eg. peanuts, lactose intolerance: ")
conditions = input("Do you have any conditions we should be aware of eg. diabetes, heart problems: ")
restrictions = input("Enter your dietary restrictions: ")
cuisine = input("Enter your cuisine preference: ")
nutri_goal = input("Enter your nutrition goal: ")

#TODO: input validation 

#TODO: save to database

#Plan of action
option = input(f"Hi {name}! Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or both(b)? ")
while (option != 'm' and option != 'n' and option != 'q'):
    option = input("Invalid input. Please try again. Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or both(b)?")

if option == 'm':
    pass
elif option == 'n':
    pass
elif option == 'q':
    print("Thanks for chatting with us! Bye bye!")


while (True):
    #TODO: meal suggestion or nutrition goal help
    option = input(f"Would you like a meal suggestion (m) or help meeting nutrition goals (n) for today? Or both(b)? ")
    if option == 'm':
        pass
    elif option == 'n':
        pass
    elif option == 'q':
        print("Thanks for chatting with us! Bye bye!")
        break
    else:
        print("")