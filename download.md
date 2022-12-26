# Download Instructions

Requirements:
- `curl`
- `parallel` (optional)
- `zstd`

There are 3 source of data we want: the **(1) original PDF pages**, the **(2) images of the PDF pages**, and the **(3) labels**.

These commands download into an `./assets` folder, which should be included in this repo because we have a dummy `.gitkeep` file in there.

You can download the **(1) raw PDF pages** (92.5 GB) with this command:

```bash
curl -o assets/PubLayNet_PDF.tar.gz https://dax-cdn.cdn.appdomain.cloud/dax-publaynet/1.0.0/PubLayNet_PDF.tar.gz
```

You can use GNU Parallel to download the **(2) images of the PDF pages** in parallel with the following command:

```
parallel --jobs 7 curl -o ./assets/train-{}.tar.gz https://dax-cdn.cdn.appdomain.cloud/dax-publaynet/1.0.0/train-{}.tar.gz ::: {0..6}
```

All the files are quite large (13GB) and the whole thing is about 96GB in total. The output is going to be consumed by `parallel` until all the jobs are finished, so you can use someting like `watch -n1 du -sh assets` to track progress.

If you don't want to downlinad in parallel:

```
curl -o assets/publaynet.tar.gz https://dax-cdn.cdn.appdomain.cloud/dax-publaynet/1.0.0/publaynet.tar.gz
```

Finally you want the **(3) labels** (314 MB), which you can get with:

```bash
curl -o assets/labels.tar.gz https://dax-cdn.cdn.appdomain.cloud/dax-publaynet/1.0.0/labels.tar.gz
```