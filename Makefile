.PHONY: run stumps debug format

run:
	@uv run python3 src/agent/main.py

stubs:
	@uv run maturin develop --generate-stubs

debug: stubs run

format:
	@uv run ruff format .