# Cookiecutter Snakemake CLI Template

A Cookiecutter template for creating Snakemake-based pipelines with a Python CLI using Click.

## Features

- Self-contained, installable Python package
- Separates snakemake pipeline from run directory for easier re-use
- CLI with `init-config` (Jinja2 prompt) and `run` commands
- Pass-through to full Snakemake CLI
- Template config rendered at runtime
- Minimal working rule as example - you need to write the real pipeline
- Includes folders for rules, envs, configs

## Usage

Install cookiecutter:

    pip install cookiecutter

Create a new project:

    cookiecutter gh:mparker2/ccsnakecli

Then:

    cd mytool/
    pip install -e .
    mytool init-config
    mytool run --cores 1

## Template variables

You’ll be prompted for:

- `cli_name`: used for CLI command name
- `package_name`: python package name
- `project_short_description`
- `full_name`
- `email`
