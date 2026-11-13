.PHONY: run stumps debug format randbats

run:
	@uv run python3 src/agent/main.py

stubs:
	@uv run maturin develop --generate-stubs

debug: stubs run

format:
	@uv run ruff format .

randbats:
	@uv run python3 scripts/fetch_randbats.py