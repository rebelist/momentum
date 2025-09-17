.PHONY: start check tests coverage


start:
	@echo "\nRunning Momentum..."
	@uv sync
	@uv run src/rebelist/momentum/presentation/dashboard.py

check:
	@echo "\nRunning pre-commit all or a specific hook..."
	@pre-commit run --all-files

tests:
	@echo "\nRunning tests..."
	@uv run pytest -vv  --cache-clear --color=yes --no-header --maxfail=1 --failed-first --disable-warnings

coverage:
	@echo "\nGenerating test coverage..."
	@uv run pytest --disable-warnings --no-summary --quiet --color=yes --no-header --cov=rebelist.momentum --no-cov-on-fail --cov-report html

# Avoid treating the argument as a target
%:
	@: