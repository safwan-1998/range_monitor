/* ============================================================================
   RULE 5 — STOCK IMBALANCE
   See CONTEXT_FOR_CLAUDE.md §9.5.

   Detects locations holding disproportionate stock relative to sales velocity
   compared to peer locations carrying the same product.

   Date window: rolling 28 days from MAX(day_date).
   Filter: exclude location 23 (warehouse) and 47 (online — physical stores
   only). Final WHERE: store_stock >= 1.
   ============================================================================ */

with sales_anchor as (
    select max(day_date) as anchor from stg__sales
),

sales_4w as (
    select
        s.product_id,
        s.location_id,
        sum(s.sales_units) as sales_4w
    from stg__sales as s, sales_anchor as a
    where s.day_date >= a.anchor - interval 28 day
      and s.location_id not in (47, 23)
    group by s.product_id, s.location_id
),

stock_4w as (
    select
        st.product_id,
        st.location_id,
        avg(st.available_stock) as stock_4w
    from stg__stock as st, sales_anchor as a
    where st.day_date >= a.anchor - interval 28 day
      and st.location_id not in (47, 23)
    group by st.product_id, st.location_id
),

velocity as (
    select
        coalesce(s.product_id, st.product_id) as product_id,
        coalesce(s.location_id, st.location_id) as location_id,
        coalesce(s.sales_4w, 0) as sales_4w,
        coalesce(st.stock_4w, 0) as stock_4w,
        case
            when coalesce(s.sales_4w, 0) = 0 then null
            else coalesce(st.stock_4w, 0) / nullif(coalesce(s.sales_4w, 0) / 4.0, 0)
        end as weeks_of_cover
    from stock_4w as st
    full outer join sales_4w as s
        on st.product_id = s.product_id and st.location_id = s.location_id
),

peer_stats as (
    select
        product_id,
        median(weeks_of_cover) as peer_median_woc,
        avg(case when stock_4w > 0 then sales_4w / nullif(stock_4w, 0) end) as peer_avg_velocity,
        count(*) as peer_count
    from velocity
    where weeks_of_cover is not null
    group by product_id
),

online_4w as (
    select
        s.product_id,
        sum(s.sales_units) as online_units_4w
    from stg__sales as s, sales_anchor as a
    where s.day_date >= a.anchor - interval 28 day
      and s.location_id = 47
    group by s.product_id
)

select
    v.product_id,
    v.location_id,
    p.product_name,
    p.product_category,
    p.product_brand,
    l.location_name,
    l.branch_area,
    l.store_type,
    v.sales_4w,
    round(v.stock_4w, 2) as stock_4w,
    round(v.weeks_of_cover, 2) as weeks_of_cover,
    round(ps.peer_median_woc, 2) as peer_median_woc,
    round(ps.peer_avg_velocity, 4) as peer_avg_velocity,
    round(v.weeks_of_cover / nullif(ps.peer_median_woc, 0), 2) as wcoc_ratio,
    coalesce(o.online_units_4w, 0) as online_units_4w,

    case
        when ps.peer_median_woc is null or ps.peer_count <= 1
            then 'NO_PEER_DATA'
        when v.weeks_of_cover is null
            then 'NO_PEER_DATA'
        when v.weeks_of_cover / nullif(ps.peer_median_woc, 0) >= 2.0
            then 'STOCK_OVERSTOCK'
        when v.weeks_of_cover / nullif(ps.peer_median_woc, 0) <= 0.5 and v.sales_4w > 0
            then 'STOCK_UNDERSTOCK'
        else 'BALANCED'
    end as insight_type,

    case
        when ps.peer_median_woc is null or ps.peer_count <= 1
            then 'Single-location stocking; no peer benchmark available'
        when v.weeks_of_cover is null
            then 'Single-location stocking; no peer benchmark available'
        when v.weeks_of_cover / nullif(ps.peer_median_woc, 0) >= 2.0
            then 'Inter-store transfer to peer location with higher sell-through; consider markdown'
        when v.weeks_of_cover / nullif(ps.peer_median_woc, 0) <= 0.5 and v.sales_4w > 0
            then 'Replenish urgently; current cover is half of peer median; risk of stockout'
        else 'No action; cover is in line with peer locations'
    end as recommended_action

from velocity as v
left join peer_stats as ps on v.product_id = ps.product_id
left join online_4w as o on v.product_id = o.product_id
left join stg__products as p on v.product_id = p.product_id
left join stg__locations as l on v.location_id = l.location_id
where v.stock_4w >= 1
