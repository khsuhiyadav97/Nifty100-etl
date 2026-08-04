# Sprint 3 Retro (Day 15-21) - Screener, Health Score, Sector/Peer Analytics

## what I built
- screener engine that reads presets from a yaml config instead of hardcoding
  filters in python - 6 named presets (quality compounder, value pick, growth
  accelerator, dividend champion, debt free blue chip, turnaround watch)
- composite ranking score - turned a bunch of different ratios into one 0-100
  score per company using percentile normalization so stuff on totally
  different scales (like ROE% vs D/E ratio) can actually be compared fairly
- peer comparison engine - instead of ranking every company against the whole
  universe, rank them only against their actual peers (private banks vs
  private banks, not vs an FMCG company). computed percentile ranks within
  each of the 11 peer groups
- radar charts for 55 companies showing them vs their peer group average
- peer_comparison.xlsx with colour coded cells across 11 sheets, one per group

## what actually went well
found some genuinely interesting stuff, not just "code ran successfully."
like ICICIBANK actually ranks higher than HDFCBANK (the official benchmark)
on ROE within private banks - the kind of insight that makes this feel like
actual analysis instead of just plumbing data around.

also got smarter about not over-engineering. was about to generate 92 static
PNG files nobody would ever look at until I stepped back and asked if that's
even useful, ended up building it so you can preview a few charts quickly
OR generate the full batch when you actually need the files, not both by
default.

## what messed me up
- guessed the wrong file structure for peer_groups.xlsx before actually
  looking at it (assumed comma-separated members in one row per group, turned
  out it was already one row per company). wasted a run figuring that out
  instead of just checking the file first
- growth component of the composite score is still missing bc it needs the
  CAGR numbers merged in properly, had to re-normalize the weights so the
  score doesn't look artificially low. need to actually go back and wire that
  up properly instead of leaving it as a workaround

## what to fix next sprint
- actually merge CAGR data into financial_ratios so the composite score can
  use the full weighting from the spec instead of a patched version
- look into why SBIN keeps showing up with missing data across peer stuff,
  probably a data gap worth tracking down properly instead of just skipping it