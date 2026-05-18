/* ============================================================================
   RULE 2 — SLOW MOVER + STORE ISSUE
   See CONTEXT_FOR_CLAUDE.md §9.1.

   Detects slow-moving products and identifies products with strong online
   demand but weak in-store performance.

   Date window: rolling 28 days from MAX(day_date) — NEVER CURRENT_DATE.
   Location 47 = online benchmark; location 23 = warehouse, excluded.
   STR capped at 100% via LEAST(1, …); online_str kept NULL when no online
   data (do NOT coalesce to 0).
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
    group by s.product_id, s.location_id
),

stock_4w as (
    select
        st.product_id,
        st.location_id,
        avg(st.available_stock) as avg_stock_4w
    from stg__stock as st, sales_anchor as a
    where st.day_date >= a.anchor - interval 28 day
    group by st.product_id, st.location_id
),

online as (
    select
        s.product_id,
        s.sales_4w as online_sales,
        st.avg_stock_4w as online_stock,
        least(1, s.sales_4w / nullif(st.avg_stock_4w, 0)) as online_str
    from sales_4w as s
    inner join stock_4w as st
        on s.product_id = st.product_id and s.location_id = st.location_id
    where s.location_id = 47
      and st.avg_stock_4w > 0
),

store as (
    select
        s.product_id,
        s.location_id,
        s.sales_4w as store_sales,
        st.avg_stock_4w as store_stock,
        least(1, s.sales_4w / nullif(st.avg_stock_4w, 0)) as store_str
    from sales_4w as s
    inner join stock_4w as st
        on s.product_id = st.product_id and s.location_id = st.location_id
    where s.location_id not in (47, 23)
      and st.avg_stock_4w > 0
),

joined as (
    select
        st.product_id,
        st.location_id,
        p.product_name,
        p.product_category,
        p.product_brand,
        l.location_name,
        l.branch_area,
        l.store_type,
        st.store_sales,
        st.store_stock,
        st.store_str,
        coalesce(o.online_sales, 0) as online_sales,
        coalesce(o.online_stock, 0) as online_stock,
        o.online_str  -- NULL = no online presence; intentional
    from store as st
    left join online as o on st.product_id = o.product_id
    left join stg__products as p on st.product_id = p.product_id
    left join stg__locations as l on st.location_id = l.location_id
)

select
    *,
    case
        when store_sales = 0
            then 'DEAD_STOCK'
        when online_str >= 0.10 and store_str < 0.10
            then 'STORE_ISSUE'
        when (online_str is null or online_str < 0.10) and store_str < 0.10
            then 'SLOW_MOVER'
        when store_str >= 0.30
            then 'FAST_MOVER'
        else 'MEDIUM_MOVEMENT'
    end as insight_type,

    case
        when store_sales = 0
            then 'Clear stock immediately; apply heavy discount; remove from store'
        when online_str >= 0.10 and store_str < 0.10
            then 'Increase stock; improve visibility; expand to more stores'
        when (online_str is null or online_str < 0.10) and store_str < 0.10
            then 'Reduce stock; apply markdown; consider discontinuation'
        when store_str >= 0.30
            then 'Maintain or increase stock allocation'
        else 'Monitor performance; optimize stock'
    end as recommended_action

from joined
where store_stock >= 1
