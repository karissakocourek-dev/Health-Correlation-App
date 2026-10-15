# Plan: NHANES Health Correlation Explorer (`app.py`)

## Context
For the M9 exercise, build one Streamlit file, `app.py`, for exploring correlations in `nhanes_health.csv`. The file holds 4,433 NHANES 2017–2018 adults, aged 20+, with 11 columns. The app must have the 5 required features: data preview, pairwise view, heatmap, sidebar filters, and a Pearson/Spearman toggle. Its r and n must match pandas run by hand on the same filtered data, because Part 4 of the exercise checks them that way.

**What I found in the data:** `sex` is text (Female 2263, Male 2170). The other 10 columns are numeric: age, bmi, waist_cm, systolic_bp, diastolic_bp, hba1c, total_chol, hdl_chol, sleep_hours, sedentary_minutes. **No column has a missing value.** Age 80 means "80 or older."

**Decisions made with the user:**
- Missing values are **dropped per pair of variables, not filled**, which is what pandas `.corr()` does. Today nothing is missing, so n = the number of rows left after filtering.
- Allowed packages: streamlit, pandas, seaborn, plus **matplotlib**, which seaborn needs and which draws the plots, and **scipy**, which pandas needs for Spearman.

## Clarifications on the original request
1. *"The data should go into columns that are numeric"*: read as "the variables offered for correlation are the 10 numeric columns." `sex` is used only as a filter and for the table.
2. *"Replace missing values with the average"*: changed to dropping missing values, as above. Filling with averages would make r and n differ from the hand-run pandas checks.
3. *Health threshold for coloring*: the app offers every clinical cut-off in the data dictionary, not only SBP ≥ 130.
4. *n next to every r on the heatmap*: when nothing is missing, n is the same for every square, so it goes in the heatmap title. If missing values ever appear, each square's label shows both r and its own n.

## Build order (all in `app.py`, one step at a time, with a run check after each)

**Step 1: Load data and set constants**
- Load the file with `@st.cache_data def load_data()` and `pd.read_csv("nhanes_health.csv")`, using the relative path so the deployed app finds it.
- `NUMERIC_COLS` = every column except `sex`, chosen with `select_dtypes("number")` so `sex` can never be included.
- `LABELS` dictionary: column name → readable label with units, such as "Systolic BP (mmHg)".
- `THRESHOLDS` dictionary: name → (column, cut-off, ≥ or <):
  - BMI ≥ 30
  - SBP ≥ 130
  - DBP ≥ 80
  - HbA1c ≥ 6.5
  - Total cholesterol ≥ 240
  - Low HDL (< 40 for men, < 50 for women; or < 40 for everyone, to keep it simple)

**Step 2: Sidebar filters and method toggle** (this one filtered DataFrame feeds every view)
- Sex: `st.sidebar.radio` with All / Female / Male.
- Age range: `st.sidebar.slider` from 20 to 80, defaulting to the full range.
- Method: `st.sidebar.radio` with Pearson / Spearman.
- Build `filtered = df[sex_mask & df["age"].between(lo, hi)]`. **Every view below uses only `filtered`**, which gives filters → table, scatter, r, n and heatmap.
- Show the number of rows left after filtering in the sidebar.
- If fewer than 3 rows remain, show `st.warning` and `st.stop()`.

**Step 3: Data preview (feature 1)**
- A short description of NHANES 2017–2018, the 4,433 adults, what each column measures, and the note that age 80 means 80+.
- A caution that this is a sample, not the US population.
- `st.dataframe(filtered)`, captioned with "showing N of 4,433 participants."

**Step 4: Pairwise view (feature 2)**
- Two `st.selectbox` controls for X and Y, choosing from `NUMERIC_COLS`. Defaults are age and systolic_bp, which is verification check 1.
- One helper, `corr_with_n(data, x, y, method)`:
  - `pair = data[[x, y]].dropna()`
  - returns `(pair[x].corr(pair[y], method=method), len(pair))`
  - The pairwise view and the heatmap labels both use this helper, so their numbers come from the same code.
- Show `st.metric` boxes for r (3 decimals) and n, side by side, labeled with the method.
- Plot options:
  - a radio for the trend: linear trend line (`sns.regplot`, no confidence band) or binned means (cut X into about 10 quantile bins, plot the mean Y per bin). Binned means show curved patterns such as sleep.
  - a selectbox "Color points by" with None plus each entry in `THRESHOLDS`. The chosen threshold becomes a True/False column used as `hue` in `sns.scatterplot`, with small, semi-transparent points.
- If X equals Y, show a note instead of a plot.
- Add a caption with the M9 caution: an r near 0 does not mean no relationship.

**Step 5: Correlation heatmap (feature 3)**
- `st.multiselect` to choose variables from `NUMERIC_COLS`, defaulting to all 10, with a minimum of 2.
- Correlation matrix: `filtered[cols].corr(method=method)`. pandas drops missing values per pair, which is consistent with the pairwise view.
- Draw with `sns.heatmap(annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, center=0, square=True)` so the colors always run from −1 to 1.
- Title: "{Method} r — n = {N} participants ({sex}, ages {lo}–{hi})".

**Step 6: Polish**
- `st.set_page_config(layout="wide")`, section headers, and readable labels on the axes.
- Close each figure with `plt.close(fig)` so figures don't pile up in memory.
- Write `requirements.txt` with streamlit, pandas, seaborn, matplotlib and scipy. This step creates a second file, but that file is required for deployment.

## Critical files
- `app.py` (new, the only code file)
- `requirements.txt` (new, needed for Part 5)
- `nhanes_health.csv` (read only)

## Verification
1. Run: `uv run --with streamlit,pandas,seaborn,scipy streamlit run app.py`
2. Click through every control. Changing sex or age must change the table row count, the scatter, r, n and the heatmap title and values.
3. Compute the verification-table values in pandas by hand and compare them with the app:
   ```python
   df = pd.read_csv("nhanes_health.csv")
   df["age"].corr(df["systolic_bp"]), len(df)                      # check 1
   f = df[df.sex == "Female"]; f["age"].corr(f["systolic_bp"]), len(f)  # check 4
   ```
   Also run checks 2, 3 and 5, and the same values with `method="spearman"`.
4. With Female selected, the heatmap's age/systolic_bp square should equal check 4, rounded to 2 decimals.
5. Edge cases:
   - an age range of one year
   - deselecting heatmap variables until only one is left
   - X = Y
