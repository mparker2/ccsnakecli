import os
import sys
from pathlib import Path
import click
import yaml
from jinja2 import Environment, FileSystemLoader

from {{ cookiecutter.package_name }}.pipeline_utils.init import init_config_from_prompts

BASE_DIR = Path(__file__).parent
PIPELINE_DIR = BASE_DIR / "pipeline"
CONFIG_DIR = PIPELINE_DIR / "config"
SNAKEFILE = PIPELINE_DIR / "Snakefile"
SUBDIR_NAMES = ['annotation_dir', 'raw_data_dir', 'results_dir']
PROMPTS = {
    'annotation_dir': {
        'default': 'annotations',
        'help': 'Directory containing reference annotation data.',
    },
    'raw_data_dir': {
        'default': 'raw_data',
        'help': 'Directory containing input data.',
    },
    'results_dir': {
        'default': 'results',
        'help': 'Directory where pipeline outputs will be written.',
    },
    'dataset_name': {
        'default': 'example_dataset',
        'help': 'Name of this dataset in the generated YAML and output paths.',
    },
}


if not SNAKEFILE.exists():
    click.echo(f"Error: Snakefile not found at {SNAKEFILE}", err=True)
    sys.exit(1)


@click.group()
def cli():
    """CLI for the pipeline."""
    pass


@cli.command("init-config")
@click.argument("destination", type=click.Path(), default='config.yaml')
@click.option("-f", "--force", is_flag=True, default=False)
def init_config(destination, force):
    """Prompt for missing values and render config.yaml from template."""
    dest = Path(destination)
    if dest.exists() and not force:
        click.echo(f"{dest} already exists. Refusing to overwrite.", err=True)
        sys.exit(1)
    context = init_config_from_prompts(PROMPTS)
    env = Environment(loader=FileSystemLoader(CONFIG_DIR))
    # Render and write output
    template = env.get_template("default_config.yaml.j2")
    rendered = template.render(context)
    dest.write_text(rendered)
    click.secho(f"Config written to {dest}", fg="green")
    config = yaml.safe_load(rendered)

    for directory in SUBDIR_NAMES:
        dir_name = config[directory]
        if not os.path.exists(dir_name):
            click.secho(f'Creating {directory}: {dir_name}', fg="bright_yellow")
            os.makedirs(dir_name)



@cli.command("run", context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--configfile", "-c", type=click.Path(exists=True), default="config.yaml",
              help="Path to config file")
@click.option("--set", "overrides", multiple=True, help="Override config values (key=value)")
@click.pass_context
def run_pipeline(ctx, configfile, overrides):
    """Run the pipeline."""
    # Convert key=value overrides into a flat list for --config
    config_overrides = []
    for item in overrides:
        if "=" not in item:
            click.echo(f"Ignoring malformed --set '{item}'", err=True)
            continue
        config_overrides.append(item)

    args = [
        "--snakefile", str(SNAKEFILE.resolve()),
        "--configfile", str(configfile),
    ]

    if config_overrides:
        args += ["--config"] + config_overrides

    # Add any unknown extra CLI args
    args += ctx.args

    click.secho(f"Running: snakemake {' '.join(args)}", fg="bright_yellow")

    try:
        # Snakemake ≥7.x
        from snakemake.cli import main as snakemake
    except ImportError:
        # Snakemake ≤6.x
        from snakemake import main as snakemake

    snakemake(args)


if __name__ == "__main__":
    cli()
