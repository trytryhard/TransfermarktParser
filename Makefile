fmt:
	@echo --- FORMATTING CODE
	isort src/
	black src/

lint:
	@echo --- RUNNING LINTERS
	pylint src/
	isort src/ --check
	black src/ --check
