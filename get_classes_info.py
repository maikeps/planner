#!/usr/bin/env python3
# Code based on ramiropolla's matrufsc_dbs
# https://github.com/ramiropolla/matrufsc_dbs

import urllib.request
import urllib.parse
import http.cookiejar
from bs4 import BeautifulSoup
import sys
from io import BytesIO
import gzip
from xml.etree import cElementTree

try:
    semestre = sys.argv[3]
except:
    semestre = 20152

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
login_form['username'] = sys.argv[1]
login_form['password'] = sys.argv[2]

print('- Fazendo login')
resp = opener.open('https://sistemas.ufsc.br' + url_action, urllib.parse.urlencode(login_form).encode('utf8'))

print('- Acessando Cadastro de Turmas')
resp = opener.open('https://cagr.sistemas.ufsc.br/modules/aluno/cadastroTurmas/')
soup = BeautifulSoup(resp)
viewState = soup.find('input', {'name':'javax.faces.ViewState'})['value']

print('- Pegando banco de dados')
request = urllib.request.Request('https://cagr.sistemas.ufsc.br/modules/aluno/cadastroTurmas/index.xhtml')
request.add_header('Accept-encoding', 'gzip')
page_form = {
    'AJAXREQUEST': '_viewRoot',
    'formBusca:selectSemestre': semestre,
    'formBusca:selectDepartamento': '',
    'formBusca:selectCampus': '1',
    'formBusca:selectCursosGraduacao': '0',
    'formBusca:codigoDisciplina': '',
    'formBusca:j_id135_selection': '',
    'formBusca:filterDisciplina': '',
    'formBusca:j_id139': '',
    'formBusca:j_id143_selection': '',
    'formBusca:filterProfessor': '',
    'formBusca:selectDiaSemana': '0',
    'formBusca:selectHorarioSemana': '',
    'formBusca': 'formBusca',
    'autoScroll': '',
    'javax.faces.ViewState': viewState,
    'formBusca:dataScroller1': '1',
    'AJAX:EVENTS_COUNT': '1',
}


def find_id(xml, id):
    for x in xml:
        if x.get('id') == id:
            return x
        else:
            y = find_id(x, id)
            if y is not None:
                return y
    return None
def go_on(xml):
    scroller = find_id(xml, 'formBusca:dataScroller1_table')
    if scroller is None:
        return False
    for x in scroller[0][0]:
        onclick = x.get('onclick')
        if onclick is not None and 'next' in onclick:
            return True
    return False

campus_str = [ 'EaD', 'FLO', 'JOI', 'CBS', 'ARA', 'BLN' ]
for campus in range(1, len(campus_str)):
    print('campus ' + campus_str[campus])
    outfile = open('db/' + str(semestre) + '_' + campus_str[campus] + '.xml', 'wb')
    page_form['formBusca:selectCampus'] = campus
    pagina = 1
    while 1:
        print(' pagina %02d' % pagina)
        page_form['formBusca:dataScroller1'] = pagina
        resp = opener.open(request, urllib.parse.urlencode(page_form).encode('utf8'))
        if resp.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(resp.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = resp.read()
        outfile.write(data)
        xml = cElementTree.fromstring(data)
        if not go_on(xml):
            break
        pagina = pagina + 1
    outfile.close()