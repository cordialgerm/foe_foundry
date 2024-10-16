import click

from .data.monsters import save_monsters
from .train import fine_tune_bert_contrastive, fine_tune_bert_on_background_corpus


@click.group()
def cli():
    pass


@cli.command()
def test():
    pass


@cli.command()
@click.option("--fresh", is_flag=True, help="Whether to start fresh training")
@click.option("--skip-training", is_flag=True, help="Whether to skip training")
def train_bg(fresh: bool, skip_training: bool = False):
    fine_tune_bert_on_background_corpus(fresh=fresh, skip_training=skip_training)


@cli.command()
@click.option("--fresh", is_flag=True, help="Whether to start fresh training")
@click.option("--skip-training", is_flag=True, help="Whether to skip training")
def train_contrastive(fresh: bool, skip_training: bool = False):
    fine_tune_bert_contrastive(fresh=fresh, skip_training=skip_training)


@cli.command()
def regen_canonical_monsters():
    save_monsters()


# Entry point for the CLI
if __name__ == "__main__":
    cli()
