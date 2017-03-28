init:
    pip3 install -r requirements.txt

test:
    python3 tests/__init__.py test

coverage:
    python3 tests/__init__.py coverage

apidoc:
    sphinx-apidoc -fMeET spresso -o docs/api

.PHONY: init test coverage apidoc