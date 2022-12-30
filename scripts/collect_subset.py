import tarfile
from collections import Counter
from enum import Enum
from pathlib import Path
from shutil import copy
from typing import Optional, Tuple

import pandas as pd
import pypdfium2 as pdfium
import typer
from pqdm.processes import pqdm
from rich import print


def get_pdf_data(path: Path):
    data = {}
    data["name"] = path.stem
    size = path.stat().st_size
    data["size"] = size
    pdf = pdfium.PdfDocument(str(path))
    data["pages"] = len(pdf)
    widths = []
    heights = []
    object_total = 0
    text_box_total = 0
    character_total = 0
    for pnumber in range(data["pages"]):
        page = pdf.get_page(pnumber)
        width, height = page.get_size()
        widths.append(width)
        heights.append(height)
        page = pdf.get_page(pnumber)
        n_objects = len(list(page.get_objects()))
        object_total += n_objects
        textpage = page.get_textpage()
        n_textboxes = len(list(textpage.get_rectboxes()))
        text_box_total += n_textboxes
        character_total += textpage.n_chars
        for garbage in (textpage, page):
            garbage.close()
    pdf.close()
    data["object_total"] = object_total
    data["text_box_total"] = text_box_total
    data["character_total"] = character_total
    data["modal_width"] = Counter(widths).most_common(1)[0][0]
    data["modal_height"] = Counter(heights).most_common(1)[0][0]
    return data


class DistributionSelect(Enum):
    LARGEST = "largest"
    SMALLEST = "smallest"
    MEDIAN = "median"


def get_records(
    df: pd.DataFrame, column: str, type_: DistributionSelect, max_elements: int = 1
) -> Tuple[pd.Series, str]:
    series = df[column]
    if type_ is DistributionSelect.LARGEST:
        return (series.nlargest(max_elements), f"{column}_largest")
    elif type_ is DistributionSelect.SMALLEST:
        return (series.nsmallest(max_elements), f"{column}_smallest")
    else:
        return (
            df[series == series.median()][column].head(max_elements),
            f"{column}_median",
        )


def main(
    source_dir: Path = typer.Argument(
        ..., help="Path to PDF directory, where PDFs are labeled by PMID."
    ),
    output_file: Path = typer.Argument(
        ..., help="Output file (.tar.gz) to archive subsetted PDFs"
    ),
    output_csv_path: Optional[Path] = typer.Option(
        None, help="Path to export csv of PDF information."
    ),
    n_jobs: int = typer.Option(8, help="Number of PDFs to process in parallel."),
):
    pdf_paths = list(source_dir.glob("*.pdf"))
    results = pqdm(pdf_paths, get_pdf_data, n_jobs=n_jobs)
    df = pd.DataFrame(results).sort_values("name").set_index("name")
    columns = [
        "size",
        "pages",
        "object_total",
        "text_box_total",
        "character_total",
        "modal_width",
        "modal_height",
    ]
    result_df = pd.DataFrame()
    for column in columns:
        largest = get_records(df, column, DistributionSelect.LARGEST, 2)
        smallest = get_records(df, column, DistributionSelect.SMALLEST, 2)
        median = get_records(df, column, DistributionSelect.MEDIAN, 1)
        for (data, type_) in [largest, smallest, median]:
            records = df.loc[data.index].copy()
            records["type"] = type_
            result_df = pd.concat((result_df, records))
    combined_types = (
        result_df.reset_index().groupby("name")["type"].apply(lambda x: ",".join(x))
    )
    unique_pdfs_df = (
        result_df.reset_index()
        .drop_duplicates(subset=["name"])
        .drop(["type"], axis="columns")
        .join(combined_types, on="name")
        .set_index("name")
    )
    article_ids = set(unique_pdfs_df.index)
    unique_pdfs_paths = [p for p in pdf_paths if p.stem in article_ids]
    archive_dir = Path("temp-subset")
    for path in unique_pdfs_paths:
        archive_dir.mkdir(exist_ok=True)
        copy(path, archive_dir / path.name)
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(archive_dir, arcname=".")
    print(
        f"✔️ Compressed {len(unique_pdfs_paths)} "
        f"PDFs into [green]{output_file}[/green]."
    )

    if output_csv_path:
        unique_pdfs_df.to_csv(output_csv_path)
        print(f"✔️ Exported PDF info to [green]{output_csv_path}[/green].")


if __name__ == "__main__":
    typer.run(main)
