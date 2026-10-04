-- Insurance Claims SQL Analysis
-- Database: SQLite (insurance.db, table: claims)
-- Note: These queries use standard SQL (GROUP BY, aggregations, CASE WHEN).
-- They will also run on SQL Server with minor changes:
--   * In SQL Server, string literals and column names work the same way here.
--   * If you recreate the table in SQL Server, use CREATE TABLE / BULK INSERT
--     instead of the Python/SQLite loading step. The SELECT queries below
--     themselves need no change, except optionally adding schema (dbo.claims).
--
-- Table: claims
--   age       INTEGER  policyholder age
--   sex       TEXT     female / male
--   bmi       REAL     body mass index
--   children  INTEGER  number of children / dependants covered
--   smoker    TEXT     yes / no
--   region    TEXT     southwest / southeast / northwest / northeast
--   charges   REAL     claim amount in USD (treated as the claim cost)

-- ---------------------------------------------------------------------
-- Q1: Total and average claims by region
-- Business question: Which regions generate the highest claim costs,
-- both in total dollars and per policyholder?
-- ---------------------------------------------------------------------
SELECT
    region,
    COUNT(*)                AS policyholders,
    ROUND(SUM(charges), 2)  AS total_charges,
    ROUND(AVG(charges), 2)  AS avg_charge,
    ROUND(MIN(charges), 2)  AS min_charge,
    ROUND(MAX(charges), 2)  AS max_charge
FROM claims
GROUP BY region
ORDER BY avg_charge DESC;

-- ---------------------------------------------------------------------
-- Q2: Total and average claims by smoker status
-- Business question: How much more do smokers cost, on average,
-- compared with non-smokers?
-- ---------------------------------------------------------------------
SELECT
    smoker,
    COUNT(*)                AS policyholders,
    ROUND(SUM(charges), 2)  AS total_charges,
    ROUND(AVG(charges), 2)  AS avg_charge,
    ROUND(MIN(charges), 2)  AS min_charge,
    ROUND(MAX(charges), 2)  AS max_charge
FROM claims
GROUP BY smoker
ORDER BY avg_charge DESC;

-- ---------------------------------------------------------------------
-- Q3: Average claims by age band
-- Business question: How do claim costs change as policyholders get older?
-- Age bands are built with CASE WHEN, a common reporting technique.
-- ---------------------------------------------------------------------
SELECT
    CASE
        WHEN age < 30 THEN '18-29'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        ELSE '50+'
    END                     AS age_band,
    COUNT(*)                AS policyholders,
    ROUND(SUM(charges), 2)  AS total_charges,
    ROUND(AVG(charges), 2)  AS avg_charge
FROM claims
GROUP BY age_band
ORDER BY
    CASE age_band
        WHEN '18-29' THEN 1
        WHEN '30-39' THEN 2
        WHEN '40-49' THEN 3
        ELSE 4
    END;

-- ---------------------------------------------------------------------
-- Q4: Average claims by number of children
-- Business question: Do policyholders with more children have
-- higher or lower average claim amounts?
-- ---------------------------------------------------------------------
SELECT
    children,
    COUNT(*)                AS policyholders,
    ROUND(SUM(charges), 2)  AS total_charges,
    ROUND(AVG(charges), 2)  AS avg_charge
FROM claims
GROUP BY children
ORDER BY children;

-- ---------------------------------------------------------------------
-- Q5: Top claim segments (region x smoker status)
-- Business question: Which combined segments are the most expensive
-- per policyholder? This is the kind of segment table used to
-- prioritise pricing, prevention, and wellness programmes.
-- Segments with very few people are excluded (HAVING) so the
-- averages are not driven by one or two records.
-- ---------------------------------------------------------------------
SELECT
    region,
    smoker,
    COUNT(*)                AS policyholders,
    ROUND(SUM(charges), 2)  AS total_charges,
    ROUND(AVG(charges), 2)  AS avg_charge
FROM claims
GROUP BY region, smoker
HAVING COUNT(*) >= 20
ORDER BY avg_charge DESC;

-- ---------------------------------------------------------------------
-- Q6: Smoker vs non-smoker cost ratio, per region
-- Business question: In each region, how many times higher is the
-- average smoker claim than the average non-smoker claim?
-- Conditional aggregation (AVG with CASE WHEN inside) puts smokers
-- and non-smokers side by side in one row per region.
-- ---------------------------------------------------------------------
SELECT
    region,
    COUNT(*)                                                        AS policyholders,
    SUM(CASE WHEN smoker = 'yes' THEN 1 ELSE 0 END)                 AS smokers,
    SUM(CASE WHEN smoker = 'no'  THEN 1 ELSE 0 END)                 AS non_smokers,
    ROUND(AVG(CASE WHEN smoker = 'yes' THEN charges END), 2)        AS avg_smoker_charge,
    ROUND(AVG(CASE WHEN smoker = 'no'  THEN charges END), 2)        AS avg_non_smoker_charge,
    ROUND(
        AVG(CASE WHEN smoker = 'yes' THEN charges END)
        / AVG(CASE WHEN smoker = 'no' THEN charges END)
    , 2)                                                            AS smoker_cost_ratio
FROM claims
GROUP BY region
ORDER BY smoker_cost_ratio DESC;
