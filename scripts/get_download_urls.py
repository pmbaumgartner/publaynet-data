import json
from dataclasses import asdict, dataclass
from functools import partial
from pathlib import Path
from time import sleep
from typing import List, NewType, Optional, Tuple
import typer

import requests
import xmltodict
from pqdm.processes import pqdm

SourceURL = NewType("SourceURL", str)
FileURL = NewType("FileURL", str)
Error = NewType("Error", str)


@dataclass
class URLResult:
    url: Optional[Tuple[SourceURL, FileURL]] = None
    error: Optional[Tuple[SourceURL, Error]] = None

    def dict(self):
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.dict())


BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={}"


def get_download_link(pubmed_id: str, pause: float = 0.5):
    """Makes a request to the OA Service API, which returns XML containing the hyperlink
    to download the corresponding .tgz file.

    ref: https://www.ncbi.nlm.nih.gov/pmc/tools/oa-service/

    Example format:

    ```xml
    <OA>
    <responseDate>2019-01-28 10:41:16</responseDate>
    <request id="PMC5334499">https://www.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id=PMC5334499</request>
    <records returned-count="2" total-count="2">
        <record id="PMC5334499" citation="World J Radiol. 2017 Feb 28; 9(2):27-33"
            license="CC BY-NC" retracted="no">
        <link format="tgz" updated="2017-03-17 13:10:45"
            href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/8e/71/PMC5334499.tar.gz"/>
        <link format="pdf" updated="2017-03-03 06:05:17"
            href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/8e/71/WJR-9-27.PMC5334499.pdf"/>
        </record>
    </records>
    </OA>
    ```
    """
    url = BASE_URL.format(pubmed_id)
    try:
        r = requests.get(url)
        sleep(pause)
        if r.status_code != 200:
            return URLResult(error=(SourceURL(url), Error("Response != 200")))
        data = xmltodict.parse(r.text)
        try:
            link = data["OA"]["records"]["record"]["link"]
        except KeyError:
            return URLResult(
                error=(
                    SourceURL(url),
                    Error("Data not available from record (KeyError)"),
                )
            )
        if link["@format"] == "tgz":
            # some links have a separate PDF link, but all of them have the tgz file
            # which contains the PDF, so we'll use that for consistency
            download_link = link["@href"]
            return URLResult(url=(SourceURL(url), FileURL(download_link)))
        else:
            return URLResult(
                error=(SourceURL(url), Error("tar.gz not available on URL"))
            )
    except Exception as e:
        return URLResult(error=(SourceURL(url), Error(str(e))))


def main(
    source_dir: Path = typer.Argument(
        ...,
        help="A directory of PDF files, where the filenames are PMIDs (ex. 'PMC3922247.pdf')",
        file_okay=False,
        dir_okay=True,
    ),
    output: Path = typer.Argument(
        ...,
        help="An output .jsonl file to store the article download links (or errors in requesting the link)",
        file_okay=True,
        dir_okay=False,
    ),
    pause: float = typer.Option(
        0.2,
        help="Amount of time to wait between requests (to be nice)",
    ),
    n_jobs: int = typer.Option(
        8,
        help="Number of parallel requests to make",
    ),
):
    completed_pdfs = list(source_dir.glob("*.pdf"))
    pubmed_ids = [f.stem for f in completed_pdfs]

    results: List[URLResult] = []

    download_wait = partial(get_download_link, pause=pause)
    results = pqdm(pubmed_ids, download_wait, n_jobs=n_jobs)
    if output.exists():
        output.unlink()
    with open(output, "a") as f:
        for result in results:
            f.write(result.json() + "\n")


if __name__ == "__main__":
    typer.run(main)
