import json
from graph import *

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
		return False

# Tests
p = Planner('208')
plans = p.build_plans([])
for i in range(len(plans)):
	plan = plans[i]
	print('\n################### Semester ' + str(i+1) + ' ###################\n')
	for code in plan:
		print(code + ' - ' + p.course_info['classes'][code]['name'])