# Prompt Log

## Prompt 1 — Initial plan request (plan mode)

I want to build a Streamlit app, app.py, that explores correlations between health measurements.
The app is about the CDC's 2017-2018 National Health and Nutrition Examination Survey (NHANES) using the nhanes_health.csv.  The app's goal is to meet these 5 criteria points:
1. Data preview. A short description of the dataset and a table of the rows.
2. Pairwise view. Two dropdowns pick X and Y. The app shows a scatter plot, the correlation r, and the number of participants n. The scatter plot has a trend line or binned means, and an option to color points by a health threshold such as SBP ≥ 130.
3. Correlation heatmap. The user picks which numeric variables to include. Every square shows its coefficient, and the color scale is fixed from −1 to 1.
4. Filters. Sidebar controls for sex and an age range that update every view: the table, scatter plot, r, n and heatmap.
5. Correlation method. A toggle between Pearson and Spearman that applies to both the pairwise view and the heatmap.
Next, the data should go into columns that are numeric.  "sex" should not go into any correlation.
If there is a missing value, it can be replaced with the average for the category.  n should be shown next to every r.  The heatmap colorscare should be coolwarm.
These are the constraints: Python, Streamlit, pandas and seaborn, one file called app.py, no other packages without asking.
I am asking for a plan, not code.  Please tell me if anything in my request is unclear.

## Prompt 2 — Answers to the agent's clarifying questions

- **Missing data:** Drop missing values for each pair (don't fill them with averages), so the app's r and n match pandas `.corr()`. The CSV has no missing values.
- **Packages:** Allow scipy and matplotlib. pandas needs scipy for Spearman, and seaborn draws with matplotlib.
