import click

from .data.monsters import save_monsters


@click.group()
def cli():
    pass


@cli.command()
def test():
    pass


@cli.command()
def train():
    pass


@cli.command()
def regen_canonical_monsters():
    save_monsters()


# Entry point for the CLI
if __name__ == "__main__":
    cli()
