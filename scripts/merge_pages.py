from pathlib import Path
from typing import Tuple
from itertools import groupby

from pypdfium2 import _namespace as pdfium

from tqdm import tqdm
import pandas as pd
import typer


def merge_files(input_paths):
    # https://github.com/pypdfium2-team/pypdfium2/blob/978e5fff5fbe5750940ef2e47cac11a8a2e5ccfc/src/pypdfium2/_cli/merge.py#L7
    dest_pdf = pdfium.PdfDocument.new()
    index = 0

    for in_path in input_paths:
        src_pdf = pdfium.PdfDocument(in_path)
        success = pdfium.FPDF_ImportPagesByIndex(
            dest_pdf.raw, src_pdf.raw, None, 0, index
        )
        if not success:
            raise RuntimeError("Importing pages failed.")
        index += len(src_pdf)

    return dest_pdf


def get_id(path: Path) -> Tuple[str, int]:
    filename = path.stem
    name, page = filename.split("_")
    page = int(page)
    return name, page


def main(
    source_dir: Path = typer.Argument(
        ...,
        help="List to a directory of PDF files, where the filenames are <PMID_PAGE> (ex. 'PMC538274_00004.pdf')",
        file_okay=False,
        dir_okay=True,
    ),
    dest_dir: Path = typer.Argument(
        ...,
        help="List to a directory to output PDFs. Subdirectories 'single', 'incomplete', and 'complete' will be created.",
        file_okay=False,
        dir_okay=True,
    ),
    metadata_output: Path = typer.Argument(
        ...,
        help="File (.csv) to store the metadata on how PDFs get merged.",
        file_okay=True,
        dir_okay=False,
    ),
):
    pdf_paths = list(source_dir.glob("**/*.pdf"))

    single_path = dest_dir / "single"
    incomplete_path = dest_dir / "incomplete"
    complete_path = dest_dir / "complete"
    for path in [single_path, incomplete_path, complete_path]:
        path.mkdir(exist_ok=True, parents=True)

    sorted_paths = sorted(pdf_paths, key=get_id)
    total_ids = set(get_id(p)[0] for p in sorted_paths)

    pdf_data = []

    pdf_progress = tqdm(
        groupby(sorted_paths, key=lambda x: get_id(x)[0]), total=len(total_ids)
    )
    s_ct, i_ct, c_ct, e_ct = 0, 0, 0, 0
    for (_id, paths) in pdf_progress:
        data = {}
        data["PMID"] = _id

        in_paths = list(paths)
        data["split"] = in_paths[0].parent.stem

        max_page = max(get_id(p)[1] for p in in_paths)
        min_page = min(get_id(p)[1] for p in in_paths)
        try:
            merged_pdf = merge_files([str(p) for p in in_paths])
        except pdfium.PdfiumError:
            data["error"] = True
            pdf_data.append(data)
            e_ct += 1
            continue
        n_pages = len(merged_pdf)
        complete = (max_page + 1 == n_pages) & (min_page == 0)
        single = n_pages == 1
        # print(f"{_id=}, {n_pages=}, {complete=}, {max_page=}, {min_page=}")

        data["n_pages"] = n_pages
        if single:
            with open(single_path / f"{_id}.pdf", "wb") as buffer:
                merged_pdf.save(buffer)
            data["merge_type"] = "single"
            s_ct += 1
        elif not complete:
            with open(incomplete_path / f"{_id}.pdf", "wb") as buffer:
                merged_pdf.save(buffer)
            data["merge_type"] = "incomplete"
            i_ct += 1
        else:
            # it's 'complete' and longer than a single page
            with open(complete_path / f"{_id}.pdf", "wb") as buffer:
                merged_pdf.save(buffer)
            data["merge_type"] = "complete"
            c_ct += 1
        data["error"] = False
        pdf_data.append(data)
        pdf_progress.set_postfix({"s": s_ct, "i": i_ct, "c": c_ct, "e": e_ct})
    pd.DataFrame(pdf_data).to_csv(metadata_output)


if __name__ == "__main__":
    typer.run(main)
