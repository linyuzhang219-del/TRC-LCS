.PHONY: install-dev test lint demo benchmark build

install-dev:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check trc_lcs tests tools

demo:
	python tools/make_demo_dataset.py --out data/demo --num-frames 80
	trc-lcs --task "找到客厅里红色椅子旁边的包" --image-dir data/demo/images --traj data/demo/trajectory_tum.txt --semantics data/demo/semantics.jsonl --camera 520 520 320 240 --out outputs/demo

benchmark:
	python tools/benchmark_demo.py --work-dir outputs/benchmark_demo

build:
	python -m build
