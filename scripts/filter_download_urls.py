import json
from pathlib import Path
import typer


def filter_files(input_urls: Path):
    for line in input_urls.read_text().splitlines():
        data = json.loads(line)
        if data["error"] is None:
            # the first element is the API URL we got the file URL from
            print(data["url"][1])


if __name__ == "__main__":
    typer.run(filter_files)
