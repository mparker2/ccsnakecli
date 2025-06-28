import shutil
import sys
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, meta

BASE_DIR = Path(__file__).parent
PIPELINE_DIR = BASE_DIR / "pipeline"
CONFIG_DIR = PIPELINE_DIR / "config"
SNAKEFILE = PIPELINE_DIR / "Snakefile"


if not SNAKEFILE.exists():
    click.echo(f"Error: Snakefile not found at {SNAKEFILE}", err=True)
    sys.exit(1)


@click.group()
def cli():
    """CLI for the pipeline."""
    pass


@cli.command("init-config")
@click.argument("destination", type=click.Path(), default='config.yaml')
def init_config(destination):
    """Prompt for missing values and render config.yaml from template."""
    dest = Path(destination)
    if dest.exists():
        click.echo(f"{dest} already exists. Refusing to overwrite.", err=True)
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(CONFIG_DIR))
    template_name = "default_config.yaml.j2"
    template_source = env.loader.get_source(env, template_name)[0]

    # Find undeclared variables in the template
    parsed = env.parse(template_source)
    variables = meta.find_undeclared_variables(parsed)

    # Prompt for each variable
    context = {}
    for var in sorted(variables):
        value = click.prompt(f"Enter value for '{var}'", default="")
        context[var] = value

    # Render and write output
    template = env.get_template(template_name)
    rendered = template.render(context)
    dest.write_text(rendered)
    click.echo(f"Config written to {dest}")


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

    click.echo(f"Running: snakemake {' '.join(args)}")

    try:
        # Snakemake ≥7.x
        from snakemake.cli import main as snakemake
    except ImportError:
        # Snakemake ≤6.x
        from snakemake import main as snakemake

    snakemake(args)

if __name__ == "__main__":
    cli()
