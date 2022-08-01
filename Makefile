all: lint format usage

lint: mypy
check: lint

mypy:
	mypy --pretty --show-error-codes costcoparser/

format:
	./script/format

usage:
	python3 ./script/update-usage.py

.PHONY: mypy lint format usage check all
