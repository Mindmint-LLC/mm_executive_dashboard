
        with max_eom as (
        select max(eom) as eom
        from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly`
        ),

        eom_subscriptions as (
        select 
            subscription_id
            ,m.product_eom
            ,m.is_trial
        FROM `bbg-platform.analytics.fct_mastermind__subscriptions_monthly` m
        JOIN max_eom me
            ON m.eom = me.eom
        WHERE m.is_cancelled = 0
        ),
        latest_invoices AS (
        SELECT 
            subscription_id
            ,MAX(due_date)latest_due_date
        from `bbg-platform.analytics.fct_mastermind__invoices` m
        GROUP BY ALL
        )


    SELECT 
        product_eom
        ,COUNT(1) as `Total Paying - Trials and Subscribers`
        , COUNT(CASE WHEN es.is_trial = 1 THEN 1 END) `Active Trials`
        ,COUNT(CASE WHEN DATE_DIFF( li.latest_due_date,CURRENT_DATE(), DAY) <= 30 AND es.is_trial = 1 THEN 1 END) AS `Trials Ending within 30 Days`
        from eom_subscriptions es
        left join  latest_invoices li
        on es.subscription_id = li.subscription_id
    GROUP BY ALL
