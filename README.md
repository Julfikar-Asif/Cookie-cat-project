# Cookie Cats A/B Test Dashboard

An end-to-end analytics project that evaluates whether placing the Cookie Cats
level gate at level 30 or level 40 affects player retention and engagement.

The project includes:

- A Streamlit dashboard for interactive analysis
- A reproducible Python analysis pipeline
- SQL queries for key metrics
- Power BI files for report creation
- Statistical tests, bootstrap confidence intervals, and data-quality reports

## Results at a glance

| Experiment version | Players | D1 retention | D7 retention | Median rounds |
|---|---:|---:|---:|---:|
| `gate_30` | 44,699 | 44.82% | 19.02% | 17 |
| `gate_40` | 45,489 | 44.23% | 18.20% | 16 |

Gate 30 has higher observed retention and median engagement. The day-7
retention difference is **+0.82 percentage points** in favor of Gate 30, with a
95% confidence interval of **+0.31 to +1.33 percentage points** and a p-value
of **0.001592**.

The recommendation is to keep Gate 30 as the preferred default. This conclusion
should be confirmed with revenue, acquisition source, device, country, and
longer-term retention data before a permanent product decision.

## Streamlit dashboard

The dashboard provides:

- Experiment-version filters
- Player-activity segment filters
- Player-count and retention KPI cards
- Retention charts by experiment version
- Segment-level retention comparisons
- A detailed segment summary table

### Run locally 

Create or activate the project environment:


Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the dashboard:

```powershell
python -m streamlit run dashboard_app.py
```

Open the URL shown in the terminal, normally
[http://localhost:8501](http://localhost:8501). Stop the app with `Ctrl+C`.

The dashboard reads its source data from
[`data/cookie_cats.csv`](data/cookie_cats.csv), so that file must remain in the
repository when deploying or sharing the app.

## Deploy to Streamlit Community Cloud

Streamlit Community Cloud deploys from a remote GitHub repository. The local
Conda environment is not uploaded; Streamlit installs the packages listed in
[`requirements.txt`](requirements.txt).

### 1. Create a GitHub repository

Create an empty repository on GitHub, for example:

```text
cookie-cats-dashboard
```

Do not add a second README, `.gitignore`, or license if those files already
exist locally.



### 3. Deploy the app

1. Open [Streamlit Community Cloud](https://share.streamlit.io/).
2. Select **New app**.
3. Choose the GitHub repository and the `main` branch.
4. Set the main file to `dashboard_app.py`.
5. Select **Deploy**.

The repository must include at least:

```text
dashboard_app.py
requirements.txt
data/cookie_cats.csv
```

## Reproduce the analysis

Run the analysis pipeline from the project root:

```powershell
python scripts\analyze_cookie_cats.py
```

The pipeline performs source loading, type conversion, outlier filtering,
segment creation, data-quality checks, Power BI export generation, retention
tests, bootstrap confidence intervals, and report generation.

## Project structure

```text
.
├── dashboard_app.py                 # Streamlit dashboard
├── data/
│   ├── cookie_cats.csv              # Source player-level dataset
│   └── cookie_cats.db               # SQLite data source
├── dashboard/                       # Power BI-ready CSV exports
├── reports/                         # Statistical and quality reports
├── scripts/
│   └── analyze_cookie_cats.py       # Reproducible analysis pipeline
├── sql/                             # SQL analysis queries
├── powerbi/                          # Power Query and DAX files
├── 01_analysis.ipynb                # Exploratory analysis notebook
├── CookieCats_Analysis.pbix         # Power BI report
├── requirements.txt                 # Python dependencies
└── README.md
```

## SQL analysis

The SQL files in [`sql/`](sql/) calculate:

- Retention by experiment version
- Median game rounds by version
- Day-7 retention gaps by activity segment

## Power BI report

To build the Power BI report:

1. Open Power BI Desktop.
2. Choose **Get data > Text/CSV**.
3. Import [`dashboard/cookie_cats_powerbi.csv`](dashboard/cookie_cats_powerbi.csv).
4. Add measures from [`powerbi/CookieCats_Measures.dax`](powerbi/CookieCats_Measures.dax).
5. Use the Power Query transformation in
   [`powerbi/CookieCats_PowerQuery.pq`](powerbi/CookieCats_PowerQuery.pq) when
   repeatable cleaning is required.
6. Sort `Segment` by `SegmentOrder`.
7. Add cards for players, D1 retention, D7 retention, and median rounds.
8. Add retention and segment comparison charts.

## Data preparation and quality

The source contains 90,189 player rows. One extreme observation has at least
40,000 game rounds. The analysis excludes values at or above 40,000 when
calculating engagement metrics and preserves the original source file.

Players are grouped into these activity segments:

```text
0 rounds, 1-10, 11-50, 51-200, 200+
```

The pipeline checks for duplicate user IDs, missing values, invalid experiment
versions, invalid retention values, negative round counts, and extreme
outliers. The generated quality report is available at
[`reports/data_quality_report.json`](reports/data_quality_report.json).

## Limitations

This dataset contains retention through day 7 and game-round activity, but it
does not include revenue, acquisition source, device, country, or longer-term
retention. The findings are therefore useful for the experiment analysis but
are not a complete product or revenue decision on their own.


## Live dashboard

[Open the Cookie Cats A/B Test dashboard](https://julfikar-asif-cookie-cat-project-dashboard-app-dbr0i3.streamlit.app/)