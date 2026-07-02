from setuptools import setup, find_packages

setup(
    name="{{ cookiecutter.cli_name }}",
    version="0.1.0",
    description="{{ cookiecutter.project_short_description }}",
    author="{{ cookiecutter.author_name }}",
    author_email="{{ cookiecutter.author_email }}",
    packages=find_packages(),
    package_data={
        "{{ cookiecutter.package_name }}": [
            "pipeline/Snakefile",
            "pipeline/config/*.j2",
            "pipeline/config/*.yaml",
            "pipeline/rules/*.snakefile",
            "pipeline/rules/*.smk",
            "pipeline/env_yamls/*.yaml",
            "pipeline/env_yamls/*.yml",
        ],
    },
    install_requires=[
        "click>=8.0",
        "jinja2",
        "pyyaml",
        "snakemake",
    ],
    entry_points={
        "console_scripts": [
            "{{ cookiecutter.cli_name }} = {{ cookiecutter.package_name }}.cli:cli"
        ]
    },
    include_package_data=True,
    zip_safe=False,
)