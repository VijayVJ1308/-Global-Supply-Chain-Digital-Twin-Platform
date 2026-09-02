-- ====================================================================
-- Global Supply Chain Digital Twin Platform
-- Production Analytical SQL Queries & Gold Layer Reporting Views
-- Database: PostgreSQL / Redshift / Medallion Lakehouse
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Executive Summary View: Core Supply Chain Operational KPIs
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_executive_kpi_summary AS
WITH order_stats AS (
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        COALESCE(SUM(total_amount_usd), 0) AS total_revenue_usd,
        COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) AS delivered_orders,
        COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) AS cancelled_orders
    FROM gold.fact_orders
),
shipment_stats AS (
    SELECT 
        COUNT(DISTINCT shipment_id) AS total_shipments,
        COUNT(CASE WHEN is_delayed = TRUE OR shipment_status = 'DELAYED' THEN 1 END) AS delayed_shipments,
        COUNT(CASE WHEN shipment_status = 'DELIVERED' AND is_delayed = FALSE THEN 1 END) AS on_time_shipments,
        COALESCE(AVG(delay_hours), 0) AS avg_delay_hours,
        COALESCE(SUM(temp_breach_count), 0) AS total_temp_breaches
    FROM gold.fact_shipments
),
inventory_stats AS (
    SELECT 
        COUNT(DISTINCT inventory_id) AS total_monitored_skus,
        COUNT(CASE WHEN is_low_stock = TRUE OR quantity_on_hand <= safety_stock THEN 1 END) AS stockout_risk_items,
        COALESCE(SUM(inventory_value_usd), 0) AS total_inventory_value_usd
    FROM gold.fact_inventory
)
SELECT 
    o.total_orders,
    o.total_revenue_usd,
    ROUND((o.delivered_orders::NUMERIC / NULLIF(o.total_orders, 0)) * 100.0, 2) AS order_fulfillment_rate_pct,
    s.total_shipments,
    s.delayed_shipments,
    ROUND((s.delayed_shipments::NUMERIC / NULLIF(s.total_shipments, 0)) * 100.0, 2) AS shipment_delay_rate_pct,
    ROUND((s.on_time_shipments::NUMERIC / NULLIF(s.total_shipments, 0)) * 100.0, 2) AS on_time_delivery_rate_pct,
    ROUND(s.avg_delay_hours, 1) AS avg_shipment_delay_hours,
    s.total_temp_breaches,
    i.total_monitored_skus,
    i.stockout_risk_items,
    i.total_inventory_value_usd,
    CURRENT_TIMESTAMP AS last_refreshed_at
FROM order_stats o
CROSS JOIN shipment_stats s
CROSS JOIN inventory_stats i;

-- --------------------------------------------------------------------
-- 2. Supplier Reliability Scorecard View (OTIF & Rating Analytics)
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_supplier_scorecard AS
SELECT 
    sup.supplier_id,
    sup.supplier_name,
    sup.country AS supplier_country,
    sup.tier AS supplier_tier,
    sup.rating AS supplier_base_rating,
    COUNT(DISTINCT fo.order_id) AS total_orders_fulfilled,
    COALESCE(SUM(fo.total_amount_usd), 0) AS total_procurement_spend_usd,
    COUNT(CASE WHEN fo.order_status = 'DELIVERED' THEN 1 END) AS delivered_orders,
    ROUND(
        (COUNT(CASE WHEN fo.order_status = 'DELIVERED' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT fo.order_id), 0)) * 100.0, 2
    ) AS supplier_otif_pct,
    CASE 
        WHEN sup.rating >= 4.5 THEN 'Tier 1 Preferred'
        WHEN sup.rating >= 3.8 THEN 'Standard Vendor'
        ELSE 'Under Watch / Risk'
    END AS vendor_risk_category
FROM gold.dim_supplier sup
LEFT JOIN gold.fact_orders fo ON sup.supplier_key = fo.supplier_key
GROUP BY sup.supplier_id, sup.supplier_name, sup.country, sup.tier, sup.rating;

-- --------------------------------------------------------------------
-- 3. Logistics & Carrier Performance View
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_carrier_performance AS
SELECT 
    fs.carrier,
    fs.transit_mode,
    COUNT(fs.shipment_fact_key) AS total_shipments_handled,
    COUNT(CASE WHEN fs.is_delayed = TRUE THEN 1 END) AS total_delayed_shipments,
    ROUND(COALESCE(AVG(fs.delay_hours), 0), 1) AS avg_delay_hours,
    ROUND(
        ((COUNT(fs.shipment_fact_key) - COUNT(CASE WHEN fs.is_delayed = TRUE THEN 1 END))::NUMERIC / 
        NULLIF(COUNT(fs.shipment_fact_key), 0)) * 100.0, 2
    ) AS carrier_on_time_pct,
    COALESCE(SUM(fs.temp_breach_count), 0) AS total_cold_chain_breaches
FROM gold.fact_shipments fs
GROUP BY fs.carrier, fs.transit_mode;

-- --------------------------------------------------------------------
-- 4. Warehouse Stockout Risk & Inventory Reorder Alerts View
-- --------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_inventory_stockout_risk AS
SELECT 
    dw.warehouse_code,
    dw.warehouse_name,
    dw.city AS warehouse_city,
    dp.sku,
    dp.product_name,
    dp.category AS product_category,
    fi.quantity_on_hand,
    fi.safety_stock,
    fi.reorder_level,
    fi.inventory_value_usd,
    CASE 
        WHEN fi.quantity_on_hand <= (fi.safety_stock * 0.5) THEN 'CRITICAL STOCKOUT'
        WHEN fi.quantity_on_hand <= fi.safety_stock THEN 'HIGH RISK'
        WHEN fi.quantity_on_hand <= fi.reorder_level THEN 'REORDER REQUIRED'
        ELSE 'HEALTHY'
    END AS stock_status
FROM gold.fact_inventory fi
JOIN gold.dim_warehouse dw ON fi.warehouse_key = dw.warehouse_key
JOIN gold.dim_product dp ON fi.product_key = dp.product_key
WHERE fi.is_low_stock = TRUE OR fi.quantity_on_hand <= fi.reorder_level;

-- --------------------------------------------------------------------
-- 5. Analytical Query: Monthly Revenue Trends & Month-over-Month Growth
-- --------------------------------------------------------------------
-- Usage: Execute directly for financial & order performance dashboards
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(DISTINCT fo.order_id) AS monthly_order_count,
    SUM(fo.total_amount_usd) AS monthly_revenue_usd,
    AVG(fo.total_amount_usd) AS avg_order_value_usd,
    LAG(SUM(fo.total_amount_usd)) OVER (ORDER BY dd.year, dd.month) AS prev_month_revenue_usd,
    ROUND(
        ((SUM(fo.total_amount_usd) - LAG(SUM(fo.total_amount_usd)) OVER (ORDER BY dd.year, dd.month)) / 
        NULLIF(LAG(SUM(fo.total_amount_usd)) OVER (ORDER BY dd.year, dd.month), 0)) * 100.0, 2
    ) AS mom_revenue_growth_pct
FROM gold.fact_orders fo
JOIN gold.dim_date dd ON fo.order_date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year DESC, dd.month DESC;

-- --------------------------------------------------------------------
-- 6. Analytical Query: Top Performing Products & Revenue Rank
-- --------------------------------------------------------------------
SELECT 
    dp.sku,
    dp.product_name,
    dp.category,
    SUM(fo.quantity) AS total_units_sold,
    SUM(fo.total_amount_usd) AS gross_revenue_usd,
    DENSE_RANK() OVER (PARTITION BY dp.category ORDER BY SUM(fo.total_amount_usd) DESC) AS category_revenue_rank
FROM gold.fact_orders fo
JOIN gold.dim_product dp ON fo.product_key = dp.product_key
GROUP BY dp.sku, dp.product_name, dp.category
ORDER BY gross_revenue_usd DESC;
