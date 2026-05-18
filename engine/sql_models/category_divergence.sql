/* ============================================================================
   RULE 4 — CATEGORY PERFORMANCE DIVERGENCE
   See CONTEXT_FOR_CLAUDE.md §9.4.

   Compares CATEGORY-level performance between online (unconstrained demand)
   and in-store-by-region. Surfaces categories that trend strongly online
   but underperform in specific store clusters.

   Grain: category × branch_area (NOT product × location).
   Date window: rolling 28 days from MAX(day_date).
   Filter: sales_units > 0; exclude location 23.
   ============================================================================ */

with sales_anchor as (
    select max(day_date) as anchor from stg__sales
),

base as (
    select
        s.product_id,
        s.location_id,
        s.sales_value,
        p.product_category,
        l.branch_area,
        coalesce(s.location_id = 47, false) as is_online
    from stg__sales as s
    inner join stg__products as p on s.product_id = p.product_id
    inner join stg__locations as l on s.location_id = l.location_id
    cross join sales_anchor as a
    where s.sales_units > 0
      and s.location_id <> 23
      and s.day_date >= a.anchor - interval 28 day
),

online_by_cat as (
    select
        product_category,
        sum(sales_value) as online_value,
        sum(case when is_online then 1 else 0 end) as _flag
    from base
    where is_online
    group by product_category
),

online_total as (
    select sum(online_value) as total_online from online_by_cat
),

region_by_cat as (
    select
        product_category,
        branch_area,
        sum(sales_value) as region_value,
        count(*) as region_total_units
    from base
    where not is_online
    group by product_category, branch_area
),

region_totals as (
    select
        branch_area,
        sum(region_value) as total_region
    from region_by_cat
    group by branch_area
),

joined as (
    select
        rbc.product_category,
        rbc.branch_area,
        coalesce(obc.online_value, 0) as online_value,
        coalesce(obc.online_value, 0) / nullif(ot.total_online, 0) as online_share,
        rbc.region_value,
        rbc.region_value / nullif(rt.total_region, 0) as region_share,
        rbc.region_total_units
    from region_by_cat as rbc
    left join online_by_cat as obc on rbc.product_category = obc.product_category
    cross join online_total as ot
    inner join region_totals as rt on rbc.branch_area = rt.branch_area
    where rbc.region_total_units >= 10
)

select
    product_category,
    branch_area,
    round(online_value, 2) as online_value,
    round(online_share, 4) as online_share,
    round(region_value, 2) as region_value,
    round(region_share, 4) as region_share,
    region_total_units,
    round(online_share - region_share, 4) as share_gap,
    round((online_share - region_share) * 100, 2) as share_gap_display,

    case
        when (online_share - region_share) >= 0.05
            then 'CATEGORY_DIVERGENCE'
        when (online_share - region_share) >= 0.02
            then 'MEDIUM_DIVERGENCE'
        when (online_share - region_share) between -0.02 and 0.02
            then 'ALIGNED'
        else 'OVER_INDEXING'
    end as insight_type,

    case
        when (online_share - region_share) >= 0.05
            then 'Strategic range review for this category in this region; expand allocation'
        when (online_share - region_share) >= 0.02
            then 'Monitor; consider increasing facings or trial in flagship stores'
        when (online_share - region_share) between -0.02 and 0.02
            then 'No action; category is balanced online vs. in-region'
        else 'Investigate regional preference; protect existing strength'
    end as recommended_action

from joined
