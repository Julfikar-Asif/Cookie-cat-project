WITH seg AS (
  SELECT version, retention_7,
         CASE WHEN sum_gamerounds = 0   THEN '0'
              WHEN sum_gamerounds <= 10  THEN '1-10'
              WHEN sum_gamerounds <= 50  THEN '11-50'
              WHEN sum_gamerounds <= 200 THEN '51-200'
              ELSE '200+' END AS segment,
         CASE WHEN sum_gamerounds = 0   THEN 1
              WHEN sum_gamerounds <= 10  THEN 2
              WHEN sum_gamerounds <= 50  THEN 3
              WHEN sum_gamerounds <= 200 THEN 4
              ELSE 5 END AS seg_order
  FROM players
  WHERE sum_gamerounds < 40000
)
SELECT segment,
       COUNT(*) AS players,
       ROUND(100.0 * AVG(CASE WHEN version = 'gate_30' THEN retention_7 END), 2) AS gate_30,
       ROUND(100.0 * AVG(CASE WHEN version = 'gate_40' THEN retention_7 END), 2) AS gate_40,
       ROUND(100.0 * (AVG(CASE WHEN version = 'gate_30' THEN retention_7 END)
                    - AVG(CASE WHEN version = 'gate_40' THEN retention_7 END)), 2) AS gap_pp
FROM seg
GROUP BY segment, seg_order
ORDER BY seg_order;