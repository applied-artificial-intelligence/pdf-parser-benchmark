"""Main CLI entry point for PDF-Bench."""


import typer

app = typer.Typer(
    name="pdfbench",
    help="PDF-Bench: Benchmarking suite for PDF-to-Markdown conversion",
    add_completion=False,
)


def version_callback(show_version: bool) -> None:
    """Show version and exit."""
    if show_version:
        from pdf_bench import __version__

        typer.echo(f"PDF-Bench version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """PDF-Bench: Benchmarking suite for PDF-to-Markdown conversion."""
    pass


if __name__ == "__main__":
    app()
