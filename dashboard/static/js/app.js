document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initMap();
    fetchKPIs();
    fetchInventory();
    fetchQualityData();

    document.getElementById("btn-run-etl").addEventListener("click", triggerETL);
    document.getElementById("btn-retest-quality").addEventListener("click", fetchQualityData);
});

let map, warehouseGroup, shipmentGroup, iotGroup;

function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");

            if (target === "tab-map" && map) {
                setTimeout(() => map.invalidateSize(), 200);
            }
        });
    });
}

function initMap() {
    map = L.map('map').setView([20.0, 0.0], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
    }).addTo(map);

    warehouseGroup = L.layerGroup().addTo(map);
    shipmentGroup = L.layerGroup().addTo(map);
    iotGroup = L.layerGroup().addTo(map);

    fetchNodes();
}

async function fetchKPIs() {
    try {
        const res = await fetch("/api/kpis");
        const data = await res.json();

        document.getElementById("kpi-orders").innerText = data.total_orders.toLocaleString();
        document.getElementById("kpi-revenue").innerText = `$${(data.total_revenue_usd / 1e6).toFixed(2)}M Revenue`;
        document.getElementById("kpi-shipments").innerText = data.active_transit_shipments.toLocaleString();
        document.getElementById("kpi-delays").innerText = data.delayed_shipments.toLocaleString();
        document.getElementById("kpi-breaches").innerText = data.temp_breaches.toLocaleString();
        document.getElementById("kpi-low-stock").innerText = data.low_stock_items.toLocaleString();
    } catch (e) {
        console.error("Error fetching KPIs:", e);
    }
}

async function fetchNodes() {
    try {
        const res = await fetch("/api/nodes");
        const data = await res.json();

        warehouseGroup.clearLayers();
        shipmentGroup.clearLayers();
        iotGroup.clearLayers();

        const sidebarFeed = document.getElementById("telemetry-feed");
        sidebarFeed.innerHTML = "";

        // 1. Plot Warehouses
        data.warehouses.forEach(wh => {
            if (wh.latitude && wh.longitude) {
                const marker = L.circleMarker([wh.latitude, wh.longitude], {
                    radius: 8,
                    fillColor: "#38bdf8",
                    color: "#0284c7",
                    weight: 2,
                    fillOpacity: 0.8
                });
                marker.bindPopup(`
                    <div style="color: #0f172a;">
                        <strong>🏢 ${wh.name} (${wh.code})</strong><br>
                        Location: ${wh.city}, ${wh.country}<br>
                        Zone: <strong>${wh.temp_zone_type}</strong><br>
                        Capacity: ${wh.capacity_sqft.toLocaleString()} sqft
                    </div>
                `);
                warehouseGroup.addLayer(marker);
            }
        });

        // 2. Plot Active Shipments & Telemetry
        data.iot_telemetry.forEach(iot => {
            if (iot.latitude && iot.longitude) {
                const isBreach = parseFloat(iot.temperature_c) > 8.0;
                const color = isBreach ? "#ef4444" : "#10b981";

                const marker = L.circleMarker([iot.latitude, iot.longitude], {
                    radius: isBreach ? 7 : 4,
                    fillColor: color,
                    color: isBreach ? "#ffffff" : color,
                    weight: isBreach ? 2 : 1,
                    fillOpacity: 0.9
                });

                marker.bindPopup(`
                    <div style="color: #0f172a;">
                        <strong>📡 Device ${iot.device_id}</strong><br>
                        Shipment: ${iot.shipment_id}<br>
                        Temperature: <strong style="color: ${isBreach ? '#ef4444' : '#10b981'};">${iot.temperature_c}°C</strong><br>
                        Humidity: ${iot.humidity_pct}%
                    </div>
                `);
                iotGroup.addLayer(marker);

                // Add to sidebar telemetry feed
                const feedItem = document.createElement("div");
                feedItem.className = `telemetry-item ${isBreach ? 'breach' : ''}`;
                feedItem.innerHTML = `
                    <div style="display: flex; justify-content: space-between;">
                        <strong>${iot.shipment_id} (${iot.device_id})</strong>
                        <span class="badge ${isBreach ? 'badge-fail' : 'badge-pass'}">${iot.temperature_c}°C</span>
                    </div>
                    <div class="time">Recorded at: ${new Date(iot.recorded_at).toLocaleTimeString()}</div>
                `;
                sidebarFeed.appendChild(feedItem);
            }
        });

    } catch (e) {
        console.error("Error fetching map nodes:", e);
    }
}

async function fetchInventory() {
    try {
        const res = await fetch("/api/inventory");
        const data = await res.json();

        const tbody = document.getElementById("inventory-tbody");
        tbody.innerHTML = "";

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center">No inventory records found</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            const isLow = item.is_low_stock;
            tr.innerHTML = `
                <td><strong>${item.warehouse_name}</strong></td>
                <td>${item.product_name}</td>
                <td><span class="badge badge-info">${item.category}</span></td>
                <td><strong>${item.quantity_on_hand}</strong></td>
                <td>${item.reorder_level}</td>
                <td>
                    <span class="badge ${isLow ? 'badge-fail' : 'badge-pass'}">
                        ${isLow ? '⚠️ REORDER NEEDED' : 'HEALTHY'}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error fetching inventory:", e);
    }
}

async function fetchQualityData() {
    try {
        const res = await fetch("/api/quality");
        const data = await res.json();

        const summary = data.summary || {};
        document.getElementById("quality-score").innerText = `${summary.score_pct || 100}%`;
        document.getElementById("quality-total").innerText = summary.total_tests || 0;
        document.getElementById("quality-passed").innerText = summary.passed || 0;
        document.getElementById("quality-failed").innerText = summary.failed || 0;

        const tbody = document.getElementById("quality-tbody");
        tbody.innerHTML = "";

        (data.test_details || []).forEach(test => {
            const tr = document.createElement("tr");
            const isPass = test.status === "PASSED";
            tr.innerHTML = `
                <td><span class="badge badge-info">${(test.layer || '').toUpperCase()}</span></td>
                <td><strong>${test.test_name}</strong></td>
                <td>${test.description}</td>
                <td><span class="badge ${isPass ? 'badge-pass' : 'badge-fail'}">${test.status}</span></td>
                <td>${new Date(test.executed_at).toLocaleTimeString()}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error fetching quality data:", e);
    }
}

async function triggerETL() {
    const btn = document.getElementById("btn-run-etl");
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Executing ETL...`;

    try {
        const res = await fetch("/api/actions/run_etl", { method: "POST" });
        const data = await res.json();
        alert(`ETL Complete! Quality Score: ${data.quality_score}%`);
        fetchKPIs();
        fetchNodes();
        fetchInventory();
        fetchQualityData();
    } catch (e) {
        alert("ETL execution failed: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i> Trigger Batch ETL`;
    }
}
