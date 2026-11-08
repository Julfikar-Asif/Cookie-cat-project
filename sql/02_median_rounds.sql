WITH ranked AS (
  SELECT version, sum_gamerounds,
         ROW_NUMBER() OVER (PARTITION BY version ORDER BY sum_gamerounds) AS rn,
         COUNT(*)     OVER (PARTITION BY version) AS n
  FROM players
  WHERE sum_gamerounds < 40000
)
SELECT version, AVG(sum_gamerounds) AS median_rounds
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY version;