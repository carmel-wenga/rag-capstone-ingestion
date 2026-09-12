import click

from app.ingest import run_ingestion


@click.group()
def cli() -> None:
    """CLI entrypoint for ingestion tasks."""


@cli.command()
@click.option("--source", required=True, type=click.Path(exists=True, path_type=str))
def ingest(source: str) -> None:
    """Ingest one file or a directory of supported documents."""
    run_ingestion(source)
    click.echo(f"Ingestion completed for {source}")


if __name__ == "__main__":
    cli()
