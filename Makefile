.PHONY: run test stubs debug format randbats type_chart run_cases

run:
	@uv run python3 src/agent/main.py

test:
	@uv run pytest -v

stubs:
	@uv run maturin develop --generate-stubs

debug: stubs run

format:
	@uv run ruff format src
	@cargo fmt

randbats:
	@uv run python3 scripts/fetch_randbats.py

type_chart:
	@uv run python3 scripts/generate_type_chart.py

run_cases:
	@uv run python3 scripts/run_cases.py