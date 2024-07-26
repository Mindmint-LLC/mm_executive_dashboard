    with max_eom as (
    select max(eom) as eom
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly`
    )

    select m.product_eom
    , m.is_trial
    , count(*) as units
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly` m
    join max_eom me
        on m.eom = me.eom
    where m.is_cancelled = 0
    group by all