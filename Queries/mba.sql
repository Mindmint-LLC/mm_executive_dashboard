with mba_summary as

(

  SELECT  sum(num_sales) as Sales
  , - (sum(num_cancel)  + sum(num_paused)) as Cancels
  , sum(num_sales) - sum(num_cancel) - sum(num_paused)   as active
  --  , sum(num_requests) as requests
  -- , sum(num_paused) as paused
  --  , sum(num_saved) as saved
  --  , sum(num_active) + sum(num_paused) as enrolled
  , ROUND(SUM(CASE WHEN pay_type = 'PIF' THEN num_sales ELSE 0 END) / SUM(num_sales),2) AS pif_sales_ratio
  , LAST_DAY(DATE(date_closed)) as date_closed
  , FORMAT_TIMESTAMP('%b-%Y', LAST_DAY(DATE(date_closed))) as Month
  FROM `bbg-platform.dbt_tscrivo.fct_hs_deal_N`
  WHERE (name_product_plantype LIKE '%Mastermind Business Academy%' OR name_product_plantype LIKE '%The Action Academy%')
  and name_product_plantype NOT LIKE "%In-Person%"
  and date_closed is not null
  AND date(date_closed) BETWEEN DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 23 MONTH) 
  AND DATE_SUB(DATE_TRUNC(DATE_ADD(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH), INTERVAL 1 DAY)
  AND DATE(date_closed) >= '2023-01-31'
  GROUP BY ALL
  ORDER BY LAST_DAY(DATE(date_closed))
)
select *, sum(active) over y as `Total Active`,round(abs(cancels/sales),2) AS `Drop Rate`  from mba_summary

window y as (order by date_closed asc rows between unbounded preceding and current row)
order by date_closed
