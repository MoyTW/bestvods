.PHONY: clean bootstrap

bootstrap: _virtualenv init-db

_virtualenv:
	virtualenv -p python3 _virtualenv
	_virtualenv/bin/pip install --upgrade pip
	_virtualenv/bin/pip install --upgrade setuptools
	_virtualenv/bin/pip install -r requirements.txt

init-db:
	rm bestvods/bestvods.db
	sqlite3 bestvods/bestvods.db < bestvods/schema.sql
	sqlite3 bestvods/bestvods.db < bestvods/seed_data.sql
