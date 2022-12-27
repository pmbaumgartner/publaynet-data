# PubLayNet - Full PDF Subset Download Pipeline

This repository is a data processing pipeline intended to download and extract full PDFs sourced from [PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet). 

The steps are all documented in the [`Taskfile.yml`](https://taskfile.dev/) file. This means you'll need to install [Taskfile](https://taskfile.dev/installation/) to replicate this workflow. If you don't want to do that, you can copy/paste the commands in the file into your own terminal, but none of the nice features of taskfile (e.g. checking if inputs have changed) will be available.

## Steps

1. We download the full set of PDFs from PubLayNet and extract them.
2. We validate that any article is unique to the given train/dev/test splits. (It should be, they split it by journal)
3. The original PDF files are single pages from an article, in the format `<PMID_PAGE>.pdf`. We merge the single page PDF files from an article into one PDF per article. 
4. Once PDFs are merged, we identify potentially "complete" article PDFs: defined as PDFs that are more than a single page, and consist of pages from the minimum page number (0) to the maximum page number.
   1. There are **`9131`** of these.
   2. For more details, see [`merging_nodes.md`](merging_notes.md).
   3. Information on this process (split, page numbers) is in `data/merged_metadata.csv`.
5. We make requests to the PubMed Open Access API to find the URL on their FTP to download the full versions of the _complete_ pdfs.
   1. We made successful requests for **`9124`** articles. You can see these in `data/download_urls.jsonl`.
6. Given the article file URL, we download the article's `.tar.gz` archive, which contains the article's PDF and other supplementary files.
   1. We successfully downloaded **`9124`** article archives.
7. We extract the archive files then remove any non PDF files from those subfolders.
   1. This results in **`8681`** folders with a single PDF.
8. We celebrate with our **`8681`** full PDFs! 🎉


## Statistics
_This comes from the `compress-pubmed-articles` task with the `--verbose` flag on the command._

```
Total Folders: 9827
Folders with single PDF: 8681
  N PDFs per Folder   
┏━━━━━━━━┳━━━━━━━━━━━┓
┃        ┃ Frequency ┃
┃ N PDFs ┃ (# PMIDs) ┃
┡━━━━━━━━╇━━━━━━━━━━━┩
│ 1      │      8681 │
│ 2      │       343 │
│ 3      │        49 │
│ 4      │        16 │
│ 7      │        10 │
│ 5      │        10 │
│ 6      │         6 │
│ 10     │         2 │
│ 8      │         2 │
│ 21     │         1 │
│ 14     │         1 │
│ 13     │         1 │
│ 9      │         1 │
└────────┴───────────┘

Page Count Statistics 
┏━━━━━━━━━━━┳━━━━━━━━┓
┃ Statistic ┃  Value ┃
┡━━━━━━━━━━━╇━━━━━━━━┩
│ count     │ 8681.0 │
│ mean      │   7.31 │
│ std       │   3.68 │
│ min       │    2.0 │
│ 25%       │    5.0 │
│ 50%       │    7.0 │
│ 75%       │    9.0 │
│ max       │   79.0 │
└───────────┴────────┘
    Page Differences between    
 PubLaynet and PubMed Download  
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ PMID - PDF ┃ Page Difference ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ count      │          8681.0 │
│ mean       │             3.3 │
│ std        │             2.7 │
│ min        │            -4.0 │
│ 25%        │             2.0 │
│ 50%        │             2.0 │
│ 75%        │             4.0 │
│ max        │            75.0 │
└────────────┴─────────────────┘
 Page Differences between PubLaynet 
        and PubMed Download         
       (as % of PubMed Pages)       
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ PMID - PDF ┃ Page Difference (%) ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ count      │              8681.0 │
│ mean       │                56.9 │
│ std        │                19.4 │
│ min        │                 5.1 │
│ 25%        │                42.9 │
│ 50%        │                60.0 │
│ 75%        │                71.4 │
│ max        │               157.1 │
└────────────┴─────────────────────┘
            Articles with Fewer Pages in PubMed Download            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃                                           ┃      Page Difference ┃
┃ PMID - PDF                                ┃ (PubMed - PubLayNet) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ PMC5398342 - ckw142.pdf                   │           -2 (5 - 7) │
│ PMC4794278 - cddiscovery201526.pdf        │          -2 (9 - 11) │
│ PMC4868398 - 10.1177_2333393614565183.pdf │          -3 (9 - 12) │
│ PMC4639696 - main.pdf                     │         -2 (11 - 13) │
│ PMC5804988 - S2059866117002941a.pdf       │           -1 (2 - 3) │
│ PMC6027614 - 41205_2016_Article_5.pdf     │           -1 (6 - 7) │
│ PMC5833946 - cix705.pdf                   │           -1 (3 - 4) │
│ PMC4678587 - JACE-98-3047.pdf             │           -2 (7 - 9) │
│ PMC4760696 - dvv008.pdf                   │          -3 (8 - 11) │
│ PMC5846682 - npjscilearn201615.pdf        │          -4 (7 - 11) │
│ PMC4380276 - mic-01-267.pdf               │           -1 (3 - 4) │
│ PMC4740918 - AJLM-2-31.pdf                │           -1 (7 - 8) │
│ PMC4811365 - vev005.pdf                   │         -4 (10 - 14) │
│ PMC4793549 - 40814_2015_Article_22.pdf    │          -2 (8 - 10) │
│ PMC5176077 - archdischild-2016-310875.pdf │           -1 (4 - 5) │
│ PMC5256467 - 41235_2016_Article_25.pdf    │         -2 (13 - 15) │
└───────────────────────────────────────────┴──────────────────────┘
   Full Articles in   
   Original Dataset   
        Splits        
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ Split ┃ N Articles ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ dev   │        153 │
│ test  │        136 │
│ train │       8392 │
└───────┴────────────┘
N Annotated Pages from
 Full Article set in  
   Original Dataset   
        Splits        
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ Split ┃ N Articles ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ dev   │        341 │
│ test  │        303 │
│ train │      34509 │
└───────┴────────────┘
Total Pages from Full 
    Article set in    
   Original Dataset   
        Splits        
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ Split ┃ N Articles ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ dev   │       1222 │
│ test  │        983 │
│ train │      61268 │
└───────┴────────────┘
```
