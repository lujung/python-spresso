init:
    pip3 install -r requirements.txt

test:
    python3 tests/__init__.py test

coverage:
    python3 tests/__init__.py coverage

.PHONY: init test coverage apidoc