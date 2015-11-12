echo "Insira sua matrícula:"
read matricula
echo "Insira sua senha:"
read senha

python3 get_classes_info.py $matricula $senha
if [ $# -gt 0 ]; then
	if [ $1 = '--update-db' ]; then
		python3 parse_classes.py db/20152_FLO.xml db/20152_FLO.json 
	fi
fi
python3 update_json.py db/208.json db/20152_FLO.json