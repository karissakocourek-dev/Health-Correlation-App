Copy this table into `verification.md` and fill it in:

| # | Check | App shows | pandas gives | Match? |
|---|---|---|---|---|
| 1 | r for `age` vs `systolic_bp`, all participants |0.463|0.463|Yes|
| 2 | r for `bmi` vs `waist_cm`, all participants |0.903|0.903|Yes|
| 3 | r for `waist_cm` vs `hdl_chol`, all participants |-0.335|-0.335|Yes|
| 4 | r and n for `age` vs `systolic_bp`, **Female only** |0.555|0.555|Yes|
| 5 | r and n for `age` vs `systolic_bp`, **Male only** |0.351|0.351|Yes|
| 6 | With the filter set to Female, does the heatmap's `age`/`systolic_bp` square match row 4? |0.56|0.555|Yes|