.PHONY: clean bootstrap

bootstrap: _virtualenv init-db

_virtualenv:
	virtualenv -p python3 _virtualenv
	_virtualenv/bin/pip install --upgrade pip
	_virtualenv/bin/pip install --upgrade setuptools
	_virtualenv/bin/pip install -r requirements.txt

init-db:
	rm dev/bestvods.db
	sqlite3 dev/bestvods.db < dev/schema.sql
	sqlite3 dev/bestvods.db < dev/seed_data.sql
	python3 dev/seed_gdq_vods.py ./resources/gdqvods/gdq-vods-agdq-2016-runData.json
	python3 dev/seed_gdq_vods.py ./resources/gdqvods/gdq-vods-agdq-2017-runData.json
	python3 dev/seed_gdq_vods.py ./resources/gdqvods/gdq-vods-sgdq-2016-runData.json
	python3 dev/seed_gdq_vods.py ./resources/gdqvods/gdq-vods-sgdq-2017-runData.json

	rm dev/test.db
	sqlite3 dev/test.db < dev/schema.sql
