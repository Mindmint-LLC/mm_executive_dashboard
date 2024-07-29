    with max_eom as (
    select max(eom) as eom
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly`
    ),
    trial_n_active as (
    select m.product_eom
    , m.is_trial
    , count(*) as units
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly` m
    join max_eom me
        on m.eom = me.eom
    where m.is_cancelled = 0
    group by all
    )
    select * from trial_n_active
    union all 
    select 
      product_eom,2 as is_trial, sum(units) as units 
    from trial_n_active
    group by all