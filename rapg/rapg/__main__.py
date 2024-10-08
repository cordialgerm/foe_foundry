import click

from rapg.test import main as test_main
from rapg.train import train_model


@click.group()
def cli():
    pass


# Add test command to the CLI
@cli.command()
def test():
    test_main()


# Add train command to the CLI
@cli.command()
def train():
    train_model()


# Entry point for the CLI
if __name__ == "__main__":
    cli()
