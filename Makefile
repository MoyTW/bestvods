.PHONY: clean bootstrap

bootstrap: _virtualenv

_virtualenv:
	virtualenv -p python3 _virtualenv
	_virtualenv/bin/pip install --upgrade pip
	_virtualenv/bin/pip install --upgrade setuptools
	_virtualenv/bin/pip install -r requirements.txt
