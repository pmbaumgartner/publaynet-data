# PubLayNet Merging Notes

The original data is split up by page into train/dev/and test. We want to merge individual pages back to their original document PDFs.

When we merge the individual pages back into whole documents, we consider 3 types of resulting PDFs:
- Single pages: there's only a single page, so page-to-page and document-level logic isn't possible to test
- Incomplete: The filenames have the PDF's identifier and page numbers (e.g. `PMC1064108_00003.pdf` is page 3) - if there is a gap in the page numbers, or the page numbers don't start at 0, we consider a PDF _incomplete_
- Complete: The number of pages in the merged PDF is equal to the range of page numbers from the filenames. Note that this is only _potentially complete_: the last page(s) of a PDF could have been removed, but the length of the PDF and the page number rage from the original data could still match.

Why is there incompleteness? They do some filtering on the PDFs so that their annotations are higher quality.

> Quality control: There are several sources that can lead to discrepancies between the PDF parsing results and the corresponding XML. When discrepancies are over the threshold dmax, the annotation algorithm may not be able to identify all elements in a document page. For example, PDFminer parses some complex inline formulas completely differently from the XML, which leads to a large Levenshtein distance and failure to match PDF elements with XML nodes. Hence we need a way to evaluate how well a PDF page is annotated and eliminate poorly annotated pages from PubLayNet. The annotation quality of a PDF page is defined as the ratio of the area of textboxes, images, and geometric shapes that are annotated to the area of textboxes, images, and geometric shapes within the main text box of the page. Non-title pages of which the annotation quality is less than 99% are excluded from PubLayNet, which is an extremely high standard to control the noise in PubLayNet at a low level. The format of title pages of different journals varies substantially. Miscellaneous information, such as manuscript history (dates of submission, revision, acceptance), copyright statement, editorial details, etc, is often included in title pages, but formatted differently from the XML representation and therefore missed in the annotations. To include adequate title pages, we set the threshold of annotation quality to 90% for title pages.

From reviewing PDFs manually, I've discovered this means that many of the Conclusion and References pages are excluded and even a "complete" PDF probably does not have the final pages in it.

**Errors**

Errors reading these PDFs were logged while merging. I haven't looked into them at all - they might be interesting test cases for handling parsing errors! 

```
Error on PDF ID PMC3116172
Error on PDF ID PMC3127127
Error on PDF ID PMC4143874
Error on PDF ID PMC4669305
Error on PDF ID PMC4708075
Error on PDF ID PMC4809603
Error on PDF ID PMC5021799
Error on PDF ID PMC5042923
Error on PDF ID PMC5042925
Error on PDF ID PMC5235335
Error on PDF ID PMC5345890
Error on PDF ID PMC5690398
Error on PDF ID PMC5690414
Error on PDF ID PMC5690448
Error on PDF ID PMC5828398
Error on PDF ID PMC5963116
Error on PDF ID PMC6023382
```

