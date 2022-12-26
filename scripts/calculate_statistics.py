from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import pypdfium2 as pdfium
from rich import print
from rich.table import Table
from tqdm import tqdm


def _series_to_table(
    series: pd.Series,
    title: Optional[str] = None,
    columns: Optional[Tuple[str, str]] = None,
) -> Table:
    if title is None:
        title = series.name
    table = Table(title=title)

    if columns is None:
        key_name, value_name = "Key", "Value"
    else:
        key_name, value_name = columns
    table.add_column(key_name, justify="left", style="bold")
    table.add_column(value_name, justify="right", style="#F5DF4D")
    for index, value in series.items():
        table.add_row(str(index), str(value))

    return table


pdf_paths = list(Path("extracted/pubmed").glob("**/*.pdf"))

pdf_data = []
for path in pdf_paths:
    pdf_data.append(
        {"name": path.name, "PMID": path.parent.stem, "size": path.stat().st_size}
    )

df = pd.DataFrame(pdf_data)

pdfs_per_id = df.groupby("PMID").size().sort_values(ascending=False)

single_pdfs = list(pdfs_per_id[pdfs_per_id == 1].index)

print(f"Total Folders: {len(df)}")
print(f"Folders with single PDF: {len(single_pdfs)}")
print(
    _series_to_table(
        pdfs_per_id.value_counts(),
        "N PDFs per Folder",
        ("N PDFs", "Frequency\n(# PMIDs)"),
    )
)

df_singles = df[df["PMID"].isin(single_pdfs)].copy()

paths_for_single_pdfs = [p for p in pdf_paths if p.parent.stem in single_pdfs]

page_counts = {}
for path in tqdm(paths_for_single_pdfs, desc="Counting Pages per PDF"):
    doc = pdfium.FPDF_LoadDocument(
        str(path), None
    )  # load document (filename, password string)
    page_count = pdfium.FPDF_GetPageCount(doc)  # get page count
    page_counts[path.parent.stem] = page_count

df_singles["page_count"] = df_singles["PMID"].map(page_counts)

assert df_singles["page_count"].isnull().sum() == 0

print(
    _series_to_table(
        df_singles["page_count"].describe().round(2),
        "Page Count Statistics",
        ("Statistic", "Value"),
    )
)

merge_data = pd.read_csv("data/merged_metadata.csv", index_col=0)

complete_data = df_singles.merge(merge_data, on=["PMID"]).assign(
    page_difference=lambda d: (d["page_count"] - d["n_pages"]).astype(int),
    original_pct=lambda d: (d["n_pages"] / d["page_count"]) * 100,
)


print(
    _series_to_table(
        complete_data["page_difference"].describe().round(1),
        "Page Differences between PubLaynet and PubMed Download",
        ("PMID - PDF", "Page Difference"),
    )
)


print(
    _series_to_table(
        complete_data["original_pct"].describe().round(1),
        "Page Differences between PubLaynet and PubMed Download\n(as % of PubMed Pages)",
        ("PMID - PDF", "Page Difference (%)"),
    )
)


fewer_pages_in_download = complete_data[complete_data["page_difference"] < 0]

# I hate formatting these stings.
fewer_pages_series = fewer_pages_in_download.assign(
    pmid_pdf_name=lambda d: d["PMID"] + " - " + d["name"],
    page_difference_str=lambda d: d["page_difference"].astype(str)
    + " ("
    + d["page_count"].astype(str)
    + " - "
    + d["n_pages"].astype(int).astype(str)
    + ")",
).set_index("pmid_pdf_name")["page_difference_str"]

print(
    _series_to_table(
        fewer_pages_series,
        "Articles with Fewer Pages in PubMed Download",
        ("PMID - PDF", "Page Difference\n(PubMed - PubLayNet)"),
    )
)