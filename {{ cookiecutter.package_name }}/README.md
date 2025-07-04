# {{ cookiecutter.package_name }}

{{ cookiecutter.project_short_description }}

## Installation

    pip install -e .

## Usage

### Initialise config

    {{ cookiecutter.cli_name }} init-config

This creates a `config.yaml` in your current directory, prompting you to fill in required fields.

### Run the pipeline

    {{ cookiecutter.cli_name }} run

You can pass any Snakemake arguments (e.g. `--profile`, `--use-conda`, etc.):

    {{ cookiecutter.cli_name }} run --cores 4 --use-conda --rerun-incomplete

You can also override config values inline:

    {{ cookiecutter.cli_name }} run --set outfile=test.txt

## Example output

The default pipeline just touches an output file defined in the config.