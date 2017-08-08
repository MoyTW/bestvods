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
	python3 dev/seed_gdq_vods.py

	rm dev/test.db
	sqlite3 dev/test.db < dev/schema.sql
