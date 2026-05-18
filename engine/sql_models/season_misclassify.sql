/* ============================================================================
   RULE 3 — SEASONAL MISCLASSIFICATION
   See CONTEXT_FOR_CLAUDE.md §9.3.

   Detects seasonal products (SS / AW) selling outside their designated
   season in the ONLINE channel — the unconstrained-demand signal.

   Date window: rolling 365 days from MAX(day_date).
   Filter: location_id = 47 (online only), product_season ∈ {SS, AW}.
   ============================================================================ */

with sales_anchor as (
    select max(day_date) as anchor from stg__sales
),

filtered as (
    select
        s.product_id,
        s.day_date,
        s.sales_units,
        upper(p.product_season) as product_season,
        case
            when month(s.day_date) between 3 and 8 then 'SS'
            else 'AW'
        end as expected_season
    from stg__sales as s
    inner join stg__products as p on s.product_id = p.product_id
    cross join sales_anchor as a
    where s.sales_units > 0
      and s.location_id = 47
      and s.day_date >= a.anchor - interval 365 day
      and upper(p.product_season) in ('SS', 'AW')
),

season_split as (
    select
        f.product_id,
        any_value(p.product_name) as product_name,
        any_value(p.product_category) as product_category,
        any_value(p.product_brand) as product_brand,
        any_value(f.product_season) as product_season,
        sum(case when f.product_season = f.expected_season then f.sales_units else 0 end) as in_season_units,
        sum(case when f.product_season <> f.expected_season then f.sales_units else 0 end) as out_season_units
    from filtered as f
    inner join stg__products as p on f.product_id = p.product_id
    group by f.product_id
),

bounded as (
    select
        *,
        in_season_units * 0.5 as lower_bound,
        in_season_units * 1.5 as upper_bound
    from season_split
    where (in_season_units + out_season_units) >= 10
)

select
    product_id,
    product_name,
    product_category,
    product_brand,
    product_season,
    in_season_units,
    out_season_units,
    round(lower_bound, 2) as lower_bound,
    round(upper_bound, 2) as upper_bound,

    case
        when in_season_units = 0 and out_season_units > 0
            then 'SEASON_MISMATCH'
        when out_season_units > upper_bound
            then 'SEASON_MISMATCH'
        when out_season_units between lower_bound and upper_bound
            then 'MID_MISMATCH'
        when out_season_units < lower_bound
            then 'SEASONAL_OK'
        else 'NO_SIGNAL'
    end as insight_type,

    case
        when in_season_units = 0 and out_season_units > 0
            then 'Reclassify to other season; no in-season sales'
        when out_season_units > upper_bound
            then 'More than twice as many sales out of season; reclassification needed'
        when out_season_units between lower_bound and upper_bound
            then 'More sales out of season than in; reclassification needed'
        when out_season_units < lower_bound
            then 'Within 50% of in-season sales; consider for continuity'
        else 'No action'
    end as recommended_action

from bounded
where out_season_units > 0
