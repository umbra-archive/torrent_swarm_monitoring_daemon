BASE_PYTHON := $(shell command -v python3 || command -v python)
VENV_PYTHON := python
VENV := venv
REQUIREMENTS := requirements.txt
APP_SCRIPT := main.py

.PHONY: debian setup run

debian:
	sudo apt install python3.11-venv

setup:
	$(BASE_PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate; $(VENV_PYTHON) -m pip install -r $(REQUIREMENTS)

run:
	. $(VENV)/bin/activate; $(VENV_PYTHON) $(APP_SCRIPT)
	
forever:
	while true; do \
		nohup sh -c '. $(VENV)/bin/activate; $(VENV_PYTHON) $(APP_SCRIPT)'; \
		sleep 1; \
		bash ../ipdl.cat/sync.sh; \
	done


