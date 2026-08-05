# Sprint 3 Retro (Day 15–21): Screener, Health Score & Sector/Peer Analytics

## What I Built

This sprint, I focused on making the stock analysis system more flexible and useful.

* Built a **screener engine** that reads screening rules from a YAML configuration file instead of hardcoding filters in Python. I added six presets: **Quality Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue Chip, and Turnaround Watch**.
* Created a **composite ranking score** that combines multiple financial ratios into a single score out of 100. Since metrics such as ROE and Debt-to-Equity are measured on completely different scales, I used percentile normalization to make them comparable.
* Developed a **peer comparison engine** that compares companies with relevant peers rather than ranking every company against the entire dataset. For example, private banks are compared with other private banks instead of unrelated companies such as FMCG companies. I calculated percentile rankings across 11 peer groups.
* Generated **radar charts for 55 companies**, showing each company’s performance compared with its peer-group average.
* Created a **peer_comparison.xlsx** file with colour-coded comparisons across 11 sheets, with one sheet for each peer group.

## What Went Well

The best part of this sprint was finding insights that felt genuinely useful rather than simply getting the code to run.

For example, **ICICI Bank ranked higher than HDFC Bank on ROE within the private banking peer group**, even though HDFC Bank was used as the official benchmark. Findings like this made the project feel more like actual financial analysis and less like just building data pipelines.

I also made a better decision around over-engineering. Initially, I planned to generate 92 static PNG charts, but I realised that most of them would probably never be viewed. Instead, I changed the workflow so that a few charts can be previewed quickly, while the full batch can still be generated when needed. This made the process more practical without removing functionality.

## What Didn’t Go Well

* I assumed the structure of `peer_groups.xlsx` before checking the file. I expected each peer group to contain comma-separated company names in a single row, but the file was already structured with one company per row. This caused an unnecessary failed run and was a reminder to inspect the source data before designing the processing logic.
* The **growth component of the composite score is still incomplete** because the CAGR data has not yet been merged properly. For now, I re-normalized the remaining weights so the overall score would not appear artificially low. However, this is only a temporary workaround and needs to be fixed properly.

## What I’ll Fix Next Sprint

* Merge the CAGR data into `financial_ratios` so the composite score can use the complete weighting defined in the original specification.
* Investigate why **SBIN** repeatedly appears with missing data in the peer analysis. Rather than continuing to skip it, I want to identify whether the issue comes from a missing source value, a company-name mismatch, or an error during data processing.
