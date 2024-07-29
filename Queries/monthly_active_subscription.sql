    with max_eom as (
    select  eom
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly`
    GROUP BY eom
    )

    select 
       FORMAT_TIMESTAMP('%b-%Y', me.eom)  AS Month
    , me.eom
    , count(case when m.product_eom = '47 membership' then  1 end) as `47 membership`
    , count(case when m.product_eom = '423 membership' then  1 end) as `423 membership`
    , count(case when m.product_eom = '997 membership' then  1 end) as `997 membership`
    , count(case when m.product_eom = '97 membership' then  1 end) as `97 membership`

    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly` m
    join max_eom me
        on m.eom = me.eom
    where m.is_cancelled = 0
    and is_trial = 0
    AND me.eom BETWEEN DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 23 MONTH) 
      AND DATE_SUB(DATE_TRUNC(DATE_ADD(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH), INTERVAL 1 DAY)
      AND DATE(me.eom) >= '2023-01-31'
    group by all
    order by me.eom