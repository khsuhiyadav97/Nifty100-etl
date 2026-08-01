# Sprint 2 Retro (Day 8-14) - Ratio Engine

okay so sprint 1 was just getting the data clean and into a database, doesn't
really tell you anything about the companies tbh, its just numbers sitting there.
sprint 2 is where it actually starts meaning something.

## what I built
- profitability stuff - NPM, OPM, ROE, ROCE for every company every year
- leverage stuff - debt to equity (banks get a pass on high debt since thats
  normal for them), interest coverage, asset turnover
- CAGR engine - how fast is revenue/profit/eps actually growing over 3/5/10yrs.
  this one was annoying bc growth rate math literally breaks when a company had
  a loss year, so had to handle like 5 different weird cases instead of just
  running the formula blindly
- cash flow stuff - is the profit real cash or just paper. free cash flow,
  cfo/pat ratio, capex intensity, and a thing that classifies each company into
  8 behavior patterns based on their cash flow signs lol
- sector-relative ROCE for banks - normal ROCE benchmark doesnt work for them
  so compared them to their own sector instead
- wrote 22 tests for all of this, all green
- finally dumped everything into an actual financial_ratios table in the db
  instead of just printing stuff and hoping

## what actually went well
every formula handles its own edge cases (zero sales, negative equity etc)
instead of just crashing or spitting out garbage numbers. and it wasnt just
theory either - found real companies in the data hitting these cases, like
ADANIGREEN literally going from loss to profit which triggered my turnaround
flag. felt good seeing it actually catch something real instead of just
passing on fake test data.

also caught a dumb mistake myself - was comparing one single "latest" roce
number against like 11 years of history for the same company which obviously
never matches, fixed it to only compare the latest year properly.

## what to fix next time
- naming files properly from the start istg. renamed like 3 files mid sprint
  bc of typos/mismatches and it broke my tests for no reason
- should probably load stuff into the db earlier instead of leaving it all in
  dataframes till the very end