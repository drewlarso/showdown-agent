.PHONY: run stumps debug format randbats generate_type_chart

run:
	@uv run python3 src/agent/main.py

stubs:
	@uv run maturin develop --generate-stubs

debug: stubs run

format:
	@uv run ruff format .

randbats:
	@uv run python3 scripts/fetch_randbats.py

type_chart:
	@uv run python3 scripts/generate_type_chart.py