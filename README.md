# Insurance Claims SQL Analysis

A SQL-first analysis of insurance claim costs, built the way claims and
policy data are actually queried in an insurance company: load the data
into a relational database, group it by business segments, and aggregate.

Each row of the dataset is treated as one policyholder / claim record, and
the `charges` column is treated as the claim amount in USD.

## Business questions

1. Which regions generate the highest claim costs, in total and per policyholder?
2. How much more do smokers cost than non-smokers?
3. How do claim costs change with policyholder age?
4. Does the number of children affect average claim amounts?
5. Which combined segments (region × smoker status) are the most expensive?
6. In each region, how many times higher is the average smoker claim than
   the average non-smoker claim?

## Dataset

**Medical Cost Personal Dataset** (public, for practice):
https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv

- 1,338 policyholder records
- Columns: `age`, `sex`, `bmi`, `children`, `smoker`, `region`, `charges`

## Method

1. `claims_analysis.py` downloads the CSV and loads it into a local
   **SQLite** database (`insurance.db`, single table `claims`) — the same
   shape of workflow as querying a policy/claims table in SQL Server.
2. The six business queries live in **`queries.sql`** and are written in
   standard SQL: `GROUP BY` aggregations (`COUNT`, `SUM`, `AVG`, `MIN`,
   `MAX`), `CASE WHEN` age bands, `HAVING` segment-size filtering, and
   conditional aggregation for the smoker cost ratio. These queries run
   unchanged on **SQL Server** with only minor adjustments (table/schema
   naming); SQLite is used here only to keep the project lightweight and
   reproducible.
3. The script executes every query in `queries.sql`, saves each result
   table as CSV, and builds the charts below with matplotlib.

## Key findings (from the actual run)

- **Smoker status is by far the biggest cost driver.** Smokers (274 people)
  average **$32,050.23** per claim versus **$8,434.27** for non-smokers
  (1,064 people) — about **3.8× higher**. Smokers are only ~20% of
  policyholders but account for $8,781,763.52 of the $17,755,824.99 total.
- **The smoker gap holds in every region**, from **4.34× in the Southeast**
  ($34,845.00 vs $8,032.22) down to **3.24× in the Northeast**
  ($29,673.54 vs $9,165.53).
- **The most expensive segment is Southeast smokers** at **$34,845.00**
  average (91 policyholders). All four smoker segments ($29,673.54–
  $34,845.00) rank above every non-smoker segment ($8,019.28–$9,165.53).
- **The Southeast is the most expensive region overall** — $14,735.41
  average across 364 policyholders ($5,363,689.76 total), versus
  $12,346.94 in the cheapest region, the Southwest.
- **Costs rise steadily with age**: $9,182.49 for ages 18–29, $11,738.78
  for 30–39, $14,399.20 for 40–49, and **$17,902.55 for ages 50+** —
  roughly double the youngest band.
- **Number of children shows no clear pattern.** Averages range from
  $12,365.98 (0 children) to $15,355.32 (3 children), with the 5-children
  group lowest at $8,786.04 — but that group has only 18 policyholders,
  so the figure should not be over-interpreted.

## Outputs

Result tables (`outputs/`):

| File | Content |
|---|---|
| `q1_claims_by_region.csv` | Total/average claims by region |
| `q2_claims_by_smoker.csv` | Total/average claims by smoker status |
| `q3_claims_by_age_band.csv` | Average claims by age band (CASE WHEN) |
| `q4_claims_by_children.csv` | Average claims by number of children |
| `q5_top_claim_segments.csv` | Region × smoker segments, ranked |
| `q6_smoker_ratio_by_region.csv` | Smoker vs non-smoker ratio per region |

Charts (`outputs/`):

- `avg_claim_by_region.png` — average claim by region
- `avg_claim_smoker_vs_non_smoker.png` — smoker vs non-smoker average claim
- `avg_claim_by_region_and_smoker.png` — both effects combined, by region

## How to run

```bash
pip install -r requirements.txt
python claims_analysis.py
```

This recreates `insurance.db`, prints every query result, and writes all
CSVs and charts into `outputs/`. The SQL can also be run on its own
against `insurance.db` with any SQLite client, or adapted to SQL Server
as noted above.

## Skills demonstrated

- **SQL**: GROUP BY aggregations, CASE WHEN banding, HAVING filters,
  conditional aggregation, ordered business reporting queries
- **SQLite**: creating and querying a local relational database
- **Python / pandas**: data loading and cleaning, executing SQL from
  Python, exporting result tables
- **matplotlib**: business charts from query results
- Insurance claims/policy data analysis and segment reporting

## Files

- `claims_analysis.py` — builds the database, runs the queries, exports results
- `queries.sql` — the six commented business queries (the core of the project)
- `requirements.txt` — Python dependencies
- `insurance.db` — generated SQLite database (created by the script)
