from pathlib import Path
from typing import Tuple
import pandas as pd

import typer
from rich import print


def get_id(path: Path) -> Tuple[str, int]:
    filename = path.stem
    name, page = filename.split("_")
    page = int(page)
    return name, page


def main(
    source_dir: Path = typer.Argument(
        ...,
        help="A directory of extracted PDFs, split into train/dev/test subfolders",
        file_okay=False,
        dir_okay=True,
    ),
):
    data = []
    splits = ["train", "dev", "test"]
    for split in splits:
        pdf_paths = Path(source_dir / split).glob("*.pdf")
        for path in pdf_paths:
            name, page = get_id(path)
            data.append((name, page, split))

    df = pd.DataFrame(data, columns=["name", "page", "split"])
    assert len(df) > 0

    if (df.groupby("name")["split"].nunique() == 1).all():
        print("[green]✔️ All full PDFs are unique to train/dev/test splits[/green]")
    else:
        print("[red]🚫 PDF pages split across train/dev/test[/red]")
        typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
