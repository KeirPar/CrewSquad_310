const API_URL = "http://localhost:8000";
let currentToken = null;
let currentUser = null;
let menuItemsCache = {};
let lastOrders = [];
let lastQueue = [];
let lastRestaurants = [];
let lastReportQueue = [];

const authSection = document.getElementById("auth-section");
const appLayout = document.getElementById("app-layout");
const sessionSection = document.getElementById("session-section");
const publicToolsSection = document.getElementById("public-tools-section");
const customerDashboard = document.getElementById("customer-dashboard");
const ownerDashboard = document.getElementById("owner-dashboard");
const adminDashboard = document.getElementById("admin-dashboard");
const driverDashboard = document.getElementById("driver-dashboard");
const sharedSection = document.getElementById("shared-section");
const dataDisplay = document.getElementById("data-display");
const requestDisplay = document.getElementById("request-display");

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

// UI Elements
const authSection = document.getElementById('auth-section');
const customerDashboard = document.getElementById('customer-dashboard');
const ownerDashboard = document.getElementById('owner-dashboard');
const adminDashboard = document.getElementById('admin-dashboard');
const sharedSection = document.getElementById('shared-section');
const dataDisplay = document.getElementById('data-display');

function logData(data) {
    const text = typeof data === "string" ? data : toPrettyJson(data);
    dataDisplay.textContent = text;
}

function setBox(id, html) {
    const element = document.getElementById(id);
    if (element) element.innerHTML = html;
}

async function apiRequest(path, options = {}) {
    const method = options.method || "GET";
    const headers = { ...(options.headers || {}) };
    if (options.auth && currentToken) headers.Authorization = `Bearer ${currentToken}`;

    let body = options.body;
    if (body && options.json !== false && !(body instanceof URLSearchParams)) {
        headers["Content-Type"] = headers["Content-Type"] || "application/json";
        body = JSON.stringify(body);
    }

    logRequest({
        method,
        url: `${API_URL}${path}`,
        headers,
        body: body instanceof URLSearchParams ? body.toString() : options.body || null
    });

    const response = await fetch(`${API_URL}${path}`, { method, headers, body });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();
    logData({ status: response.status, ok: response.ok, data });

    if (!response.ok) {
        throw new Error((data && data.detail) || `Request failed with status ${response.status}`);
    }
    return data;
}

function resetDashboards() {
    customerDashboard.style.display = "none";
    ownerDashboard.style.display = "none";
    adminDashboard.style.display = "none";
    driverDashboard.style.display = "none";
}

function fillUpdateForm() {
    if (!currentUser) return;
    document.getElementById("update-name").value = currentUser.name || "";
    document.getElementById("update-email").value = currentUser.email || "";
    document.getElementById("update-phone").value = currentUser.phone_number || "";
    document.getElementById("update-address").value = currentUser.address || "";
    document.getElementById("update-note").value = currentUser.delivery_note || "";
    document.getElementById("update-latitude").value = currentUser.coordinate?.latitude ?? 49.88;
    document.getElementById("update-longitude").value = currentUser.coordinate?.longitude ?? -119.49;
}

async function fetchProfile() {
    currentUser = await apiRequest("/auth/me", { auth: true });
    document.querySelectorAll(".user-name").forEach((element) => {
        element.innerText = currentUser.name;
    });
    currentUser = await res.json();

    document.querySelectorAll('.user-name').forEach(el => el.innerText = currentUser.name);
    authSection.style.display = 'none';
    sharedSection.style.display = 'block';
    ownerDashboard.style.display = 'none';
    customerDashboard.style.display = 'none';
    adminDashboard.style.display = 'none';

    if (currentUser.role.toUpperCase() === 'OWNER' || currentUser.role === 'Restaurant Owner') {
        ownerDashboard.style.display = 'block';
    } else if (currentUser.role === 'Admin') {
        adminDashboard.style.display = 'block';
    } else {
        customerDashboard.style.display = "block";
    }
}

function requireLogin() {
    if (!currentToken) {
        alert("Please login first.");
        return false;
    }
    return true;
}

function normalizeMenuItem(item) {
    return {
        id: item.id,
        name: item.name,
        description: item.description || "",
        price: item.price ?? item.base_price ?? 0,
        category: item.category || "General",
        image_url: item.image_url || "",
        add_ons: Array.isArray(item.add_ons) ? item.add_ons : [],
        is_available: item.is_available !== false,
        restaurant_id: item.restaurant_id
    };
}

function cacheMenuItems(items) {
    items.forEach((item) => {
        menuItemsCache[item.id] = normalizeMenuItem(item);
    });
}

function formatPrice(item) {
    const price = Number(item.price ?? item.base_price ?? 0);
    return Number.isNaN(price) ? "N/A" : `$${price.toFixed(2)}`;
}

function useRestaurantId(restaurantId) {
    document.getElementById("review-restaurant-id").value = restaurantId;
    document.getElementById("fav-restaurant-id").value = restaurantId;
    document.getElementById("manage-rest-id").value = restaurantId;
    document.getElementById("owner-restaurant-id").value = restaurantId;
}

function useOrderId(orderId, restaurantId) {
    document.getElementById("track-order-id").value = orderId;
    document.getElementById("simulate-order-id").value = orderId;
    document.getElementById("decision-order-id").value = orderId;
    document.getElementById("payment-status-order-id").value = orderId;
    document.getElementById("report-order-id").value = orderId;
    document.getElementById("notif-order-id").value = orderId;
    document.getElementById("timeline-order-id").value = orderId;
    document.getElementById("owner-decision-order-id").value = orderId;
    document.getElementById("owner-timeline-order-id").value = orderId;
    if (restaurantId) document.getElementById("report-target-id").value = restaurantId;
}

function renderSearchResults(payload) {
    const restaurants = payload.data || [];
    lastRestaurants = restaurants;
    if (!restaurants.length) {
        setBox("search-results", `<p>${escapeHtml(payload.message || "No restaurants found.")}</p>`);
        return;
    }

    let html = `<p>${escapeHtml(payload.message || "Success")}</p><ul class="list">`;
    restaurants.forEach((restaurant) => {
        html += `
            <li>
                <strong>${escapeHtml(restaurant.name)}</strong> (ID ${restaurant.id}) |
                ${escapeHtml(restaurant.cuisine_type)} |
                Price Tier ${restaurant.price_tier}
                <div class="input-row">
                    <button class="inline-button" onclick="useRestaurantFromSearch(${restaurant.id})">Use Restaurant ID</button>
                    <button class="inline-button" onclick="loadRestaurantMenuAction(${restaurant.id})">Load Menu</button>
                    <button class="inline-button" onclick="loadRestaurantRatingAction(${restaurant.id})">Get Rating</button>
                    <button class="inline-button" onclick="loadRestaurantReviewsAction(${restaurant.id})">Get Reviews</button>
                </div>
            </li>
        `;
    });
    html += "</ul>";
    setBox("search-results", html);
}

// View Favorites
document.getElementById('btn-view-favorites').onclick = async () => {
    try {
        // Fix: Fetch the user profile, because it contains the favourite_restaurants list!
        const res = await fetch(`${API_URL}/auth/me`, { 
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data); 

        const container = document.getElementById('feature-results');
        if (!res.ok) throw new Error(data.detail || "Failed to fetch profile");

        const favRests = data.favourite_restaurants || [];
        if (favRests.length === 0) return container.innerHTML = "You have no favorite restaurants yet.";

        let html = '<ul style="margin-top: 0; padding-left: 20px;">';
        favRests.forEach(id => {
            html += `<li style="margin-bottom: 5px;"><strong>Restaurant ID: ${id}</strong></li>`;
        });
        html += '</ul>';
        container.innerHTML = html;

function renderOrders(orders) {
    lastOrders = orders;
    if (!orders.length) {
        setBox("orders-results", "No orders found.");
        return;
    }

// Add Favorite
document.getElementById('btn-add-favorite').onclick = async () => {
    const restId = parseInt(document.getElementById('add-fav-id').value);
    if (!restId) return alert("Please enter a Restaurant ID to favorite.");

    try {
        // Fix: Updated to exactly match your Python router
        const res = await fetch(`${API_URL}/user/favourites/restaurants/${restId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add favorite");
        
        alert("Restaurant added to favorites!");
        logData(data);
        document.getElementById('btn-view-favorites').click(); 
    } catch (err) { handleError(err); }
};

// View Recent Orders (Recent Items)
document.getElementById('btn-view-recent').onclick = async () => {
    try {
        // Fix: Updated to exactly match your Python router
        const res = await fetch(`${API_URL}/user/recently-ordered`, { 
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data);

        const container = document.getElementById('feature-results');
        if (!res.ok) throw new Error(data.detail || "Failed to fetch recent items");
        
        // Fix: Your backend returns 'recent_items' which are Menu Item objects, not Orders!
        const recentItems = data.recent_items || [];
        if (recentItems.length === 0) return container.innerHTML = "No recent items found.";

        let html = '<ul style="margin-top: 0; padding-left: 20px;">';
        recentItems.forEach(item => {
            html += `<li style="margin-bottom: 5px;"><strong>${item.name}</strong> - $${item.price.toFixed(2)} <br><span style="font-size: 12px; color: gray;">(Restaurant ID: ${item.restaurant_id})</span></li>`;
        });
        html += '</ul>';
        container.innerHTML = html;

function renderQueue(queue) {
    lastQueue = queue;
    if (!queue.length) {
        setBox("queue-results", "No pending orders.");
        return;
    }

    let html = '<ul class="list">';
    queue.forEach((order) => {
        html += `<li><strong>Order #${order.id}</strong> | Status: ${escapeHtml(order.status)} | Created: ${escapeHtml(order.created_at)}<div class="input-row"><button class="inline-button" onclick="useQueueOrder(${order.id})">Use In Update Form</button><button class="inline-button" onclick="trackOrderByIdAction(${order.id})">Get Status</button></div></li>`;
    });
    html += "</ul>";
    setBox("queue-results", html);
}

// 1. Search Menus
document.getElementById('btn-browse-menus').onclick = async () => {
    const nameQuery = document.getElementById('menu-search-name').value.toLowerCase();
    
    try {
        // ADDED: You need this fetch line or 'items' will be undefined!
        const res = await fetch(`${API_URL}/menu?limit=50&offset=0`);
        const data = await res.json();
        let items = data.items || [];

        // Frontend filtering if nameQuery exists
        if (nameQuery) {
            items = items.filter(item => item.name.toLowerCase().includes(nameQuery));
        }

    let html = '<ul class="list">';
    reports.forEach((report) => {
        html += `<li><strong>Report #${report.id}</strong> | Order ${report.order_id} | ${escapeHtml(report.target_type)} ${report.target_id}<br>${escapeHtml(report.reason)}<div class="input-row"><button class="inline-button" onclick="useReportId(${report.id})">Use Report ID</button></div></li>`;
    });
    html += "</ul>";
    setBox("report-results", html);
}

function renderDriverOrders(orders) {
    if (!orders.length) {
        setBox("driver-results", "No nearby orders found.");
        return;
    }

        // Group items by category
        const groupedItems = items.reduce((acc, item) => {
            const cat = item.category || "General";
            if (!acc[cat]) acc[cat] = [];
            acc[cat].push(item);
            return acc;
        }, {});

        // Display by category folders
        for (const category in groupedItems) {
            const catHeader = document.createElement('h4');
            catHeader.innerText = `📂 ${category}`;
            catHeader.style.margin = '15px 0 5px 0';
            resultsContainer.appendChild(catHeader);

            groupedItems[category].forEach(item => {
                menuItemsCache[item.id] = item;
                const itemDiv = document.createElement('div');
                itemDiv.style.borderBottom = '1px solid #eee';
                itemDiv.style.padding = '10px 0';
                itemDiv.style.display = 'flex';
                itemDiv.style.justifyContent = 'space-between';
                itemDiv.style.alignItems = 'center';

                itemDiv.innerHTML = `
                    <div>
                        <strong>${item.name}</strong> - $${item.price.toFixed(2)}<br>
                        <span class="helper-text">${item.description}</span>
                    </div>
                    <button class="btn-secondary" style="width: auto; padding: 6px 12px; margin: 0;" onclick="addToCart(${item.id})">Add</button>
                `;
                resultsContainer.appendChild(itemDiv);
            });
        }
        logData(data);
    } catch (err) { handleError(err); }
};

//Add Item to Cart
window.addToCart = async (itemId) => {
    try {
        const res = await fetch(`${API_URL}/cart/add/${itemId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data);
        
        // Auto-refresh the cart UI
        document.getElementById('btn-view-cart').click(); 
    } catch (err) { handleError(err); }
};

//Remove Item from Cart
window.removeFromCart = async (itemId) => {
    try {
        const res = await fetch(`${API_URL}/cart/remove/${itemId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to remove item");
        
        // Auto-refresh the cart UI so the item visually disappears
        document.getElementById('btn-view-cart').click(); 
    } catch (err) { handleError(err); }
};

// 3. View Cart
document.getElementById('btn-view-cart').onclick = async () => {
    try {
        const res = await fetch(`${API_URL}/cart`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data);

        const cartIds = data.cart_items || [];
        const cartContainer = document.getElementById('cart-contents');
        
        if (cartIds.length === 0) return cartContainer.innerHTML = 'Cart is empty.';

        let html = '<ul style="margin-top: 0; padding-left: 20px;">';
        let total = 0;
        
        cartIds.forEach(id => {
            const item = menuItemsCache[id];
            if (item) {
                // ADDED: A small, red Remove button next to each item
                html += `<li style="margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
                            <span><strong>${item.name}</strong> - $${item.price.toFixed(2)}</span>
                            <button class="btn-danger" style="width: auto; padding: 2px 8px; margin: 0; font-size: 12px;" onclick="removeFromCart(${id})">X</button>
                         </li>`;
                total += item.price;
            } else {
                html += `<li>Item ID: ${id} (Details not loaded)</li>`;
            }
        });
}

async function refreshUserState() {
    if (!currentToken) return;
    await fetchProfile();
}

async function loadRestaurantMenu(restaurantId) {
    const items = await apiRequest(`/menu/${restaurantId}`);
    cacheMenuItems(items);
    refreshScheduledOrderDropdowns();
    renderMenuResults(items.map(normalizeMenuItem));
    useRestaurantId(restaurantId);
}

async function loadRestaurantRating(restaurantId) {
    const rating = await apiRequest(`/restaurants/${restaurantId}/rating`);
    setBox("review-results", `Restaurant ${restaurantId} rating: ${rating}`);
    document.getElementById("review-restaurant-id").value = restaurantId;
}

async function loadRestaurantReviews(restaurantId) {
    const reviews = await apiRequest(`/restaurants/${restaurantId}/reviews`);
    renderReviews(reviews);
    document.getElementById("review-restaurant-id").value = restaurantId;
}

async function loadAllMenus() {
    const nameQuery = document.getElementById("menu-search-name").value.trim().toLowerCase();
    const limit = document.getElementById("menu-limit").value || "50";
    const offset = document.getElementById("menu-offset").value || "0";
    const data = await apiRequest(`/menu?limit=${limit}&offset=${offset}`);
    let items = (data.items || []).map(normalizeMenuItem);
    cacheMenuItems(items);
    refreshScheduledOrderDropdowns();
    if (nameQuery) items = items.filter((item) => item.name.toLowerCase().includes(nameQuery));
    renderMenuResults(items);
}

async function viewCart() {
    if (!requireLogin()) return;
    const data = await apiRequest("/cart", { auth: true });
    renderCart(data.cart_items || []);
}

async function addToCart(itemId) {
    if (!requireLogin()) return;
    await apiRequest(`/cart/add/${itemId}`, { method: "POST", auth: true });
    await viewCart();
}

async function removeFromCart(itemId) {
    if (!requireLogin()) return;
    await apiRequest(`/cart/remove/${itemId}`, { method: "DELETE", auth: true });
    await viewCart();
}

async function clearCart() {
    if (!requireLogin()) return;
    await apiRequest("/cart/clear", { method: "DELETE", auth: true });
    await viewCart();
}

async function checkout() {
    if (!requireLogin()) return;
    const cartData = await apiRequest("/cart", { auth: true });
    const cartIds = cartData.cart_items || [];
    if (!cartIds.length) return alert("Your cart is empty.");

    const items = cartIds.map((id) => menuItemsCache[id]).filter(Boolean);
    if (items.length !== cartIds.length) return alert("Some cart item details are missing. Load menus first.");

    const payload = {
        user_id: currentUser.id,
        cart: {
            id: Date.now(),
            menu_items: items.map(normalizeMenuItem)
        }
    };

    await apiRequest("/orders/", { method: "POST", body: payload });
    await viewOrders();
}

async function viewOrders() {
    if (!requireLogin()) return;
    const orders = await apiRequest("/orders/", { auth: true });
    renderOrders(Array.isArray(orders) ? orders : []);
}

async function trackOrderById(id) {
    const status = await apiRequest(`/orders/${id}`);
    setBox("orders-results", `Order ${id} status: ${escapeHtml(status["order status"])}`);
}

async function cancelOrder() {
    if (!requireLogin()) return;
    const orderId = Number(document.getElementById("track-order-id").value);
    if (!orderId) return alert("Enter an order ID.");

    let order = lastOrders.find((item) => item.id === orderId);
    if (!order) {
        const orders = await apiRequest("/orders/", { auth: true });
        order = (orders || []).find((item) => item.id === orderId);
    }
    if (!order) return alert("Order not found in your history.");

    await apiRequest(`/orders/${orderId}/status?new_status=CANCELLED`, { method: "PATCH", body: order, auth: true });
    await viewOrders();
}

async function searchRestaurants() {
    const params = new URLSearchParams();
    const name = document.getElementById("search-name").value.trim();
    const cuisine = document.getElementById("search-cuisine").value;
    const minRating = document.getElementById("search-min-rating").value;
    const sortBy = document.getElementById("search-sort").value;
    const limit = document.getElementById("search-limit").value || "10";
    const offset = document.getElementById("search-offset").value || "0";

    if (name) params.append("name", name);
    if (cuisine) params.append("cuisine_type", cuisine);
    if (minRating) params.append("min_rating", minRating);
    if (sortBy) params.append("sort_by", sortBy);
    params.append("limit", limit);
    params.append("offset", offset);

    const payload = await apiRequest(`/search/restaurants?${params.toString()}`, { auth: Boolean(currentToken) });
    renderSearchResults(payload);
}

async function viewFavorites() {
    if (!requireLogin()) return;
    await refreshUserState();
    setBox("feature-results", `<p><strong>Favorite Restaurants:</strong> ${(currentUser.favourite_restaurants || []).join(", ") || "None"}</p><p><strong>Favorite Items:</strong> ${(currentUser.favourite_items || []).join(", ") || "None"}</p>`);
}

async function viewRecent() {
    if (!requireLogin()) return;
    const data = await apiRequest("/user/recently-ordered", { auth: true });
    const items = data.recent_items || [];
    cacheMenuItems(items.map(normalizeMenuItem));
    if (!items.length) return setBox("feature-results", "No recently ordered items found.");

    let html = '<ul class="list">';
    items.forEach((item) => {
        html += `<li>${escapeHtml(item.name)} (Item ID ${item.id}) - ${formatPrice(item)}</li>`;
    });
    html += "</ul>";
    setBox("feature-results", html);
}

async function addFavoriteRestaurant() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("fav-restaurant-id").value);
    if (!restaurantId) return alert("Enter a restaurant ID.");
    await apiRequest(`/user/favourites/restaurants/${restaurantId}`, { method: "POST", auth: true });
    await viewFavorites();
}

async function removeFavoriteRestaurant() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("fav-restaurant-id").value);
    if (!restaurantId) return alert("Enter a restaurant ID.");
    await apiRequest(`/user/favourites/restaurants/${restaurantId}`, { method: "DELETE", auth: true });
    await viewFavorites();
}

// Register Storefront
document.getElementById('btn-register-store').onclick = async () => {
    const name = document.getElementById('store-name').value;
    const cuisine = document.getElementById('store-cuisine').value;

    if (!name || !cuisine) return alert("Please provide a name and cuisine type.");

    const payload = {
        name: name,
        cuisine_type: cuisine,
        owner_id: currentUser.id,
        coordinate: currentUser.coordinate,
        address: currentUser.address
    };

    try {
        const res = await fetch(`${API_URL}/search/restaurants`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to register storefront");
        
        alert(`Storefront registered! Your Restaurant ID is: ${data.id}`);
        document.getElementById('manage-rest-id').value = data.id;
        logData(data);
    } catch (err) { handleError(err); }
};

// Add Menu Item (Detailed)
document.getElementById('btn-add-menu').onclick = async () => {
    const restId = document.getElementById('manage-rest-id').value;
    const name = document.getElementById('add-menu-name').value;
    const description = document.getElementById('add-menu-description').value;
    const category = document.getElementById('add-menu-category').value;
    const price = parseFloat(document.getElementById('add-menu-price').value);

async function removeFavoriteItem() {
    if (!requireLogin()) return;
    const itemId = Number(document.getElementById("fav-item-id").value);
    if (!itemId) return alert("Enter a menu item ID.");
    await apiRequest(`/user/favourites/items/${itemId}`, { method: "DELETE", auth: true });
    await viewFavorites();
}

async function updateUser() {
    if (!requireLogin()) return;
    const payload = {
        name: name,
        description: description || "Delicious food",
        price: price,
        category: category || "General",
        image_url: "",
        is_available: true,
        add_ons: [],
        restaurant_id: parseInt(restId)
    };
    const result = await apiRequest("/user/update", { method: "POST", body: payload, auth: true });
    await refreshUserState();
    setBox("feature-results", `<p>${escapeHtml(result.message)}</p>`);
}

    try {
        const res = await fetch(`${API_URL}/menu/${restId}/add`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify(payload)
        });
        logData(await res.json());
        alert("Item added to your menu!");
    } catch (err) { handleError(err); }
};

// Delete Menu Item
document.getElementById('btn-delete-menu').onclick = async () => {
    const restId = document.getElementById('manage-rest-id').value;
    const itemId = document.getElementById('delete-item-id').value;

    if (!restId || !itemId) return alert("Fill out Restaurant ID and Item ID.");

async function submitReview() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("review-restaurant-id").value);
    const content = document.getElementById("review-content").value;
    const rating = Number(document.getElementById("review-rating").value);
    if (!restaurantId || Number.isNaN(rating)) return alert("Enter restaurant ID and rating.");
    const review = await apiRequest(`/restaurants/${restaurantId}/reviews`, { method: "POST", body: { content, rating }, auth: true });
    setBox("review-results", `<pre>${escapeHtml(toPrettyJson(review))}</pre>`);
}

async function simulatePayment() {
    if (!requireLogin()) return;
    const orderId = document.getElementById("simulate-order-id").value;
    if (!orderId) return alert("Enter order ID.");
    await apiRequest(`/payments/${orderId}/simulate`, { method: "POST", auth: true });
}

async function submitPaymentDecision(prefix = "") {
    if (!requireLogin()) return;
    const orderId = document.getElementById(`${prefix}decision-order-id`).value;
    const decision = document.getElementById(`${prefix}decision-value`).value;
    const reason = document.getElementById(`${prefix}decision-reason`).value;
    if (!orderId) return alert("Enter order ID.");
    const body = { decision };
    if (reason) body.reason = reason;
    await apiRequest(`/payments/${orderId}`, { method: "POST", body, auth: true });
}

async function checkOrderStatus() {
    const orderId = document.getElementById("payment-status-order-id").value;
    if (!orderId) return alert("Enter order ID.");
    const data = await apiRequest(`/orders/${orderId}`);
    setBox("orders-results", `Order ${orderId} status: ${escapeHtml(data["order status"])}`);
}

async function loadAllNotifications() {
    await apiRequest("/notifications");
}

async function loadMyNotifications() {
    if (!requireLogin()) return;
    await apiRequest(`/notifications/recipient/${currentUser.id}`, { auth: true });
}

async function loadOrderNotifications() {
    const orderId = document.getElementById("notif-order-id").value;
    if (!orderId) return alert("Enter order ID.");
    await apiRequest(`/notifications/order/${orderId}`, { auth: true });
}

async function loadOrderTimeline(orderInputId) {
    const orderId = document.getElementById(orderInputId).value;
    if (!orderId) return alert("Enter order ID.");
    if (!currentUser) return alert("Login first.");
    await apiRequest(`/notifications/order/${orderId}/recipient/${currentUser.id}`, { auth: true });
}

async function loadScheduledSource() {
    const data = await apiRequest("/menu?limit=200&offset=0");
    cacheMenuItems((data.items || []).map(normalizeMenuItem));
    refreshScheduledOrderDropdowns();
}

async function placeScheduledOrder() {
    if (!requireLogin()) return;
    const itemRaw = document.getElementById("sched-item").value;
    const scheduledTime = document.getElementById("sched-time").value;
    if (!itemRaw || !scheduledTime) return alert("Select a menu item and time.");
    const item = JSON.parse(itemRaw);
    const payload = {
        cart: { id: Date.now(), menu_items: [normalizeMenuItem(item)] },
        scheduled_time: new Date(scheduledTime).toISOString()
    };
    const data = await apiRequest("/scheduled-orders", { method: "POST", body: payload, auth: true });
    setBox("scheduled-results", `<pre>${escapeHtml(toPrettyJson(data))}</pre>`);
}

async function loadMyScheduledOrders() {
    if (!requireLogin()) return;
    const data = await apiRequest("/scheduled-orders/my-orders/all", { auth: true });
    setBox("scheduled-results", `<pre>${escapeHtml(toPrettyJson(data))}</pre>`);
}

async function cancelScheduledOrder() {
    if (!requireLogin()) return;
    const scheduledOrderId = document.getElementById("cancel-sched-id").value;
    const reason = document.getElementById("cancel-sched-reason").value;
    if (!scheduledOrderId) return alert("Enter scheduled order ID.");
    const body = reason ? { reason } : {};
    const data = await apiRequest(`/scheduled-orders/${scheduledOrderId}/cancel`, { method: "PATCH", body, auth: true });
    setBox("scheduled-results", `<pre>${escapeHtml(toPrettyJson(data))}</pre>`);
}

async function getScheduledOrder() {
    if (!requireLogin()) return;
    const scheduledOrderId = document.getElementById("get-sched-id").value;
    if (!scheduledOrderId) return alert("Enter scheduled order ID.");
    const data = await apiRequest(`/scheduled-orders/${scheduledOrderId}`, { auth: true });
    setBox("scheduled-results", `<pre>${escapeHtml(toPrettyJson(data))}</pre>`);
}

async function submitReport() {
    if (!requireLogin()) return;
    const payload = {
        order_id: Number(document.getElementById("report-order-id").value),
        target_type: document.getElementById("report-target-type").value,
        target_id: Number(document.getElementById("report-target-id").value),
        reason: document.getElementById("report-reason").value
    };
    if (!payload.order_id || !payload.target_id || !payload.reason) return alert("Fill in report fields.");
    await apiRequest("/reports/", { method: "POST", body: payload, auth: true });
}

async function registerRestaurant() {
    if (!requireLogin()) return;
    const priceTierValue = Number(document.getElementById("restaurant-price-tier").value);
    const payload = {
        name: document.getElementById("restaurant-name").value,
        address: document.getElementById("restaurant-address").value || currentUser?.address || "123 Main St",
        coordinate: currentUser?.coordinate || { latitude: 49.88, longitude: -119.49 },
        cuisine_type: document.getElementById("restaurant-cuisine").value,
        phone_number: document.getElementById("restaurant-phone").value || currentUser?.phone_number || "250-555-0000",
        price_tier: Number.isFinite(priceTierValue) && priceTierValue >= 1 && priceTierValue <= 4 ? priceTierValue : 1,
        flags: 0
    };
    if (!payload.name || !payload.cuisine_type) return alert("Enter at least a restaurant name and cuisine.");
    await apiRequest("/restaurants/register", { method: "POST", body: payload, auth: true });
    await loadMyRestaurants();
}

async function loadMyRestaurants() {
    if (!requireLogin()) return;
    const data = await apiRequest("/restaurants/my-restaurant", { auth: true });
    renderRestaurants(Array.isArray(data) ? data : []);
}

async function updateRestaurant() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("owner-restaurant-id").value);
    if (!restaurantId) return alert("Enter restaurant ID.");
    const payload = {};
    const name = document.getElementById("update-restaurant-name").value;
    const address = document.getElementById("update-restaurant-address").value;
    const phone = document.getElementById("update-restaurant-phone").value;
    const cuisine = document.getElementById("update-restaurant-cuisine").value;
    const priceTier = document.getElementById("update-restaurant-price-tier").value;
    const openValue = document.getElementById("update-restaurant-open").value;
    if (name) payload.name = name;
    if (address) payload.address = address;
    if (phone) payload.phone_number = phone;
    if (cuisine) payload.cuisine_type = cuisine;
    if (priceTier) payload.price_tier = Number(priceTier);
    if (openValue) payload.is_open = openValue === "true";
    const data = await apiRequest(`/restaurants/${restaurantId}`, { method: "PATCH", body: payload, auth: true });
    setBox("restaurant-results", `<pre>${escapeHtml(toPrettyJson(data))}</pre>`);
}

async function deleteRestaurant() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("owner-restaurant-id").value);
    if (!restaurantId) return alert("Enter restaurant ID.");
    await apiRequest(`/restaurants/${restaurantId}`, { method: "DELETE", auth: true });
    await loadMyRestaurants();
}

async function loadOwnerMenu() {
    const restaurantId = Number(document.getElementById("manage-rest-id").value);
    if (!restaurantId) return alert("Enter restaurant ID.");
    await loadRestaurantMenu(restaurantId);
    setBox("owner-menu-results", document.getElementById("menu-results").innerHTML);
}

async function addMenuItem() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("manage-rest-id").value);
    if (!restaurantId) return alert("Enter restaurant ID.");
    const payload = {
        name: document.getElementById("add-menu-name").value,
        description: document.getElementById("add-menu-description").value || "Added from frontend",
        price: Number(document.getElementById("add-menu-price").value),
        category: document.getElementById("add-menu-category").value || "Main",
        image_url: document.getElementById("add-menu-image-url").value || "",
        is_available: true,
        add_ons: []
    };
    await apiRequest(`/menu/${restaurantId}/add`, { method: "POST", body: payload, auth: true });
    await loadOwnerMenu();
}

async function updateMenuItem() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("manage-rest-id").value);
    const itemId = Number(document.getElementById("update-item-id").value);
    if (!restaurantId || !itemId) return alert("Enter restaurant ID and item ID.");
    const payload = {};
    const name = document.getElementById("update-menu-name").value;
    const description = document.getElementById("update-menu-description").value;
    const price = document.getElementById("update-menu-price").value;
    const category = document.getElementById("update-menu-category").value;
    const available = document.getElementById("update-menu-available").value;
    if (name) payload.name = name;
    if (description) payload.description = description;
    if (price) payload.price = Number(price);
    if (category) payload.category = category;
    if (available) payload.is_available = available === "true";
    await apiRequest(`/menu/${restaurantId}/${itemId}`, { method: "PATCH", body: payload, auth: true });
    await loadOwnerMenu();
}

async function deleteMenuItem() {
    if (!requireLogin()) return;
    const restaurantId = Number(document.getElementById("manage-rest-id").value);
    const itemId = Number(document.getElementById("delete-item-id").value);
    if (!restaurantId || !itemId) return alert("Enter restaurant ID and item ID.");
    await apiRequest(`/menu/${restaurantId}/${itemId}`, { method: "DELETE", auth: true });
    await loadOwnerMenu();
}

async function viewQueue() {
    if (!requireLogin()) return;
    const data = await apiRequest("/orders/queue", { auth: true });
    renderQueue(Array.isArray(data.pending_orders) ? data.pending_orders : []);
}

async function updateOrderStatus() {
    if (!requireLogin()) return;
    const orderId = Number(document.getElementById("update-order-id").value);
    const newStatus = document.getElementById("update-order-status").value;
    if (!orderId) return alert("Enter order ID.");
    let order = lastQueue.find((item) => item.id === orderId);
    if (!order) {
        const data = await apiRequest("/orders/queue", { auth: true });
        order = (data.pending_orders || []).find((item) => item.id === orderId);
    }
    if (!order) return alert("Order not found in queue.");
    await apiRequest(`/orders/${orderId}/status?new_status=${encodeURIComponent(newStatus)}`, { method: "PATCH", body: order, auth: true });
    await viewQueue();
}

async function updateMultiplier() {
    if (!requireLogin()) return;
    const multiplier = Number(document.getElementById("delivery-fee-multiplier").value);
    if (!multiplier || multiplier <= 0) return alert("Enter a valid multiplier.");
    const data = await apiRequest("/admin/config/update", { method: "POST", body: { delivery_fee_multiplier: multiplier }, auth: true });
    document.getElementById("multiplier-status").innerText = `Updated multiplier to ${data.delivery_fee_multiplier}`;
}

async function loadReportQueue() {
    if (!requireLogin()) return;
    const reports = await apiRequest("/reports/queue", { auth: true });
    renderReports(Array.isArray(reports) ? reports : []);
}

async function handleReport() {
    if (!requireLogin()) return;
    const reportId = document.getElementById("handle-report-id").value;
    const decision = document.getElementById("handle-report-decision").value;
    const notes = document.getElementById("handle-report-notes").value;
    if (!reportId) return alert("Enter report ID.");
    await apiRequest(`/reports/${reportId}/handle?decision=${encodeURIComponent(decision)}&notes=${encodeURIComponent(notes)}`, { method: "PATCH", auth: true });
    await loadReportQueue();
}

async function loadDriverOrders() {
    if (!requireLogin()) return;
    const maxKm = document.getElementById("driver-max-km").value || "10";
    const data = await apiRequest(`/driver/orders?max_km=${encodeURIComponent(maxKm)}`, { auth: true });
    renderDriverOrders(Array.isArray(data) ? data : []);
}

window.useRestaurantFromSearch = function (restaurantId) { useRestaurantId(restaurantId); };
window.useRestaurantFromOwner = function (restaurantId) { useRestaurantId(restaurantId); };
window.useMenuItemId = function (itemId, restaurantId) {
    document.getElementById("fav-item-id").value = itemId;
    document.getElementById("cart-remove-item-id").value = itemId;
    document.getElementById("manage-rest-id").value = restaurantId;
    useRestaurantId(restaurantId);
};
window.useOrderFromList = function (orderId, restaurantId) { useOrderId(orderId, restaurantId); };
window.useQueueOrder = function (orderId) {
    document.getElementById("update-order-id").value = orderId;
    useOrderId(orderId);
};
window.useReportId = function (reportId) { document.getElementById("handle-report-id").value = reportId; };
window.loadRestaurantMenuAction = () => {};
window.loadRestaurantRatingAction = () => {};
window.loadRestaurantReviewsAction = () => {};
window.addToCartAction = () => {};
window.removeFromCartAction = () => {};
window.trackOrderByIdAction = () => {};

document.getElementById("show-register").onclick = (event) => {
    event.preventDefault();
    document.getElementById("register-form-container").style.display = "block";
};

document.getElementById("show-login").onclick = (event) => {
    event.preventDefault();
    document.getElementById("register-form-container").style.display = "none";
};

document.getElementById("btn-fill-admin").onclick = () => {
    document.getElementById("login-email").value = "admin@example.com";
    document.getElementById("login-password").value = "dOyOUkNOWiMaNaDMIN?";
};

document.getElementById("register-form").onsubmit = async (event) => {
    event.preventDefault();
    const payload = {
        name: document.getElementById("reg-name").value,
        email: document.getElementById("reg-email").value,
        password: document.getElementById("reg-password").value,
        phone_number: document.getElementById("reg-phone").value || "000-000-0000",
        address: document.getElementById("reg-address").value || "123 Main St",
        role: document.getElementById("reg-role").value,
        coordinate: { latitude: 49.88, longitude: -119.49 }
    };
    try {
        await apiRequest("/auth/register", { method: "POST", body: payload });
        document.getElementById("auth-error").innerText = "Registration successful. Please login.";
        document.getElementById("register-form-container").style.display = "none";
    } catch (error) {
        document.getElementById("auth-error").innerText = error.message;
    }
};

document.getElementById("login-form").onsubmit = async (event) => {
    event.preventDefault();
    const formData = new URLSearchParams();
    formData.append("username", document.getElementById("login-email").value);
    formData.append("password", document.getElementById("login-password").value);
    try {
        const data = await apiRequest("/auth/login", {
            method: "POST",
            body: formData,
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            json: false
        });
        currentToken = data.access_token;
        await fetchProfile();
    } catch (error) {
        document.getElementById("auth-error").innerText = error.message;
    }
};

document.getElementById("btn-view-profile").onclick = async () => {
    if (!requireLogin()) return;
    const profile = await apiRequest("/auth/me", { auth: true });
    currentUser = profile;
    fillUpdateForm();
};

document.getElementById("btn-logout").onclick = () => {
    currentToken = null;
    currentUser = null;
    menuItemsCache = {}; // Clear the cart cache on logout
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    authSection.style.display = 'block';
    customerDashboard.style.display = 'none';
    ownerDashboard.style.display = 'none';
    adminDashboard.style.display = 'none';
    sharedSection.style.display = 'none';
    logData("Awaiting action...");
};

document.getElementById('btn-update-multiplier').onclick = async () => {
    const multiplierInput = document.getElementById('delivery-fee-multiplier');
    const multiplier = parseFloat(multiplierInput.value);
    const status = document.getElementById('multiplier-status');

    if (Number.isNaN(multiplier) || multiplier <= 0) {
        return alert('Enter a valid multiplier greater than 0');
    }

    try {
        const res = await fetch(`${API_URL}/admin/config/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ delivery_fee_multiplier: multiplier })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed to update multiplier');

        status.textContent = `Updated multiplier to ${data.delivery_fee_multiplier}`;
        logData(data);
    } catch (err) {
        status.textContent = err.message;
        handleError(err);
    }
};
