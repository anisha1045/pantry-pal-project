import requests
import json
import re 
# url = "https://www.britelink.io/api/v1/food_interactions"
api_key = 'secret_699038a1-a1de-4f70-8e63-308f2c8caf48'

headers = {
    "Authorization": f"Bearer {api_key}",
}

while (True):
    drug_name = input("Please enter the generic drug name of your medicine: ")
    url = f"https://www.britelink.io/api/v1/food_interactions?n={drug_name}&exact=true"
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        break
    elif r.status_code == 404:
        print("""Sorry, we don't recognize that drug. Please try using the generic drug name instead of brand name. For example, use “ibuprofen” instead of “Advil”.""")

data = r.json()

# parse output to get advice
advice = None
for drug in data['foodInteractions']:
    for interaction in drug['interactions']:
        if interaction != []:
            advice = interaction['advice']
            break
    if advice:
        break

# clean the advice string
advice = re.sub(r'\.\s*,', '.', advice)
if advice: 
    print(advice)
else: 
    print(f"No advice for {drug_name}.")