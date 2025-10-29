.PHONY: test run

test:
	pytest

run:
	onepaisa

clean:
	rm -rf .pytest_cache __pycache__