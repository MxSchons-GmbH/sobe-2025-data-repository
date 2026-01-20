# Brain Emulation Report 2025 - Makefile
# Common tasks for figure generation and build pipeline

.PHONY: help install figures downloads html serve clean all

PYTHON ?= python3
SCRIPTS_DIR = scripts
OUTPUT_DIR = data-and-figures

help:
	@echo "Brain Emulation Report 2025 - Build Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install     Install Python dependencies"
	@echo "  figures     Generate all figures"
	@echo "  downloads   Build ZIP archives for download"
	@echo "  html        Build standalone HTML files for embedding"
	@echo "  serve       Start local development server"
	@echo "  clean       Remove generated files"
	@echo "  all         Run full pipeline (figures + downloads + html)"
	@echo ""

install:
	$(PYTHON) -m pip install -r requirements.txt

figures:
	cd $(SCRIPTS_DIR) && $(PYTHON) run_all_figures.py

downloads:
	cd $(SCRIPTS_DIR) && $(PYTHON) build_downloads.py

html:
	cd $(SCRIPTS_DIR) && $(PYTHON) build_standalone_html.py

serve:
	@echo "Starting server at http://localhost:8000"
	@echo "Open http://localhost:8000/figures.html or http://localhost:8000/data.html"
	cd $(OUTPUT_DIR) && $(PYTHON) -m http.server 8000

clean:
	rm -rf $(OUTPUT_DIR)/figures/generated/*.png
	rm -rf $(OUTPUT_DIR)/figures/generated/*.svg
	rm -rf $(OUTPUT_DIR)/figures/generated/neuro-sim/*
	rm -rf $(OUTPUT_DIR)/figures/generated/neuro-rec/*
	rm -rf $(OUTPUT_DIR)/figures/generated/radar-charts/*
	rm -rf $(OUTPUT_DIR)/downloads/*.zip

all: figures downloads html
	@echo ""
	@echo "Build complete!"
	@echo "Output in: $(OUTPUT_DIR)/"
