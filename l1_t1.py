import requests
import json
from pprint import pprint

user_name = "Gerald16311"
url = f"https://api.github.com/users/{user_name}/repos"

response = requests.get(url)
j_data = response.json()

with open('parsed_data.json', 'w') as outfile:
    json.dump(j_data, outfile)

print(f'У пользователя {user_name} есть вот такой список репозиториев:')
for item in j_data:
    print(item['name'])
