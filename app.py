"""NHANES 2017-2018 Health Correlation Explorer."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="NHANES Correlation Explorer", layout="wide")

# ---------------------------------------------------------------------------
# Data and constants
# ---------------------------------------------------------------------------


@st.cache_data
def load_data():
    return pd.read_csv("nhanes_health.csv")


df = load_data()

# Only numeric columns can be correlated, so `sex` (text) is never included.
NUMERIC_COLS = df.select_dtypes("number").columns.tolist()

LABELS = {
    "age": "Age (years)",
    "bmi": "BMI (kg/m²)",
    "waist_cm": "Waist (cm)",
    "systolic_bp": "Systolic BP (mmHg)",
    "diastolic_bp": "Diastolic BP (mmHg)",
    "hba1c": "HbA1c (%)",
    "total_chol": "Total cholesterol (mg/dL)",
    "hdl_chol": "HDL cholesterol (mg/dL)",
    "sleep_hours": "Sleep (hours/night)",
    "sedentary_minutes": "Sedentary time (min/day)",
}


def label(col):
    return LABELS.get(col, col)


def low_hdl(data):
    # Low HDL: < 40 mg/dL for men, < 50 mg/dL for women
    limit = data["sex"].map({"Male": 40, "Female": 50})
    return data["hdl_chol"] < limit


# Name -> function returning a True/False Series for each participant
THRESHOLDS = {
    "Obesity: BMI ≥ 30": lambda d: d["bmi"] >= 30,
    "High BP: systolic ≥ 130": lambda d: d["systolic_bp"] >= 130,
    "High BP: diastolic ≥ 80": lambda d: d["diastolic_bp"] >= 80,
    "Diabetes: HbA1c ≥ 6.5": lambda d: d["hba1c"] >= 6.5,
    "High cholesterol: total ≥ 240": lambda d: d["total_chol"] >= 240,
    "Low HDL: < 40 (men) / < 50 (women)": low_hdl,
}


def corr_with_n(data, x, y, method):
    """Correlation of x and y plus the number of complete pairs used."""
    pair = data[[x, y]].dropna()
    return pair[x].corr(pair[y], method=method), len(pair)


# ---------------------------------------------------------------------------
# Sidebar: filters and method (feed every view below)
# ---------------------------------------------------------------------------

st.sidebar.header("Filters")
sex_choice = st.sidebar.radio("Sex", ["All", "Female", "Male"])
age_min, age_max = int(df["age"].min()), int(df["age"].max())
age_lo, age_hi = st.sidebar.slider(
    "Age range (80 means 80+)", age_min, age_max, (age_min, age_max)
)

st.sidebar.header("Correlation method")
method_name = st.sidebar.radio("Method", ["Pearson", "Spearman"])
method = method_name.lower()

sex_mask = df["sex"] == sex_choice if sex_choice != "All" else True
filtered = df[sex_mask & df["age"].between(age_lo, age_hi)]

filter_text = f"{sex_choice}, ages {age_lo}–{age_hi}"
st.sidebar.metric("Participants after filters", f"{len(filtered):,}")

# ---------------------------------------------------------------------------
# 1. Data preview
# ---------------------------------------------------------------------------

st.title("NHANES Health Correlation Explorer")
st.markdown(
    f"""
Data from the CDC's **2017–2018 National Health and Nutrition Examination Survey (NHANES)**:
{len(df):,} adults aged 20 and over, one row per participant. Columns cover body size
(BMI, waist), blood pressure, blood sugar (HbA1c), cholesterol (total, HDL), and
self-reported sleep and sitting time. Age is top-coded at 80 (80 means 80 or older).

NHANES oversamples some groups, so these correlations describe **this sample**, not the
US population.
"""
)

if len(filtered) < 3:
    st.warning("Fewer than 3 participants match these filters. Widen the age range or change the sex filter.")
    st.stop()

st.header("1. Data preview")
st.caption(f"Showing {len(filtered):,} of {len(df):,} participants ({filter_text}).")
st.dataframe(filtered, width="stretch", height=300)

# ---------------------------------------------------------------------------
# 2. Pairwise view
# ---------------------------------------------------------------------------

st.header("2. Pairwise view")

c1, c2 = st.columns(2)
x = c1.selectbox("X variable", NUMERIC_COLS, index=NUMERIC_COLS.index("age"), format_func=label)
y = c2.selectbox("Y variable", NUMERIC_COLS, index=NUMERIC_COLS.index("systolic_bp"), format_func=label)

c3, c4 = st.columns(2)
trend = c3.radio("Trend", ["Linear trend line", "Binned means"], horizontal=True)
color_by = c4.selectbox("Color points by", ["None"] + list(THRESHOLDS))

if x == y:
    st.info("Pick two different variables to see their correlation.")
else:
    r, n = corr_with_n(filtered, x, y, method)
    m1, m2, m3 = st.columns(3)
    m1.metric(f"{method_name} r", f"{r:.3f}")
    m2.metric("n (participants)", f"{n:,}")
    m3.metric("Filters", filter_text)

    plot_df = filtered[[x, y]].dropna().copy()
    hue = None
    if color_by != "None":
        # Threshold uses its own column(s), which may not be X or Y
        flag = THRESHOLDS[color_by](filtered).loc[plot_df.index]
        plot_df[color_by] = flag.map({True: "Yes", False: "No"})
        hue = color_by

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=plot_df, x=x, y=y, hue=hue, hue_order=["No", "Yes"] if hue else None,
        palette={"No": "tab:blue", "Yes": "tab:red"} if hue else None,
        s=12, alpha=0.4, edgecolor=None, ax=ax,
    )
    if trend == "Linear trend line":
        sns.regplot(data=plot_df, x=x, y=y, scatter=False, ci=None, color="black", ax=ax, label="Linear trend")
    else:
        bins = pd.qcut(plot_df[x], q=10, duplicates="drop")
        binned = plot_df.groupby(bins, observed=True).agg(x_mean=(x, "mean"), y_mean=(y, "mean"))
        ax.plot(binned["x_mean"], binned["y_mean"], "o-", color="black", lw=2, label="Binned means (deciles of X)")
    ax.set_xlabel(label(x))
    ax.set_ylabel(label(y))
    ax.set_title(f"{label(y)} vs {label(x)}  —  {method_name} r = {r:.3f}, n = {n:,}")
    ax.legend(loc="best", fontsize=8)
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Caution: an r near zero does not mean \"no relationship\". A U-shaped pattern "
        "(like sleep, where both short and long sleep can be unhealthy) can give r ≈ 0. "
        "Try **Binned means** to see curved patterns."
    )

# ---------------------------------------------------------------------------
# 3. Correlation heatmap
# ---------------------------------------------------------------------------

st.header("3. Correlation heatmap")

cols = st.multiselect("Variables to include", NUMERIC_COLS, default=NUMERIC_COLS, format_func=label)

if len(cols) < 2:
    st.info("Pick at least two variables.")
else:
    corr = filtered[cols].corr(method=method)
    # n for each pair (complete cases); equal to the filtered row count when nothing is missing
    notna = filtered[cols].notna().astype(int)
    n_pairs = notna.T @ notna
    n_values = set(n_pairs.values.ravel())

    if len(n_values) == 1:
        annot, fmt = True, ".2f"
        n_text = f"n = {n_values.pop():,} participants"
    else:
        annot = corr.round(2).astype(str) + "\nn=" + n_pairs.astype(str)
        fmt = ""
        n_text = "n shown in each square"

    size = max(6, 0.8 * len(cols) + 2)
    fig, ax = plt.subplots(figsize=(size, size * 0.8))
    sns.heatmap(
        corr, annot=annot, fmt=fmt, cmap="coolwarm", vmin=-1, vmax=1, center=0,
        square=True, linewidths=0.5, cbar_kws={"label": f"{method_name} r"},
        xticklabels=[label(c) for c in cols], yticklabels=[label(c) for c in cols],
        annot_kws={"size": 8}, ax=ax,
    )
    ax.set_title(f"{method_name} r  —  {n_text} ({filter_text})")
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Colors are fixed from −1 (blue) to +1 (red), so a pale square always means a weak correlation.")
