from setuptools import setup, find_packages

setup(
    name="{{ cookiecutter.cli_name }}",
    version="0.1.0",
    description="{{ cookiecutter.project_short_description }}",
    author="{{ cookiecutter.author_name }}",
    author_email="{{ cookiecutter.author_email }}",
    packages=["{{ cookiecutter.package_name }}"],
    install_requires=[
        "click>=8.0",
        "jinja2",
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