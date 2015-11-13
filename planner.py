import json
import sys
import getpass
from graph import *
import get_completed_classes

class Planner:
	def __init__(self, course_code):
		self.course_info = {}

		with open('db/'+course_code+'.json') as f:
			json_file = json.load(f)

			self.course_info['code'] = json_file["code"]
			self.course_info['min_hours'] = json_file["min_hours"]
			self.course_info['max_hours'] = json_file["max_hours"]
			self.course_info['classes'] = json_file["classes"]
			self.course_info['final_class'] = json_file["final_class"]

		self.graph = self.build_graph(self.course_info)

	def build_graph(self, course_info):
		graph = Graph()

		classes = course_info['classes']
		for _class in classes:
			graph.add_node(Node(_class, classes))

		for _class in classes:
			for next_class in classes[_class]['prereq']:
				graph.connect(_class, next_class)

		return graph

	def get_available_options(self, completed_classes):
		options = []
		classes = self.course_info['classes']
		for _class in classes:
			if _class not in completed_classes:
				dependencies = classes[_class]['prereq']
				if dependencies == []:
					options.append(_class)
				else:
					if set(dependencies).issubset(set(completed_classes)):
						options.append(_class)

		return options

	def calculate_magnitude(self, remaining_classes):
		magnitudes = {x: 0 for x in remaining_classes}

		for _class in remaining_classes:
			magnitudes[_class] = len(self.get_blocked_classes(_class))

		return magnitudes

	def get_blocked_classes(self, _class):
		return self.graph.path_to_end(_class)

	def all_classes_completed(self, completed_classes):
		return self.get_available_options(completed_classes) == [] and self.course_info["final_class"] in completed_classes

	def check_min_hours(self, plan, new_class):
		hours = self.course_info['classes'][new_class]['credits']

		for _class in plan:
			hours += self.course_info['classes'][_class]['credits']

		return hours >= self.course_info['min_hours']

	def check_max_hours(self, plan, new_class):
		hours = self.course_info['classes'][new_class]['credits']

		for _class in plan:
			hours += self.course_info['classes'][_class]['credits']

		return hours <= self.course_info['max_hours']

	def build_plans(self, completed_classes):
		completed_classes_aux = completed_classes
		options = self.get_available_options(completed_classes_aux)
		magnitudes = self.calculate_magnitude(options)

		plans = []
		while not self.all_classes_completed(completed_classes_aux):
			classes_sorted = sorted(magnitudes.keys(), key=lambda x: magnitudes[x])[::-1]

			plan = []
			new_class = classes_sorted[0]

			while (not self.check_min_hours(plan, new_class) or self.check_max_hours(plan, new_class)):
				try:
					if not self.conflicts(plan, new_class):
						plan.append(new_class)

					del classes_sorted[0]
					new_class = classes_sorted[0]
				except IndexError:
					break

			plans.append(plan)

			for item in plan:
				completed_classes_aux.append(item)

			options = self.get_available_options(completed_classes_aux)
			magnitudes = self.calculate_magnitude(options)

		return plans

	def conflicts(self, plan, _class):
		course_schedule = self.get_schedule(_class)
	
		# para cada materia presente no plano
		for aux in plan:
			conflict_count = 0
			aux_schedule = self.get_schedule(aux)

			# itera sobre as diferentes turmas existentes
			count = 0
			for course_schedule_aux in course_schedule:
				# itera sobre as turmas existentes de cada materia existente no plano
				for course_option in course_schedule_aux:
					
					for aux_schedule_aux in aux_schedule:
						for aux_option in aux_schedule_aux:
							day_a = int(aux_option[0])
							start_a = int(aux_option[1])
							end_a = int(aux_option[2])
							day_b = int(course_option[0])
							start_b = int(course_option[1])
							end_b = int(course_option[2])

							# if day_b == day_a and ((start_a > start_b and start_a < end_b) or (start_b > start_a and start_b < end_a) or start_a == start_b or end_a == end_b):
							A = start_a >= end_b
							B = end_a <= start_b
							if day_b == day_a and not A and not B:
								conflict_count += 1
								break
					if conflict_count == len(aux_schedule):
						count += 1
			if count >= len(course_schedule):
				return True
		return False

	def get_schedule(self, class_code):
		schedule_aux = self.course_info['classes'][class_code]['schedule']
		schedule = []
		for item in schedule_aux[0]:
			class_day = []
			for i in range(len(item)):
				aux = item[i][:8:]
				day = aux[0]

				start_hour = int(aux[2:4])
				start_min = int(aux[4:6])
				hours = int(aux[7])

				offset = 50*hours
				plus_hours = int(offset/60)
				plus_min = offset % 60

				end_hour = start_hour + plus_hours
				end_min = (start_min + plus_min) % 60
				if(start_min + plus_min >= 60):
					end_hour += 1

				if(end_hour > 16):
					end_min = (end_min + 20) % 60
					if int((end_min+20)/60) % 60 == 0:
						end_hour += 1

				start = str(start_hour) + str(start_min).zfill(2)
				end = str(end_hour) + str(end_min).zfill(2)

				class_day.append((day, start, end))
			schedule.append(class_day)
		return schedule

# Tests
if __name__ == '__main__':
	username = input('UFSC Registration Number:\n')
	pw = getpass.getpass('CAGR Password:\n')

	# username, pw = sys.argv[1], sys.argv[2]
	p = Planner('208')
	plans = p.build_plans(get_completed_classes.get_completed(username, pw, True))
	for i in range(len(plans)):
		plan = plans[i]
		print('\n################### Semester ' + str(i+1) + ' ###################\n')
		for code in plan:
			print(code + ' - ' + p.course_info['classes'][code]['name'])
