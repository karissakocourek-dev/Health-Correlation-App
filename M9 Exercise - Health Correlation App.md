# M9 Exercise: Build a Health Correlation Explorer with an AI Agent

You will use an AI coding agent to build a **Streamlit** app that explores correlations in real health data, check its numbers yourself in pandas, and then publish it online. The agent writes the code, but **you are responsible for the numbers**.

## Your app must include
1. **Data preview.** A short description of the dataset and a table of the rows.
2. **Pairwise view.** Two dropdowns pick X and Y. The app shows a scatter plot, the **correlation r**, and the **number of participants n**. The scatter plot has a trend line or binned means, and an option to color points by a health threshold such as SBP ≥ 130.
3. **Correlation heatmap.** The user picks which numeric variables to include. Every square shows its coefficient, and the color scale is **fixed from −1 to 1**.
4. **Filters.** Sidebar controls for **sex** and an **age range** that update *every* view: the table, scatter plot, r, n and heatmap.
5. **Correlation method.** A toggle between **Pearson** and **Spearman** that applies to both the pairwise view and the heatmap.

Keep the two cautions from the M9 notebook in mind:
- An r near zero does not mean "no relationship" (remember the U-shaped sleep curve).
- A heatmap is only honest if its colors run from −1 to 1.

**You will submit:** a link to your GitHub repository and a link to your deployed Streamlit app.

## Part 0: Setup

1. Make a new folder, put `nhanes_health.csv` in it, and open your coding agent in that folder.
2. Run the app with:
   ```bash
   uv run --with streamlit,pandas,seaborn,scipy streamlit run app.py
   ```

## Part 1: The data

`nhanes_health.csv` holds **4,433 adults aged 20 and over** from the CDC's 2017–2018 National Health and Nutrition Examination Survey (NHANES). Each row is one participant.

| Column | Meaning | Units | Health problem it measures |
|---|---|---|---|
| `age` | Age at screening (80 means 80 or older) | years | |
| `sex` | `Female` or `Male` | text | |
| `bmi` | Body mass index | kg/m² | Obesity: 30 or above |
| `waist_cm` | Waist circumference | cm | Obesity (abdominal) |
| `systolic_bp` | Mean of up to 3 systolic readings | mmHg | High blood pressure: 130 or above |
| `diastolic_bp` | Mean of up to 3 diastolic readings | mmHg | High blood pressure: 80 or above |
| `hba1c` | Glycohemoglobin, average blood sugar over about 3 months | % | Diabetes: 6.5 or above |
| `total_chol` | Total cholesterol | mg/dL | High cholesterol: 240 or above |
| `hdl_chol` | HDL ("good") cholesterol | mg/dL | Low HDL is a risk factor |
| `sleep_hours` | Usual sleep on workdays (self-reported) | hours | |
| `sedentary_minutes` | Time spent sitting on a typical day (self-reported) | minutes | |

NHANES oversamples some groups, so these correlations describe *this sample*, not the US population.

## Part 2: Plan with your agent

### Step 1: Write your first prompt

Switch your agent to **plan mode** (or start your message with *"Don't write any code yet."*). Then write one message, in plain paragraphs, describing the app you want. Point the agent at `nhanes_health.csv` instead of retyping the data dictionary. Your message must cover:

- **The goal** and the five required features
- **The data:** which columns are numeric, and that `sex` must not go into any correlation
- **The filters** and what each one must affect
- **Rules for the numbers:** how missing values are handled, the heatmap color scale, and showing n next to every r
- **Constraints:** Python, Streamlit, pandas and seaborn (or plotly), one file called `app.py`, no other packages without asking
- **A request for a plan, not code:** the build order, how the filters feed every view, the command to run the app, and anything in your request that is unclear

For example, your message might begin:

> I want to build a Streamlit app, `app.py`, that explores correlations between health measures in `nhanes_health.csv`. Read the CSV first. Every numeric column except…

Save your message as the first entry in `prompts.md`.

### Step 2: Review the plan

Before you approve the plan, check that it:

- [ ] includes **all five required features**
- [ ] computes r and n from the **filtered** data in every view
- [ ] leaves **`sex`** out of the correlations
- [ ] fixes the heatmap colors to **−1 to 1**
- [ ] shows **n** next to every r
- [ ] builds a little at a time, starting with the data and filters
- [ ] uses only the packages you allowed

If anything is missing, ask for a revised plan. When it passes, save it as `plan.md`.

## Part 3: Build

Leave plan mode and have the agent build the app. Describe what you *see* when something is wrong ("the heatmap doesn't change when I pick Female"). Add each prompt to `prompts.md`.

## Part 4: Verify

Treat your app as untrusted. For each check, read the value from **your app**, then compute it yourself in pandas (not with the agent):

```python
import pandas as pd
df = pd.read_csv("nhanes_health.csv")
f = df[(df["sex"] == "Female") & df["age"].between(40, 59)]
f["age"].corr(f["systolic_bp"]), len(f)
```

Copy this table into `verification.md` and fill it in:

| # | Check | App shows | pandas gives | Match? |
|---|---|---|---|---|
| 1 | r for `age` vs `systolic_bp`, all participants | | | |
| 2 | r for `bmi` vs `waist_cm`, all participants | | | |
| 3 | r for `waist_cm` vs `hdl_chol`, all participants | | | |
| 4 | r and n for `age` vs `systolic_bp`, **Female only** | | | |
| 5 | r and n for `age` vs `systolic_bp`, **Male only** | | | |
| 6 | With the filter set to Female, does the heatmap's `age`/`systolic_bp` square match row 4? | | | |


If a check fails, describe the mismatch to your agent, fix it, and log that prompt.

## Part 5: Publish to GitHub and Streamlit

1. Have your agent create `requirements.txt` listing every package `app.py` imports (e.g. `streamlit`, `pandas`, `seaborn`, `scipy`, and `plotly` if used). Check that `app.py` loads the CSV with the relative path `nhanes_health.csv`.
2. Create a **public** GitHub repository to host your work. It should contain:

   | File | What it is |
   |---|---|
   | `app.py` | Your Streamlit app |
   | `requirements.txt` | Packages Streamlit installs when it deploys the app |
   | `nhanes_health.csv` | The data the app loads |
   | `prompts.md` | Your prompt log, starting with your first prompt |
   | `plan.md` | The plan you approved |
   | `verification.md` | The completed verification table, the M9 trap and your code check |
3. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and click **Create app**. Choose your repository, branch `main`, and main file `app.py`, then click **Deploy**.
4. Open the deployed app and confirm that check 4 gives the same r and n as your local app.

## Submit

- Your GitHub repository URL
- Your deployed Streamlit app URL
