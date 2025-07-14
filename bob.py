    
import ast
reqs = "{'daily_requirements': {'calories': 2000, 'protein': 46, 'fat': 78, 'carbs': 310, 'fiber': 25, 'vitamin_a': 700, 'vitamin_c': 75, 'vitamin_d': 15, 'vitamin_e': 15, 'vitamin_k': 90, 'vitamin_b6': 1.3, 'vitamin_b12': 2.4, 'iron': 18, 'calcium': 1000, 'magnesium': 310, 'zinc': 8, 'potassium': 4700, 'sodium': 2300, 'phosphorus': 700}, 'adjustments': {'iron': {'default': 18, 'personalized': 27, 'explanation': 'Higher iron needs for anemia'}, 'protein': {'default': 46, 'personalized': 60, 'explanation': 'Increased protein for muscle building'}}}"""
real_dict = ast.literal_eval(reqs)
print(real_dict)
daily_reqs = real_dict['daily_requirements']
adjustments = real_dict['adjustments']

print("Daily Requirements:", daily_reqs)
print("Adjustments:", adjustments)