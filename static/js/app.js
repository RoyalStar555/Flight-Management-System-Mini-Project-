/**
 * AeroStructures™ Frontend Application Controller
 * Handles REST API communication and reactive rendering of:
 *   - Operations: Flight directory, bookings, waitlist, routing, undo
 *   - Live Data Structure Inspector: Stack, Queue, Linked List, Hash Table, Graph
 */

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    refreshAllData();
});

/**
 * Refreshes all data components and synchronizes with Python memory engine
 */
async function refreshAllData() {
    await Promise.all([
        loadFlights(),
        loadAirports(),
        loadManifest(),
        syncMemoryState()
    ]);
}

/* ==========================================================================
   TOAST NOTIFICATION BANNER
   ========================================================================== */
let toastTimeout = null;

function showToast(message, type = "info") {
    const banner = document.getElementById("toast-banner");
    const icon = document.getElementById("toast-icon");
    const msg = document.getElementById("toast-message");

    banner.className = `toast-banner toast-${type}`;
    msg.textContent = message;

    if (type === "error") {
        icon.textContent = "🛑";
    } else if (type === "warning") {
        icon.textContent = "⚠️";
    } else if (type === "success") {
        icon.textContent = "✅";
    } else {
        icon.textContent = "ℹ️";
    }

    banner.classList.remove("hidden");

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        dismissToast();
    }, 4500);
}

function dismissToast() {
    const banner = document.getElementById("toast-banner");
    banner.classList.add("hidden");
}

/* ==========================================================================
   FLIGHT DIRECTORY, SEARCHING & SORTING (ARRAY & ALGORITHMS)
   ========================================================================== */
async function loadFlights() {
    try {
        const res = await fetch("/api/flights");
        const data = await res.json();
        if (data.success) {
            renderFlightsTable(data.flights);
            populateFlightSelects(data.flights);
            // Hide algorithm benchmark if resetting
            document.getElementById("algo-feedback").classList.add("hidden");
        }
    } catch (err) {
        showToast("Failed to connect to backend server.", "error");
    }
}

function renderFlightsTable(flights) {
    const tbody = document.getElementById("flights-table-body");
    tbody.innerHTML = "";

    if (!flights || flights.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">No flights available.</td></tr>`;
        return;
    }

    flights.forEach(f => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><span class="flight-code">${f.flight_id}</span></td>
            <td><strong>${f.airline}</strong></td>
            <td>
                <span class="airport-badge">${f.origin}</span>
                <span style="color:var(--text-muted); margin: 0 4px;">➔</span>
                <span class="airport-badge">${f.dest}</span>
                <div style="font-size:0.7rem; color:var(--text-muted);">${f.origin_city} to ${f.dest_city}</div>
            </td>
            <td><strong>${f.departure}</strong></td>
            <td style="font-family: var(--font-mono); font-weight:700; color: #1e3a8a;">₹${f.fare.toLocaleString('en-IN')}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="quickSelectFlight('${f.flight_id}')">Book</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function populateFlightSelects(flights) {
    const bookSelect = document.getElementById("book-flight-id");
    const waitSelect = document.getElementById("waitlist-flight-id");

    const optionsHtml = flights.map(f => 
        `<option value="${f.flight_id}">${f.flight_id} - ${f.airline} (${f.origin}➔${f.dest})</option>`
    ).join("");

    bookSelect.innerHTML = optionsHtml;
    waitSelect.innerHTML = optionsHtml;
}

function quickSelectFlight(flightId) {
    const bookSelect = document.getElementById("book-flight-id");
    bookSelect.value = flightId;
    document.getElementById("booking-section").scrollIntoView({ behavior: 'smooth' });
    document.getElementById("book-passenger-name").focus();
}

async function searchFlight() {
    const query = document.getElementById("flight-search-input").value.trim();
    const method = document.getElementById("search-method-select").value;

    if (!query) {
        showToast("Please enter a Flight ID to search.", "warning");
        return;
    }

    try {
        const res = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flight_id: query, method: method })
        });
        const data = await res.json();

        if (data.success && data.result) {
            const r = data.result;
            const benchCard = document.getElementById("algo-feedback");
            const title = document.getElementById("algo-title");
            const stats = document.getElementById("algo-stats");

            benchCard.classList.remove("hidden");
            title.textContent = `🔍 ${r.algorithm} Results for Flight ID: ${query.toUpperCase()}`;

            if (r.found) {
                renderFlightsTable([r.flight]);
                stats.innerHTML = `
                    <div><strong>Status:</strong> Found at Index [${r.index}]</div>
                    <div><strong>Key Comparisons:</strong> ${r.comparisons}</div>
                    <div><strong>Time Complexity:</strong> ${method === 'binary' ? 'O(log n)' : 'O(n)'}</div>
                `;
                showToast(`Flight ${query.toUpperCase()} found in ${r.comparisons} comparisons!`, "success");
            } else {
                renderFlightsTable([]);
                stats.innerHTML = `
                    <div style="color:var(--color-danger)"><strong>Status:</strong> Not Found</div>
                    <div><strong>Total Comparisons Checked:</strong> ${r.comparisons}</div>
                `;
                showToast(`Flight ${query.toUpperCase()} not found.`, "warning");
            }
        }
    } catch (err) {
        showToast("Error executing flight search.", "error");
    }
}

async function sortFlights(key, algorithm) {
    try {
        const res = await fetch("/api/sort", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ key: key, algorithm: algorithm, ascending: true })
        });
        const data = await res.json();

        if (data.success && data.result) {
            const r = data.result;
            renderFlightsTable(r.sorted_flights);

            const benchCard = document.getElementById("algo-feedback");
            const title = document.getElementById("algo-title");
            const stats = document.getElementById("algo-stats");

            benchCard.classList.remove("hidden");
            title.textContent = `⚡ ${r.algorithm} Execution Metrics (Sorted by ${r.sorted_by.toUpperCase()})`;
            stats.innerHTML = `
                <div><strong>Passes:</strong> ${r.passes}</div>
                <div><strong>Comparisons:</strong> ${r.comparisons}</div>
                <div><strong>Swaps Performed:</strong> ${r.swaps}</div>
                <div><strong>Time Complexity:</strong> O(n²)</div>
            `;
            showToast(`Flights sorted using ${r.algorithm}!`, "success");
        }
    } catch (err) {
        showToast("Error sorting flight directory.", "error");
    }
}

/* ==========================================================================
   BOOKINGS & MANIFEST (SINGLY LINKED LIST & ACTIONS)
   ========================================================================== */
async function bookTicket() {
    const flightId = document.getElementById("book-flight-id").value;
    const name = document.getElementById("book-passenger-name").value.trim();
    const seat = document.getElementById("book-seat").value.trim() || "AUTO";

    if (!name) {
        showToast("Passenger name is required.", "warning");
        return;
    }

    try {
        const res = await fetch("/api/book", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flight_id: flightId, name: name, seat: seat })
        });
        const data = await res.json();

        if (data.success) {
            showToast(`Confirmed! PNR: ${data.pnr} assigned to ${name} (Seat ${data.ticket.seat}).`, "success");
            document.getElementById("book-passenger-name").value = "";
            resetCabinSeat();
            await Promise.all([loadManifest(), syncMemoryState()]);
        } else {
            showToast(data.message || "Failed to book ticket.", "error");
        }
    } catch (err) {
        showToast("Server communication error.", "error");
    }
}

async function cancelTicket(pnrVal) {
    const pnr = pnrVal || document.getElementById("cancel-pnr-input").value.trim();
    if (!pnr) {
        showToast("Please enter a valid PNR to cancel.", "warning");
        return;
    }

    try {
        const res = await fetch("/api/cancel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pnr: pnr })
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, "success");
            document.getElementById("cancel-pnr-input").value = "";
            await Promise.all([loadManifest(), syncMemoryState()]);
        } else {
            showToast(data.message || "Cancellation failed.", "error");
        }
    } catch (err) {
        showToast("Server error during cancellation.", "error");
    }
}

async function loadManifest() {
    try {
        const res = await fetch("/api/manifest");
        const data = await res.json();
        if (data.success) {
            renderManifestTable(data.manifest);
        }
    } catch (err) {
        console.error("Failed to load manifest", err);
    }
}

function renderManifestTable(manifest) {
    const tbody = document.getElementById("manifest-table-body");
    const countBadge = document.getElementById("manifest-count-badge");
    tbody.innerHTML = "";

    countBadge.textContent = `${manifest.length} Confirmed`;

    // Synchronize cabin seat map with current Singly Linked List passenger manifest
    updateCabinSeatStatus(manifest);

    if (!manifest || manifest.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">Manifest is empty. No passengers currently booked.</td></tr>`;
        return;
    }

    manifest.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong style="font-family:var(--font-mono); color: #4338ca;">${p.pnr}</strong></td>
            <td><strong>${p.name}</strong></td>
            <td><span class="flight-code">${p.flight_id}</span></td>
            <td><span class="airport-badge">${p.seat}</span></td>
            <td><span class="status-tag status-confirmed">CONFIRMED</span></td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="cancelTicket('${p.pnr}')">Cancel</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

/* ==========================================================================
   INTERACTIVE AIRCRAFT CABIN SEAT VISUALIZER
   (First Class Suite Pods, Business Recliners, Economy Comfort Chairs)
   ========================================================================== */
const ALL_CABIN_SEATS = [
    { code: "1A", classType: "First Class Suite", pillId: "pill-1A", defaultPillText: "SUITE", defaultPillClass: "pill-vacant-first" },
    { code: "1F", classType: "First Class Suite", pillId: "pill-1F", defaultPillText: "SUITE", defaultPillClass: "pill-vacant-first" },
    { code: "2A", classType: "First Class Suite", pillId: "pill-2A", defaultPillText: "SUITE", defaultPillClass: "pill-vacant-first" },
    { code: "2F", classType: "First Class Suite", pillId: "pill-2F", defaultPillText: "SUITE", defaultPillClass: "pill-vacant-first" },
    { code: "3A", classType: "Business Class", pillId: "pill-3A", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "3C", classType: "Business Class", pillId: "pill-3C", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "3D", classType: "Business Class", pillId: "pill-3D", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "3F", classType: "Business Class", pillId: "pill-3F", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "4A", classType: "Business Class", pillId: "pill-4A", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "4C", classType: "Business Class", pillId: "pill-4C", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "4D", classType: "Business Class", pillId: "pill-4D", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "4F", classType: "Business Class", pillId: "pill-4F", defaultPillText: "BIZ", defaultPillClass: "pill-vacant-business" },
    { code: "5A", classType: "Economy Class", pillId: "pill-5A", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "5B", classType: "Economy Class", pillId: "pill-5B", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "5C", classType: "Economy Class", pillId: "pill-5C", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "5D", classType: "Economy Class", pillId: "pill-5D", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "5E", classType: "Economy Class", pillId: "pill-5E", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "5F", classType: "Economy Class", pillId: "pill-5F", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6A", classType: "Economy Class", pillId: "pill-6A", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6B", classType: "Economy Class", pillId: "pill-6B", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6C", classType: "Economy Class", pillId: "pill-6C", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6D", classType: "Economy Class", pillId: "pill-6D", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6E", classType: "Economy Class", pillId: "pill-6E", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" },
    { code: "6F", classType: "Economy Class", pillId: "pill-6F", defaultPillText: "ECON", defaultPillClass: "pill-vacant-economy" }
];

let selectedCabinSeatCode = null;

function toggleCabinMap() {
    const sec = document.getElementById("aircraft-cabin-section");
    if (!sec) return;
    const isCollapsed = sec.classList.toggle("collapsed");
    const btnText = document.getElementById("cabin-btn-text");
    if (btnText) btnText.textContent = isCollapsed ? "Cabin Map" : "Hide Map";
    if (!isCollapsed) {
        sec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function selectCabinSeat(seatCode, seatClass) {
    const chair = document.getElementById(`chair-${seatCode}`);
    if (chair && chair.disabled) {
        showToast(`Seat ${seatCode} is already booked! Please pick a vacant seat.`, "warning");
        return;
    }

    selectedCabinSeatCode = seatCode;
    const seatInput = document.getElementById("book-seat");
    if (seatInput) seatInput.value = seatCode;
    
    const label = document.getElementById("cabin-selected-label");
    if (label) label.textContent = `Selected: ${seatCode} • ${seatClass}`;

    // Highlight selected seat chair
    ALL_CABIN_SEATS.forEach(s => {
        const el = document.getElementById(`chair-${s.code}`);
        const pill = document.getElementById(s.pillId);
        if (el && !el.disabled) {
            const isMatch = (s.code === seatCode);
            el.classList.toggle("selected-seat", isMatch);
            if (pill) {
                pill.className = isMatch ? "seat-status-pill pill-selected" : `seat-status-pill ${s.defaultPillClass}`;
                pill.textContent = isMatch ? "PICKED" : s.defaultPillText;
            }
        }
    });

    showToast(`💺 Selected Seat ${seatCode} (${seatClass})! Ready to book.`, "info");
}

function resetCabinSeat() {
    selectedCabinSeatCode = null;
    const seatInput = document.getElementById("book-seat");
    if (seatInput) seatInput.value = "AUTO";

    const label = document.getElementById("cabin-selected-label");
    if (label) label.textContent = "Selected: AUTO (System Assigned)";

    ALL_CABIN_SEATS.forEach(s => {
        const el = document.getElementById(`chair-${s.code}`);
        const pill = document.getElementById(s.pillId);
        if (el && !el.disabled) {
            el.classList.remove("selected-seat");
            if (pill) {
                pill.className = `seat-status-pill ${s.defaultPillClass}`;
                pill.textContent = s.defaultPillText;
            }
        }
    });
    showToast("Reset seat selection to AUTO.", "info");
}

function updateCabinSeatStatus(manifest) {
    const bookedMap = {};
    if (manifest && Array.isArray(manifest)) {
        manifest.forEach(p => {
            if (p.seat) {
                bookedMap[p.seat.toUpperCase().trim()] = p;
            }
        });
    }

    ALL_CABIN_SEATS.forEach(s => {
        const chair = document.getElementById(`chair-${s.code}`);
        const pill = document.getElementById(s.pillId);
        if (!chair || !pill) return;

        const bookedPassenger = bookedMap[s.code.toUpperCase()];
        if (bookedPassenger) {
            chair.disabled = true;
            chair.classList.add("occupied");
            chair.classList.remove("selected-seat");
            chair.title = `Booked: ${bookedPassenger.name} (${bookedPassenger.pnr})`;
            pill.className = "seat-status-pill pill-booked";
            pill.textContent = "BOOKED";
        } else {
            chair.disabled = false;
            chair.classList.remove("occupied");
            chair.title = `Available: ${s.code} (${s.classType})`;
            if (selectedCabinSeatCode === s.code) {
                chair.classList.add("selected-seat");
                pill.className = "seat-status-pill pill-selected";
                pill.textContent = "PICKED";
            } else {
                chair.classList.remove("selected-seat");
                pill.className = `seat-status-pill ${s.defaultPillClass}`;
                pill.textContent = s.defaultPillText;
            }
        }
    });
}

/* ==========================================================================
   WAITLIST DESK (CIRCULAR QUEUE)
   ========================================================================== */
async function enqueueWaitlist() {
    let name = document.getElementById("waitlist-name").value.trim();
    const flightId = document.getElementById("waitlist-flight-id").value;

    if (!name) {
        name = "Waitlist Passenger " + (Math.floor(Math.random() * 899) + 100);
    }

    try {
        const res = await fetch("/api/waitlist/enqueue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, flight_id: flightId })
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, "success");
            document.getElementById("waitlist-name").value = "";
            await syncMemoryState();
        } else {
            // Check for Queue Overflow!
            if (data.error_type === "QUEUE_OVERFLOW") {
                showToast(`🛑 ${data.message}`, "error");
            } else {
                showToast(data.message, "error");
            }
        }
    } catch (err) {
        showToast("Error updating waitlist queue.", "error");
    }
}

async function dequeueWaitlist() {
    try {
        const res = await fetch("/api/waitlist/dequeue", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        const data = await res.json();

        if (data.success) {
            showToast(data.message, "success");
            await Promise.all([loadManifest(), syncMemoryState()]);
        } else {
            // Check for Queue Underflow!
            if (data.error_type === "QUEUE_UNDERFLOW") {
                showToast(`⚠️ ${data.message}`, "warning");
            } else {
                showToast(data.message, "error");
            }
        }
    } catch (err) {
        showToast("Error processing waitlist queue.", "error");
    }
}

/* ==========================================================================
   ACTION UNDO ENGINE (STACK - LIFO)
   ========================================================================== */
async function executeUndo() {
    try {
        const res = await fetch("/api/undo", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        const data = await res.json();

        if (data.success) {
            showToast(`↩️ ${data.message}`, "success");
            await Promise.all([loadManifest(), syncMemoryState()]);
        } else {
            if (data.error_type === "STACK_UNDERFLOW") {
                showToast(`⚠️ Stack Underflow! History stack is empty; nothing to undo.`, "warning");
            } else {
                showToast(data.message, "error");
            }
        }
    } catch (err) {
        showToast("Undo request failed.", "error");
    }
}

async function testStackOverflow() {
    // Book simulated rapid bookings to demonstrate Stack Overflow
    try {
        const randomName = "Demo Action " + Math.floor(Math.random() * 100);
        const res = await fetch("/api/book", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ flight_id: "AI-101", name: randomName, seat: "AUTO" })
        });
        const data = await res.json();
        if (data.success) {
            if (data.stack_status && data.stack_status.includes("Full")) {
                showToast(`🛑 ${data.stack_status}`, "error");
            } else {
                showToast(`Pushed action to stack! (Top moved up)`, "info");
            }
            await Promise.all([loadManifest(), syncMemoryState()]);
        }
    } catch (err) {
        showToast("Test push failed.", "error");
    }
}

/* ==========================================================================
   PNR LOOKUP (HASH TABLE - MODULO & CHAINING)
   ========================================================================== */
async function lookupTicket() {
    const pnr = document.getElementById("lookup-pnr-input").value.trim();
    if (!pnr) {
        showToast("Please enter a PNR code.", "warning");
        return;
    }

    try {
        const res = await fetch("/api/lookup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pnr: pnr })
        });
        const data = await res.json();
        const card = document.getElementById("lookup-result-card");
        card.classList.remove("hidden");

        if (data.found && data.ticket) {
            const t = data.ticket;
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                    <strong style="color:var(--brand-accent); font-family:var(--font-mono); font-size:1.1rem;">${data.pnr}</strong>
                    <span class="status-tag status-confirmed">${t.status || 'CONFIRMED'}</span>
                </div>
                <div style="font-size:0.82rem; line-height:1.6;">
                    <div><strong>Passenger:</strong> ${t.name}</div>
                    <div><strong>Flight Code:</strong> ${t.flight_id}</div>
                    <div><strong>Assigned Seat:</strong> ${t.seat}</div>
                    <div style="margin-top:0.5rem; padding:0.4rem; background:#ede9fe; border-radius:4px; font-family:var(--font-mono); font-size:0.75rem; color:#5b21b6;">
                        🎯 <strong>Hash Table Slot:</strong> Bucket #[${data.bucket_index}] (hash = key % 7)
                    </div>
                </div>
            `;
            showToast(`PNR found in Hash Bucket #${data.bucket_index}`, "success");
        } else {
            card.innerHTML = `
                <div style="color:var(--color-danger); font-size:0.85rem; font-weight:600;">
                    ❌ PNR '${pnr.toUpperCase()}' was not found.
                </div>
                <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem;">
                    Target slot Bucket #[${data.bucket_index}] was examined in O(1) time.
                </div>
            `;
            showToast(data.message, "warning");
        }
    } catch (err) {
        showToast("Error during PNR lookup.", "error");
    }
}

/* ==========================================================================
   UPGRADED ROUTE NETWORK & AIRSPACE RADAR GRAPH CONTROLLER
   (BFS, DFS, Dijkstra by Distance/Fare, Backtracking Alternative Routes)
   ========================================================================== */

let globalAirportsList = [];
let globalNetworkEdges = [];
let lastCalculatedPath = [];

async function loadAirports() {
    try {
        const res = await fetch("/api/airports");
        const data = await res.json();
        if (data.success && data.airports) {
            globalAirportsList = data.airports;
            const originSelect = document.getElementById("route-origin-select");
            const destSelect = document.getElementById("route-dest-select");

            const opts = data.airports.map(a => 
                `<option value="${a.code}">${a.code} - ${a.name} (${a.city || ''})</option>`
            ).join("");

            if (originSelect && destSelect) {
                originSelect.innerHTML = opts;
                destSelect.innerHTML = opts;

                // Defaults: BOM (Mumbai) to CCU (Kolkata)
                originSelect.value = "BOM";
                destSelect.value = "CCU";
            }

            // Sync network edges from state
            const stateRes = await fetch("/api/state");
            const stateData = await stateRes.json();
            if (stateData.success && stateData.state && stateData.state.graph) {
                globalNetworkEdges = stateData.state.graph.edges || [];
            }

            renderAirportRadarGraph();
        }
    } catch (err) {
        console.error("Failed to load airports", err);
    }
}

function renderAirportRadarGraph(highlightPath = []) {
    const svg = document.getElementById("route-network-svg");
    if (!svg) return;
    svg.innerHTML = "";

    const originSelect = document.getElementById("route-origin-select");
    const destSelect = document.getElementById("route-dest-select");
    const originCode = originSelect ? originSelect.value : "";
    const destCode = destSelect ? destSelect.value : "";

    const SVG_WIDTH = 800;
    const SVG_HEIGHT = 330;

    // 1. Draw Radar Background Concentric Rings & Range Marks
    const radarGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const center = { x: 400, y: 165 };
    [70, 140, 210, 280].forEach(r => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", center.x);
        circle.setAttribute("cy", center.y);
        circle.setAttribute("r", r);
        circle.setAttribute("fill", "none");
        circle.setAttribute("stroke", "#14253d");
        circle.setAttribute("stroke-width", "1");
        circle.setAttribute("stroke-dasharray", "4, 6");
        radarGroup.appendChild(circle);
    });
    svg.appendChild(radarGroup);

    // Map airports by code for fast coordinate lookup
    const nodeMap = {};
    globalAirportsList.forEach(a => {
        const cx = (a.x / 100) * SVG_WIDTH;
        const cy = (a.y / 100) * SVG_HEIGHT;
        nodeMap[a.code] = { ...a, cx, cy };
    });

    // 2. Draw Flight Route Edges (Lines & Distance Tags)
    const edgesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const labelsGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");

    // Helper to test if an edge is part of the highlighted route path
    function isEdgeInPath(u, v) {
        if (!highlightPath || highlightPath.length < 2) return false;
        for (let i = 0; i < highlightPath.length - 1; i++) {
            const p1 = highlightPath[i];
            const p2 = highlightPath[i + 1];
            if ((p1 === u && p2 === v) || (p1 === v && p2 === u)) {
                return true;
            }
        }
        return false;
    }

    globalNetworkEdges.forEach(edge => {
        const n1 = nodeMap[edge.from];
        const n2 = nodeMap[edge.to];
        if (!n1 || !n2) return;

        const isPath = isEdgeInPath(edge.from, edge.to);

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", n1.cx);
        line.setAttribute("y1", n1.cy);
        line.setAttribute("x2", n2.cx);
        line.setAttribute("y2", n2.cy);
        line.setAttribute("class", isPath ? "svg-edge-line active-path" : "svg-edge-line");
        edgesGroup.appendChild(line);

        // Distance & fare badge at edge midpoint
        const midX = (n1.cx + n2.cx) / 2;
        const midY = (n1.cy + n2.cy) / 2 - 4;
        const distLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
        distLabel.setAttribute("x", midX);
        distLabel.setAttribute("y", midY);
        distLabel.setAttribute("text-anchor", "middle");
        distLabel.setAttribute("class", isPath ? "svg-edge-label active-path" : "svg-edge-label");
        distLabel.textContent = isPath ? `${edge.distance_km}km • ₹${edge.fare}` : `${edge.distance_km}km`;
        labelsGroup.appendChild(distLabel);
    });

    svg.appendChild(edgesGroup);
    svg.appendChild(labelsGroup);

    // 3. Draw Airport Nodes (Vertices)
    const nodesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");

    globalAirportsList.forEach(a => {
        const node = nodeMap[a.code];
        if (!node) return;

        const isOrigin = (a.code === originCode);
        const isDest = (a.code === destCode);
        const isInPath = highlightPath && highlightPath.includes(a.code);

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.style.cursor = "pointer";
        g.onclick = () => onRadarNodeClick(a.code);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", node.cx);
        circle.setAttribute("cy", node.cy);
        circle.setAttribute("r", isOrigin || isDest ? "19" : "16");

        let nodeClass = "svg-node-circle";
        if (isOrigin) nodeClass += " origin-node";
        else if (isDest) nodeClass += " dest-node";
        else if (isInPath) nodeClass += " active-node";
        circle.setAttribute("class", nodeClass);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", node.cx);
        text.setAttribute("y", node.cy);
        text.setAttribute("class", "svg-node-text");
        text.textContent = a.code;

        const cityText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        cityText.setAttribute("x", node.cx);
        cityText.setAttribute("y", node.cy + 24);
        cityText.setAttribute("class", "svg-node-city-text");
        cityText.textContent = a.city || a.code;

        g.appendChild(circle);
        g.appendChild(text);
        g.appendChild(cityText);
        nodesGroup.appendChild(g);
    });

    svg.appendChild(nodesGroup);
}

function onRadarNodeClick(airportCode) {
    const originSelect = document.getElementById("route-origin-select");
    const destSelect = document.getElementById("route-dest-select");
    if (!originSelect || !destSelect) return;

    if (originSelect.value !== airportCode) {
        destSelect.value = airportCode;
        showToast(`📍 Set destination airport to ${airportCode}`, "info");
    } else {
        originSelect.value = airportCode;
        showToast(`🛫 Set origin airport to ${airportCode}`, "info");
    }
    renderAirportRadarGraph(lastCalculatedPath);
}

async function findRouteUpgraded() {
    const originSelect = document.getElementById("route-origin-select");
    const destSelect = document.getElementById("route-dest-select");
    const algoSelect = document.getElementById("route-algo-select");

    const origin = originSelect.value;
    const dest = destSelect.value;
    const selectedMode = algoSelect.value;

    if (origin === dest) {
        showToast("Origin and destination airports must be distinct vertices.", "warning");
        return;
    }

    // Resolve algorithm and weight parameter
    let algorithm = "bfs";
    let weightMetric = "distance_km";

    if (selectedMode === "dfs") {
        algorithm = "dfs";
    } else if (selectedMode === "dijkstra_dist") {
        algorithm = "dijkstra";
        weightMetric = "distance_km";
    } else if (selectedMode === "dijkstra_fare") {
        algorithm = "dijkstra";
        weightMetric = "fare";
    } else if (selectedMode === "all_routes") {
        algorithm = "all_routes";
    }

    try {
        const res = await fetch("/api/route", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                origin: origin,
                dest: dest,
                algorithm: algorithm,
                weight_metric: weightMetric
            })
        });
        const data = await res.json();
        const box = document.getElementById("route-result-box");
        box.classList.remove("hidden");

        if (selectedMode === "all_routes") {
            handleAllRoutesDisplay(data, box);
            return;
        }

        if (data.found && data.path) {
            lastCalculatedPath = data.path;
            renderAirportRadarGraph(data.path);

            const stepsHtml = data.path.map((code, idx) => `
                <span class="route-step-pill">${code}</span>
                ${idx < data.path.length - 1 ? '<span class="route-arrow">➔</span>' : ''}
            `).join("");

            let legsRowsHtml = "";
            if (data.legs && Array.isArray(data.legs)) {
                legsRowsHtml = data.legs.map((leg, i) => `
                    <tr>
                        <td><strong>Leg ${i + 1}</strong></td>
                        <td><span class="flight-code">${leg.from} ➔ ${leg.to}</span></td>
                        <td>${leg.distance_km} km</td>
                        <td>₹${leg.fare.toLocaleString('en-IN')}</td>
                        <td>${Math.floor(leg.duration_mins / 60)}h ${leg.duration_mins % 60}m</td>
                    </tr>
                `).join("");
            }

            box.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.5rem;">
                    <div>
                        <span class="ds-pill pill-graph" style="font-size:0.68rem;">${data.algorithm}</span>
                        <h3 style="font-size:1rem; font-weight:800; color:var(--text-primary); margin-top:2px;">
                            Optimal Route Found: ${origin} ➔ ${dest}
                        </h3>
                    </div>
                    <span class="badge" style="background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; font-family:var(--font-mono);">
                        ${data.stops} Flight Leg${data.stops > 1 ? 's' : ''} (${data.stops - 1} Layover${data.stops > 2 ? 's' : ''})
                    </span>
                </div>

                <!-- 4 Metrics Analytics Grid -->
                <div class="route-analytics-grid">
                    <div class="route-stat-card">
                        <div class="route-stat-val">${data.total_distance_km.toLocaleString()} km</div>
                        <div class="route-stat-lbl">Total Flight Distance</div>
                    </div>
                    <div class="route-stat-card">
                        <div class="route-stat-val" style="color:#1d4ed8;">₹${data.total_fare.toLocaleString('en-IN')}</div>
                        <div class="route-stat-lbl">Combined Fare Estimate</div>
                    </div>
                    <div class="route-stat-card">
                        <div class="route-stat-val" style="color:#059669;">${data.formatted_duration}</div>
                        <div class="route-stat-lbl">Est. Airborne Duration</div>
                    </div>
                    <div class="route-stat-card">
                        <div class="route-stat-val" style="color:#d97706;">${data.stops} Legs</div>
                        <div class="route-stat-lbl">Flight Connections</div>
                    </div>
                </div>

                <!-- Pathway Sequence -->
                <div style="font-size:0.75rem; font-weight:700; color:var(--text-secondary); margin-top:0.6rem;">Itinerary Route Sequence:</div>
                <div class="route-steps-chain">${stepsHtml}</div>

                <!-- Flight Legs Breakdown Table -->
                ${legsRowsHtml ? `
                <div style="margin-top:0.85rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:var(--text-secondary); margin-bottom:0.3rem;">Connecting Legs Breakdown:</div>
                    <table class="route-legs-table">
                        <thead>
                            <tr>
                                <th>Flight Leg</th>
                                <th>Connection</th>
                                <th>Sector Distance</th>
                                <th>Ticket Fare</th>
                                <th>Flight Time</th>
                            </tr>
                        </thead>
                        <tbody>${legsRowsHtml}</tbody>
                    </table>
                </div>` : ''}

                <!-- Traversal Order -->
                <div style="margin-top:0.75rem; font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">
                    <strong>Algorithm Node Visit Order:</strong> ${data.visited_order.join(" ➔ ")}
                </div>
            `;
            showToast(`Route computed using ${data.algorithm}!`, "success");
        } else {
            box.innerHTML = `<div style="color:var(--color-danger); font-size:0.85rem; font-weight:600;">❌ ${data.message}</div>`;
            showToast(data.message, "warning");
        }
    } catch (err) {
        showToast("Error executing graph route algorithm.", "error");
    }
}

function handleAllRoutesDisplay(data, box) {
    if (!data.found || !data.routes || data.routes.length === 0) {
        box.innerHTML = `<div style="color:var(--color-danger); font-size:0.85rem;">No alternative routes discovered.</div>`;
        return;
    }

    const cardsHtml = data.routes.map((r, idx) => `
        <div class="alternative-route-card">
            <div>
                <div style="font-weight:700; font-size:0.85rem; color:var(--brand-primary); display:flex; align-items:center; gap:0.4rem;">
                    <span>Option ${idx + 1}: ${r.path.join(" ➔ ")}</span>
                    ${idx === 0 ? '<span class="status-tag status-confirmed">Fastest</span>' : ''}
                </div>
                <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:2px;">
                    ${r.stops} Leg${r.stops > 1 ? 's' : ''} • ${r.total_distance_km.toLocaleString()} km • ₹${r.total_fare.toLocaleString('en-IN')} • ${r.formatted_duration}
                </div>
            </div>
            <button class="btn btn-sm btn-outline" onclick='highlightAlternativeRoute(${JSON.stringify(r.path)})'>
                View on Radar
            </button>
        </div>
    `).join("");

    box.innerHTML = `
        <div style="font-size:0.85rem; font-weight:800; color:var(--brand-primary); margin-bottom:0.6rem;">
            Discovered ${data.total_routes_found} Connecting Itineraries between ${data.origin} and ${data.destination}
        </div>
        <div>${cardsHtml}</div>
    `;

    // Highlight top route on radar by default
    if (data.routes[0]) {
        lastCalculatedPath = data.routes[0].path;
        renderAirportRadarGraph(data.routes[0].path);
    }
    showToast(`Found ${data.total_routes_found} alternative flight itineraries!`, "success");
}

function highlightAlternativeRoute(path) {
    lastCalculatedPath = path;
    renderAirportRadarGraph(path);
    showToast(`Displaying route: ${path.join(" ➔ ")} on radar.`, "info");
}

// Backward-compatible alias
function findShortestRoute() {
    findRouteUpgraded();
}

/* ==========================================================================
   LIVE MEMORY INSPECTOR CONTROLLER (ALL 5 DATA STRUCTURES)
   ========================================================================== */
async function syncMemoryState() {
    try {
        const res = await fetch("/api/state");
        const data = await res.json();
        if (data.success && data.state) {
            const s = data.state;
            renderStackVisualizer(s.stack);
            renderQueueVisualizer(s.queue);
            renderLinkedListVisualizer(s.linked_list);
            renderHashTableVisualizer(s.hash_table);
            renderGraphVisualizer(s.graph);

            // Update header count badges
            document.getElementById("waitlist-active-count").textContent = s.queue.count;
            updateQueueStatusBox(s.queue);
        }
    } catch (err) {
        console.error("Failed to sync memory state", err);
    }
}

function updateQueueStatusBox(q) {
    const box = document.getElementById("queue-status-box");
    const text = document.getElementById("queue-status-text");

    if (q.is_full) {
        box.innerHTML = `<span class="status-indicator-dot dot-danger"></span><span style="color:#b91c1c;">QUEUE OVERFLOW (5/5 Full)</span>`;
    } else if (q.is_empty) {
        box.innerHTML = `<span class="status-indicator-dot dot-ready"></span><span>Queue Empty (0/5)</span>`;
    } else {
        box.innerHTML = `<span class="status-indicator-dot dot-warning"></span><span>Active (${q.count}/5)</span>`;
    }
}

// 1. Stack Visualizer
function renderStackVisualizer(stackData) {
    const container = document.getElementById("stack-container");
    const pointerLabel = document.getElementById("stack-pointer-label");
    container.innerHTML = "";

    pointerLabel.textContent = stackData.top_index === -1 
        ? "Top: -1 (Stack Underflow / Empty)" 
        : `Top Pointer: Index [${stackData.top_index}]`;

    if (stackData.is_full) {
        const overBanner = document.createElement("div");
        overBanner.className = "overflow-banner";
        overBanner.textContent = "🛑 STACK OVERFLOW! Capacity 5 reached";
        container.appendChild(overBanner);
    }

    // Render slots in reverse (index 4 down to 0) to simulate vertical stack tube
    for (let i = stackData.capacity - 1; i >= 0; i--) {
        const slot = stackData.slots[i];
        const slotEl = document.createElement("div");
        slotEl.className = `stack-slot ${slot.value ? 'active' : ''} ${slot.is_top ? 'is-top' : ''}`;

        let valLabel = `<span style="color:var(--text-light); font-style:italic;">[ Empty Slot ]</span>`;
        if (slot.value) {
            valLabel = `<strong>${slot.value.action}</strong> (${slot.value.pnr || ''})`;
        }

        slotEl.innerHTML = `
            <span>[Slot ${i}] ${valLabel}</span>
            ${slot.is_top ? '<span class="top-badge">TOP ➔</span>' : ''}
        `;
        container.appendChild(slotEl);
    }
}

// 2. Queue Visualizer
function renderQueueVisualizer(qData) {
    const container = document.getElementById("queue-container");
    const label = document.getElementById("queue-pointers-label");
    container.innerHTML = "";

    const frontStr = qData.front_index !== null ? qData.front_index : "None";
    const rearStr = qData.rear_index !== null ? qData.rear_index : "None";
    label.textContent = `Front: [${frontStr}] | Rear: [${rearStr}] | Count: ${qData.count}/${qData.capacity}`;

    qData.slots.forEach(slot => {
        const slotEl = document.createElement("div");
        slotEl.className = `queue-slot ${slot.value ? 'active' : ''}`;

        let pillsHtml = "";
        if (slot.is_front) pillsHtml += `<span class="pointer-pill pointer-front">FRONT</span>`;
        if (slot.is_rear) pillsHtml += `<span class="pointer-pill pointer-rear">REAR</span>`;

        let passengerName = slot.value ? slot.value.name.split(" ")[0] : "Empty";

        slotEl.innerHTML = `
            <div style="font-weight:700; color:var(--text-muted);">[${slot.index}]</div>
            <div style="font-size:0.65rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60px;">${passengerName}</div>
            ${pillsHtml}
        `;
        container.appendChild(slotEl);
    });
}

// 3. Singly Linked List Visualizer
function renderLinkedListVisualizer(llData) {
    const container = document.getElementById("ll-chain-container");
    const sizeBadge = document.getElementById("ll-size-label");
    container.innerHTML = "";

    sizeBadge.textContent = `${llData.total_nodes} Nodes`;

    if (!llData.head_exists || llData.nodes.length === 0) {
        container.innerHTML = `
            <div class="ll-node-row">
                <div class="ll-null-box" style="width:100%;">[ HEAD ➔ NULL ] (Empty Linked List)</div>
            </div>
        `;
        return;
    }

    llData.nodes.forEach(node => {
        const row = document.createElement("div");
        row.className = "ll-node-row";
        row.innerHTML = `
            <div class="ll-node-box">
                <span><strong>${node.data.pnr}</strong>: ${node.data.name}</span>
                <span style="color:var(--text-muted);">[${node.data.flight_id}]</span>
            </div>
            <span class="ll-pointer-arrow">➔</span>
        `;
        container.appendChild(row);
    });

    // Final NULL terminator
    const nullRow = document.createElement("div");
    nullRow.className = "ll-node-row";
    nullRow.innerHTML = `<div class="ll-null-box">NULL</div>`;
    container.appendChild(nullRow);
}

// 4. Hash Table Visualizer
function renderHashTableVisualizer(hashData) {
    const container = document.getElementById("hash-table-container");
    const loadBadge = document.getElementById("hash-load-factor");
    container.innerHTML = "";

    loadBadge.textContent = `Keys: ${hashData.total_keys} | Load: ${hashData.load_factor}`;

    hashData.buckets.forEach(b => {
        const row = document.createElement("div");
        row.className = "hash-bucket-row";

        let tagsHtml = b.items.length === 0 
            ? `<span style="color:var(--text-light); font-size:0.65rem;">Empty Bucket</span>`
            : b.items.map(it => `<span class="hash-item-tag">${it.key} (${it.passenger_name.split(' ')[0]})</span>`).join("");

        let colBadge = b.has_collision ? `<span class="collision-badge">Collision (${b.chain_length})</span>` : "";

        row.innerHTML = `
            <span class="hash-bucket-idx">Slot #${b.bucket_index}</span>
            <div class="hash-bucket-items">${tagsHtml}</div>
            ${colBadge}
        `;
        container.appendChild(row);
    });
}

// 5. Upgraded Graph Adjacency List Visualizer
function renderGraphVisualizer(graphData) {
    const container = document.getElementById("graph-container");
    const countBadge = document.getElementById("graph-vertex-count");
    container.innerHTML = "";

    if (!graphData || !graphData.nodes) return;
    countBadge.textContent = `${graphData.nodes.length} Vertices • ${graphData.edges ? graphData.edges.length : 0} Edges`;

    graphData.nodes.forEach(node => {
        // Collect detailed connections with distance and fare
        const edgesForNode = (graphData.edges || []).filter(e => e.from === node.code || e.to === node.code);
        const connectionTags = edgesForNode.map(e => {
            const target = (e.from === node.code) ? e.to : e.from;
            const fareK = Math.round(e.fare / 1000 * 10) / 10;
            return `<span style="background:#f1f5f9; padding:1px 4px; border-radius:3px; margin:0 2px;">${target} (${e.distance_km}km, ₹${fareK}k)</span>`;
        });

        const row = document.createElement("div");
        row.className = "graph-vertex-row";
        row.innerHTML = `
            <span class="graph-vertex-badge">${node.code}</span>
            <span class="graph-edges-list" style="display:inline-flex; flex-wrap:wrap; gap:2px; align-items:center;">
                ➔ ${connectionTags.join("")}
            </span>
        `;
        container.appendChild(row);
    });
}
