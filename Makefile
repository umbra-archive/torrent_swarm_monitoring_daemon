PYTHON := $(shell command -v python3 || command -v python)
VENV := venv
REQUIREMENTS := requirements.txt
APP_SCRIPT := main.py

.PHONY: debian setup run

debian:
	sudo apt install python3.11-venv

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate; $(PYTHON) -m pip install -r $(REQUIREMENTS)

run:
	. $(VENV)/bin/activate; $(PYTHON) $(APP_SCRIPT)

