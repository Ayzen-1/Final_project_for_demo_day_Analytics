CREATE VIEW v_qual AS (
SELECT 
	oi.price,  
	or2.review_score 
FROM order_items oi
INNER JOIN order_reviews or2 ON oi.order_id = or2.order_id
);

CREATE VIEW v_qual_cat AS (
SELECT 
	p.product_category_name,
    COUNT(or2.review_score) AS review_count,
    ROUND(AVG(or2.review_score), 2) AS average_review_score
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
INNER JOIN order_reviews or2 ON oi.order_id = or2.order_id
GROUP BY p.product_category_name
);

CREATE VIEW v_top_sel AS (
SELECT
    seller_id,
    COUNT(seller_id) AS orders,
    monthkey,
    region,
    seller_state,
    MIN(timestamp) AS timestamp
FROM (
    SELECT
        s.seller_id,
        o.timestamp,
        strftime('%Y%m', o.timestamp) AS monthkey,
        s.seller_state,
        CASE
            WHEN s.seller_state IN ('AM', 'PA', 'RO') THEN 'North'
            WHEN s.seller_state IN ('BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'North-East'
            WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Weste'
            WHEN s.seller_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'South-East'
            WHEN s.seller_state IN ('PR', 'RS', 'SC') THEN 'South'
            ELSE 'Outro'
        END AS region,
        COUNT(oi.order_id) AS order_count
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN sellers s ON oi.seller_id = s.seller_id
    GROUP BY
        s.seller_id,
        o.timestamp,
        strftime('%Y%m', o.timestamp),
        s.seller_state,
        CASE
            WHEN s.seller_state IN ('AM', 'PA', 'RO') THEN 'North'
            WHEN s.seller_state IN ('BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'North-East'
            WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Weste'
            WHEN s.seller_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'South-East'
            WHEN s.seller_state IN ('PR', 'RS', 'SC') THEN 'South'
            ELSE 'Outro'
        END
) AS subquery
GROUP BY
    seller_id,
    monthkey,
    region,
    seller_state
ORDER BY orders DESC;
)
;

CREATE VIEW v_top_state(
select
    seller_state
    , monthkey
    , count(seller_id)
from (
	SELECT
    s.seller_id,
    o.timestamp,
    strftime('%Y%m', o.timestamp) AS monthkey,
    s.seller_state,
    CASE
        WHEN s.seller_state IN ('AM', 'PA', 'RO') THEN 'North'
        WHEN s.seller_state IN ('BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'North-East'
        WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Weste'
        WHEN s.seller_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'South-East'
        WHEN s.seller_state IN ('PR', 'RS', 'SC') THEN 'South'
        ELSE 'Outro'
    END AS region,
    count(oi.order_id) 
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY
    s.seller_id,
    o.timestamp,
    monthkey,
    s.seller_state,
    CASE
        WHEN s.seller_state IN ('AM', 'PA', 'RO') THEN 'North'
        WHEN s.seller_state IN ('BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'North-East'
        WHEN s.seller_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Weste'
        WHEN s.seller_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'South-East'
        WHEN s.seller_state IN ('PR', 'RS', 'SC') THEN 'South'
        ELSE 'Outro'
    END
)
group by seller_state, monthkey
)
;
CREATE VIEW v_top_product(

SELECT
    s.seller_id,
    COUNT(oi.order_id) AS orders,
    strftime('%Y%m', o.timestamp) AS monthkey,
    p.product_id,
    COUNT(oi.product_id) AS total_sold,
    SUM(oi.price) AS total_revenue
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN sellers s ON oi.seller_id = s.seller_id
INNER JOIN products p ON oi.product_id = p.product_id
GROUP BY
    s.seller_id,
    monthkey,
    p.product_id
ORDER BY total_revenue DESC
);