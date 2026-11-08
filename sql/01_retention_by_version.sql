SELECT version,
       COUNT(*) AS players,
       ROUND(100.0 * AVG(retention_1), 2) AS d1_retention,
       ROUND(100.0 * AVG(retention_7), 2) AS d7_retention
FROM players
WHERE sum_gamerounds < 40000
GROUP BY version;