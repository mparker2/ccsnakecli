import sys
import shutil
import textwrap
import click

def _raise_template_error(message):
    raise click.ClickException(message)


def _wrapped_prompt_lines(text, width):
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width=width) or [''])
    return lines


def _prompt_config_value(name, *, default, help_text=None, clear=True):
    lines_printed = 0
    width = max(20, shutil.get_terminal_size((80, 20)).columns)

    if help_text:
        for line in _wrapped_prompt_lines(help_text, width):
            click.secho(line, fg='bright_black')
            lines_printed += 1

    value = click.prompt(
        click.style(name, fg='bright_yellow'),
        default=default,
    )
    prompt_width = len(f'{name} [{default}]: ')
    lines_printed += max(1, (prompt_width + width - 1) // width)

    if clear and sys.stdout.isatty():
        for _ in range(lines_printed):
            click.echo('\033[F\033[K', nl=False)

    return value


def _echo_config_summary(context):
    click.secho('Config values:', fg='green')
    for key in context.keys():
        click.echo(f'  {key}: {context[key]}')


def init_config_from_prompts(prompts):
    context = {}
    for var in prompts.keys():
        prompt_kwargs = prompts[var]

        value = _prompt_config_value(var, **prompt_kwargs)
        context[var] = value

    _echo_config_summary(context)
    return context
