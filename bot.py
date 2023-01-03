from pymongo import MongoClient
from time import sleep
import requests

# mongodb
cluster = MongoClient("")
db = cluster['']
channels_collection = db['']
# telegram
chat_id = '@gamerpowerbot'
token = ''
api_url = "https://api.telegram.org/bot{}/".format(token)

def create_ids_list(ids_list):
	data = {
	'_id': 1,
	'ids_list': ids_list
	}
	return channels_collection.insert_one(data)

def update_ids_list(ids_list):
	data_id = {'_id': 1}
	data = {'$set':{'ids_list': ids_list}}
	return channels_collection.update_one(data_id, data)

def find_data():
	data_id = {'_id': 1}
	return channels_collection.find_one(data_id)['ids_list']

def get_response():
	r = requests.get('https://www.gamerpower.com/api/giveaways')

	if r.status_code == 200:
		response = r.json()
	else:
		response = None

	return response

def get_new_ids(current_ids, response):
	new_ids = []
	for element in response:
		if element['id'] not in current_ids:
			new_ids.append(element['id'])
	return new_ids

def send_message(api_url, chat_id, message):
	params = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
	method = 'sendMessage'
	resp = requests.post(api_url + method, params)
	return resp

def generate_message(response, new_id):
	for element in response:
		if element['id'] == new_id:
			message = f'<b><a href="{element["open_giveaway_url"]}">{element["title"]}</a>\
			\n\n{element["description"]}\n{element["gamerpower_url"]}\
			\n\nworth: {element["worth"]}\ntype: {element["type"]}\
			\nplatforms: {element["platforms"]}\nstatus: {element["status"]}\
			\nend date: {element["end_date"]}\n\nInstructions:\n{element["instructions"]}</b>'

	return message

def main():
	while True:

		response = get_response()
		current_ids = find_data()

		if response and current_ids:
			new_ids = get_new_ids(current_ids, response)
			if new_ids:
				for new_id in reversed(new_ids):
					message = generate_message(response, new_id)
					send_message(api_url, chat_id, message)
					sleep(3)
		
				new_current_ids = list(set(current_ids + new_ids))
				update_ids_list(new_current_ids)

		sleep(3600) #1 hour
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		exit()
