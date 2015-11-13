import urllib.request
import urllib.parse
import http.cookiejar
from bs4 import BeautifulSoup
import sys

def get_completed(username, pw, current_semester=False):
	jar = http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(debuglevel=0))
	resp = opener.open('https://cagr.sistemas.ufsc.br/modules/aluno')
	soup = BeautifulSoup(resp)

	print('- Acessando pagina de login')
	url_action = soup.form['action']
	login_form = {}
	for input in soup.findAll('input'):
	    try:
	        login_form[input['name']] = input['value']
	    except KeyError:
	        pass
	login_form['username'] = username
	login_form['password'] = pw

	print('- Fazendo login')
	resp = opener.open('https://sistemas.ufsc.br' + url_action, urllib.parse.urlencode(login_form).encode('utf8'))

	print('- Acessando Historico Escolar')
	resp = opener.open('https://cagr.sistemas.ufsc.br/modules/aluno/historicoEscolar/')
	soup = BeautifulSoup(resp)
	tags = soup.find_all('td', {'class': 'rich-table-cell'})

	print('- Pegando informacoes')
	completed = []
	suff_freq = False
	suff_grades = False
	for i in range(int(len(tags)/7)):

		suff_grades = float(tags[i*7+3].next) >= 6
		suff_freq = tags[i*7+4].next == 'FS'
		if suff_grades and suff_freq:
			completed.append(tags[i*7].next)

	if current_semester:
		resp = opener.open('https://cagr.sistemas.ufsc.br/modules/aluno/espelhoMatricula/')
		soup = BeautifulSoup(resp)
		completed = completed + get_to_complete(soup)

	return completed

def get_to_complete(soup):
	current = []

	table = soup.find('table', id='j_id119:j_id202')
	tags = table.find_all('td')
	for i in range(int(len(tags)/10)):
		current.append(tags[i*10+1].next)

	return current