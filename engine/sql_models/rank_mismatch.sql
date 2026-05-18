/* ============================================================================
   RULE 1 — ONLINE / IN-STORE RANK MISMATCH
   See CONTEXT_FOR_CLAUDE.md §9.2.

   Rank products by online sales (globally) and by store sales (per store).
   Flag large rank gaps as RANGE_GAP candidates.

   No date filter — rank is relative to lifetime performance.
   Location 47 = online benchmark; location 23 = warehouse, excluded.
   ============================================================================ */

with filtered as (
    select
product_id,
location_id,
sales_value
    from stg__sales
    where sales_units > 0
),

online as (
    select
        product_id,
        sum(sales_value) as online_value
    from filtered
    where location_id = 47
    group by product_id
),

store as (
    select
        product_id,
        location_id,
        sum(sales_value) as store_value
    from filtered
    where location_id not in (47, 23)
    group by product_id, location_id
),

online_ranked as (
    select
        product_id,
        online_value,
        rank() over (order by online_value desc) as online_rank,
        count(*) over () as total_online_products
    from online
),

store_ranked as (
    select
        product_id,
        location_id,
        store_value,
        rank() over (partition by location_id order by store_value desc) as store_rank,
        count(*) over (partition by location_id) as total_store_products
    from store
),

joined as (
    select
        sr.product_id,
        sr.location_id,
        l.location_name,
        l.branch_area,
        l.store_type,
        cast(null as varchar) as country,
        p.product_name,
        p.product_category,
        p.product_brand,
        coalesce(orc.online_value, 0) as online_value,
        sr.store_value,
        orc.online_rank,
        orc.total_online_products,
        sr.store_rank,
        sr.total_store_products,
        case when orc.online_rank is null
             then 'No online sales'
             else concat(orc.online_rank, ' / ', orc.total_online_products)
        end as online_rank_label,
        concat(sr.store_rank, ' / ', sr.total_store_products) as store_rank_label,
        case when orc.online_rank is null
             then null
             else cast(orc.online_rank as double) / nullif(orc.total_online_products, 0)
        end as online_percentile,
        cast(sr.store_rank as double) / nullif(sr.total_store_products, 0) as store_percentile
    from store_ranked as sr
    left join online_ranked as orc on sr.product_id = orc.product_id
    left join stg__products as p on sr.product_id = p.product_id
    left join stg__locations as l on sr.location_id = l.location_id
)

select
    *,
    coalesce(store_percentile - online_percentile, 0) as percentile_gap,
    case
        when online_rank is null
            then 'NO_ONLINE_SIGNAL'
        when online_percentile <= 0.20 and store_percentile >= 0.50
            then 'RANGE_GAP'
        when online_percentile <= 0.30 and store_percentile >= 0.50
            then 'MEDIUM_RANGE_GAP'
        when online_percentile <= 0.40 and store_percentile >= 0.50
            then 'LOW_RANGE_GAP'
        else 'BALANCED'
    end as insight_type,

    case
        when online_rank is null
            then 'Fix online listing before scaling stores; pilot in thin store set'
        when online_percentile <= 0.20 and store_percentile >= 0.50
            then 'Step-change store depth; reset shelf and window planogram'
        when online_percentile <= 0.30 and store_percentile >= 0.50
            then 'Increase store allocation and facings; widen size curve'
        when online_percentile <= 0.40 and store_percentile >= 0.50
            then 'Nudge min display depth; test end-cap or cross-sell bundle'
        else 'Maintain current strategy; balanced online-store profile'
    end as recommended_action,

    round(online_percentile * 100, 2) as online_percentile_display,
    round(store_percentile * 100, 2) as store_percentile_display

from joined
