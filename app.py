from flask import Flask, render_template, redirect, url_for, request
from planner import Planner

app = Flask(__name__)

@app.route('/')
def home():
	return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		p = Planner('208')
		plans = p.build_plans(username, password)

		complete = []
		for plan in plans:
			plan_names = []
			for code in plan:
				plan_names.append(p.course_info['classes'][code]['name'])
			complete.append(plan_names)
		
		return render_template('index.html', plans=complete)

	return render_template('login.html')

if __name__ == '__main__':
	app.run(debug=True)