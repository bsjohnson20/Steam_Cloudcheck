# Installs packages, runs pytest, and runs pyinstaller
# https://github.com/batonogov/docker-pyinstaller - very useful

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: all
all: uv_install pytest requirements pyinstaller_linux pyinstaller_windows

.PHONY: run
run:
	uv run main.py

.PHONY: uv_install
uv_install:
	uv sync

.PHONY: pytest
pytest:
	pytest

.PHONY: pyinstaller_linux
pyinstaller_linux:
	sudo docker run --volume "$(ROOT_DIR):/src/" batonogov/pyinstaller-linux:latest

.PHONY: pyinstaller_windows
pyinstaller_windows:
	sudo docker run --volume "$(ROOT_DIR):/src/" batonogov/pyinstaller-windows:latest

requirements: 
	uv pip freeze > requirements.txt