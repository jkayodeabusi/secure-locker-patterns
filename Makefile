.PHONY: install run demo demo-off attack test semgrep

PATTERN ?= 01
HOST := 127.0.0.1

install:
	pip install -r requirements-dev.txt
	pipx install semgrep==1.186.0 || true   # Semgrep runs in its own environment

run demo:              ## every check on
	uvicorn app.main:app --host $(HOST) --port 8000

demo-off:              ## one check switched off, local only
	DEMO_MODE=1 BREAK_PATTERNS=$(PATTERN) uvicorn app.main:app --host $(HOST) --port 8000

attack:
	python attacks/$(PATTERN)_*.py

test:
	# pytest -q
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q

semgrep:
	semgrep scan --config semgrep/ --error --metrics=off app/ secure_patterns/
	semgrep scan --test --metrics=off semgrep/
