import json
import sys

current_data = {}
with open(sys.argv[1]) as f:
	json_file = json.load(f)

	current_data['code'] = json_file["code"]
	current_data['min_hours'] = json_file["min_hours"]
	current_data['max_hours'] = json_file["max_hours"]
	current_data['classes'] = json_file["classes"]
	current_data['final_class'] = json_file["final_class"]

with open(sys.argv[2]) as f:
	data = json.load(f)
	semester = sys.argv[2].split('_')[0]
	campus = sys.argv[2].split('_')[1][:-5]
	
	for course in data[campus]:
		class_code = course[0]
		try:
			_class = current_data['classes'][class_code]
			print(class_code)
			current_data['classes'][class_code]['schedule'] = []
		except:
			continue

		schedule = []
		for option in course[3]:
			schedule.append(option[7])
		current_data['classes'][class_code]['schedule'].append(schedule)

with open(sys.argv[1], 'w') as f:
	json_file = {
		'code': current_data['code'],
		'min_hours': current_data['min_hours'],
		'max_hours': current_data['max_hours'],
		'classes': current_data['classes'],
		'final_class': current_data['final_class']
	}

	json.dump(json_file, f)