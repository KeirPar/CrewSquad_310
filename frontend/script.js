const API_URL = 'http://localhost:8000';
let currentToken = null;
let currentUser = null;
let menuItemsCache = {}; // Remembers item details to build the cart payload later

// UI Elements
const authSection = document.getElementById('auth-section');
const customerDashboard = document.getElementById('customer-dashboard');
const ownerDashboard = document.getElementById('owner-dashboard');
const adminDashboard = document.getElementById('admin-dashboard');
const sharedSection = document.getElementById('shared-section');
const dataDisplay = document.getElementById('data-display');

// Display Helpers
function logData(data) {
    dataDisplay.innerText = JSON.stringify(data, null, 2);
}
function handleError(err) {
    logData({ error: err.message });
}

// --- AUTHENTICATION ---
document.getElementById('show-register').onclick = (e) => {
    e.preventDefault();
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('register-form-container').style.display = 'block';
};
document.getElementById('show-login').onclick = (e) => {
    e.preventDefault();
    document.getElementById('register-form-container').style.display = 'none';
    document.getElementById('login-form-container').style.display = 'block';
};

// Register
document.getElementById('register-form').onsubmit = async (e) => {
    e.preventDefault();
    const payload = {
        name: document.getElementById('reg-name').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value,
        phone_number: document.getElementById('reg-phone').value || "000-000-0000",
        address: document.getElementById('reg-address').value || "123 Main St",
        role: document.getElementById('reg-role').value,
        coordinate: { latitude: 49.88, longitude: -119.49 }
    };

    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Registration failed");
        alert("Success! Please log in.");
        document.getElementById('show-login').click();
    } catch (err) {
        document.getElementById('auth-error').innerText = err.message;
    }
};

// Login
document.getElementById('login-form').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('login-email').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Invalid credentials");
        
        currentToken = data.access_token;
        await fetchProfile();
    } catch (err) {
        document.getElementById('auth-error').innerText = err.message;
    }
};

async function fetchProfile() {
    const res = await fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${currentToken}` }
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
        customerDashboard.style.display = 'block';
    }
    logData(currentUser);
}

// --- CUSTOMER DASHBOARD ---

// Search
document.getElementById('btn-search').onclick = async () => {
    const params = new URLSearchParams();
    
    // Grab all values from the UI
    const name = document.getElementById('search-name').value;
    const cuisine = document.getElementById('search-cuisine').value;
    const minRating = document.getElementById('search-min-rating').value;
    const sort = document.getElementById('search-sort').value;
    const limit = document.getElementById('search-limit').value;
    const offset = document.getElementById('search-offset').value;

    // Append to query string ONLY if the user actually provided a value
    if (name) params.append('name', name);
    if (cuisine) params.append('cuisine_type', cuisine);
    if (minRating) params.append('min_rating', minRating);
    if (sort) params.append('sort_by', sort);
    
    // Limit and offset have defaults, but we append them if they exist in the inputs
    if (limit) params.append('limit', limit);
    if (offset) params.append('offset', offset);
    
    try {
        const res = await fetch(`${API_URL}/search/restaurants?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { 
        handleError(err); 
    }
};

// --- INDIVIDUAL FEATURE: FAVORITES & RECENT ORDERS ---

//View Favorites
document.getElementById('btn-view-favorites').onclick = async () => {
    try {
        // IMPORTANT: Adjust this URL to match your exact backend endpoint
        const res = await fetch(`${API_URL}/favorites`, { 
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data); // Shows full response in the raw JSON viewer

        const container = document.getElementById('feature-results');
        if (!res.ok) throw new Error(data.detail || "Failed to fetch favorites");
        if (!data || data.length === 0) return container.innerHTML = "You have no favorite restaurants yet.";

        let html = '<ul style="margin-top: 0; padding-left: 20px;">';
        // Adjust "fav.name" or "fav.restaurant_name" based on what your backend returns
        data.forEach(fav => {
            html += `<li style="margin-bottom: 5px;"><strong>Restaurant ID: ${fav.restaurant_id}</strong></li>`;
        });
        html += '</ul>';
        container.innerHTML = html;

    } catch (err) { handleError(err); }
};

//Add Favorite
document.getElementById('btn-add-favorite').onclick = async () => {
    const restId = parseInt(document.getElementById('add-fav-id').value);
    if (!restId) return alert("Please enter a Restaurant ID to favorite.");

    try {
        // IMPORTANT: Adjust this URL and Method to match your backend
        const res = await fetch(`${API_URL}/favorites/${restId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add favorite");
        
        alert("Restaurant added to favorites!");
        logData(data);
        document.getElementById('btn-view-favorites').click(); // Auto-refresh the list
    } catch (err) { handleError(err); }
};

//View Recent Orders
document.getElementById('btn-view-recent').onclick = async () => {
    try {
        // IMPORTANT: Adjust this URL to match your exact backend endpoint
        const res = await fetch(`${API_URL}/orders/recent`, { 
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const data = await res.json();
        logData(data);

        const container = document.getElementById('feature-results');
        if (!res.ok) throw new Error(data.detail || "Failed to fetch recent orders");
        
        // Handle both possible JSON structures (array or object with a list inside)
        const ordersList = Array.isArray(data) ? data : (data.orders || []);
        if (ordersList.length === 0) return container.innerHTML = "No recent orders found.";

        let html = '<ul style="margin-top: 0; padding-left: 20px;">';
        ordersList.forEach(order => {
            html += `<li style="margin-bottom: 5px;"><strong>Order #${order.id}</strong> - Status: ${order.status} - Total: $${order.total_amount}</li>`;
        });
        html += '</ul>';
        container.innerHTML = html;

    } catch (err) { handleError(err); }
};

// --- MENU BROWSING & CART SYSTEM ---

// 1. Search Menus
document.getElementById('btn-browse-menus').onclick = async () => {
    const nameQuery = document.getElementById('menu-search-name').value.toLowerCase();
    
    try {
        const res = await fetch(`${API_URL}/menu?limit=50&offset=0`);
        const data = await res.json();
        
        let items = data.items || [];
        
        // Frontend filtering if nameQuery exists
        if (nameQuery) {
            items = items.filter(item => item.name.toLowerCase().includes(nameQuery));
        }

        const resultsContainer = document.getElementById('menu-results');
        resultsContainer.innerHTML = ''; 

        if (items.length === 0) return resultsContainer.innerHTML = '<p class="helper-text">No items found.</p>';

        items.forEach(item => {
            menuItemsCache[item.id] = item; // Cache the item for the cart payload!

            const itemDiv = document.createElement('div');
            itemDiv.style.borderBottom = '1px solid #eee';
            itemDiv.style.padding = '10px 0';
            itemDiv.style.display = 'flex';
            itemDiv.style.justifyContent = 'space-between';
            itemDiv.style.alignItems = 'center';

            itemDiv.innerHTML = `
                <div>
                    <strong>${item.name}</strong> - $${item.price.toFixed(2)}<br>
                    <span class="helper-text">Rest ID: ${item.restaurant_id} | ${item.description}</span>
                </div>
                <button class="btn-secondary" style="width: auto; padding: 6px 12px; margin: 0;" onclick="addToCart(${item.id})">Add</button>
            `;
            resultsContainer.appendChild(itemDiv);
        });
        logData(data);
    } catch (err) { handleError(err); }
};

// 2. Add Item to Cart
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
        html += `</ul><hr style="margin: 10px 0;"><strong style="color: #28a745;">Items Subtotal:$${total.toFixed(2)}</strong>`;
        cartContainer.innerHTML = html;

    } catch (err) { handleError(err); }
};

// 4. Checkout / Place Order
document.getElementById('btn-checkout').onclick = async () => {
    try {
        const cartRes = await fetch(`${API_URL}/cart`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
        const cartData = await cartRes.json();
        const cartIds = cartData.cart_items || [];

        if (cartIds.length === 0) return alert("Your cart is empty!");

        const menuItemsForOrder = cartIds.map(id => menuItemsCache[id]).filter(item => item !== undefined);
        
        if (menuItemsForOrder.length !== cartIds.length) {
            return alert("Some items in your cart haven't been loaded. Please hit 'Search Menu' to load the item data before checking out.");
        }

        const payload = {
            user_id: currentUser.id,
            cart: {
                id: Math.floor(Math.random() * 10000), 
                menu_items: menuItemsForOrder
            }
        };

        const res = await fetch(`${API_URL}/orders/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to place order.");
        
        alert("Order Placed Successfully!");
        logData(data);
    } catch (err) { handleError(err); }
};

// --- ORDERS & TRACKING ---

// Get Orders
document.getElementById('btn-my-orders').onclick = async () => {
    try {
        const res = await fetch(`${API_URL}/orders/`, { headers: { 'Authorization': `Bearer ${currentToken}` }});
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-track-order').onclick = async () => {
    const id = document.getElementById('track-order-id').value;
    try {
        const res = await fetch(`${API_URL}/orders/${id}`);
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// Cancel Order
document.getElementById('btn-cancel-order').onclick = async () => {
    const id = parseInt(document.getElementById('track-order-id').value);
    if (!id) return alert("Enter Order ID");

    try {
        const getRes = await fetch(`${API_URL}/orders/`, { headers: { 'Authorization': `Bearer ${currentToken}` }});
        const orders = await getRes.json();
        const fullOrder = Array.isArray(orders) ? orders.find(o => o.id === id) : orders.orders.find(o => o.id === id);
        
        if (!fullOrder) throw new Error("Order full data not found in history");

        const patchRes = await fetch(`${API_URL}/orders/${id}/status?new_status=CANCELLED`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(fullOrder)
        });
        logData(await patchRes.json());
    } catch (err) { handleError(err); }
};

// --- OWNER DASHBOARD ---

// View Queue
document.getElementById('btn-view-queue').onclick = async () => {
    try {
        const res = await fetch(`${API_URL}/orders/queue`, { headers: { 'Authorization': `Bearer ${currentToken}` }});
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// Update Order Status
document.getElementById('btn-update-status').onclick = async () => {
    const id = parseInt(document.getElementById('update-order-id').value);
    const newStatus = document.getElementById('update-order-status').value;
    if (!id) return alert("Enter Order ID");

    try {
        const getRes = await fetch(`${API_URL}/orders/queue`, { headers: { 'Authorization': `Bearer ${currentToken}` }});
        const queueData = await getRes.json();
        const ordersList = Array.isArray(queueData) ? queueData : queueData.pending_orders;
        const fullOrder = ordersList.find(o => o.id === id);

        if (!fullOrder) throw new Error("Order full data not found in pending queue");

        const patchRes = await fetch(`${API_URL}/orders/${id}/status?new_status=${newStatus}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(fullOrder)
        });
        logData(await patchRes.json());
    } catch (err) { handleError(err); }
};

// Add Menu Item
document.getElementById('btn-add-menu').onclick = async () => {
    const restId = document.getElementById('manage-rest-id').value;
    const name = document.getElementById('add-menu-name').value;
    const price = parseFloat(document.getElementById('add-menu-price').value);

    if (!restId || !name || isNaN(price)) return alert("Fill out Restaurant ID, Name, and Price.");

    const payload = {
        name: name,
        description: "Added via Owner UI",
        price: price,
        category: "Main",
        image_url: "",
        is_available: true,
        add_ons: []
    };

    try {
        const res = await fetch(`${API_URL}/menu/${restId}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(payload)
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// Delete Menu Item
document.getElementById('btn-delete-menu').onclick = async () => {
    const restId = document.getElementById('manage-rest-id').value;
    const itemId = document.getElementById('delete-item-id').value;

    if (!restId || !itemId) return alert("Fill out Restaurant ID and Item ID.");

    try {
        const res = await fetch(`${API_URL}/menu/${restId}/${itemId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        if (res.status === 204) logData({ message: "Menu item successfully deleted." });
        else logData(await res.json());
    } catch (err) { handleError(err); }
};
// =====================================================================
// FEAT 7 — PAYMENT (ADDED)
// =====================================================================

document.getElementById('btn-simulate-payment').onclick = async () => {
    const orderId = document.getElementById('simulate-order-id').value;
    if (!orderId) return alert("Enter an Order ID.");
    try {
        const res = await fetch(`${API_URL}/payments/${orderId}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-submit-decision').onclick = async () => {
    const orderId = document.getElementById('decision-order-id').value;
    const decision = document.getElementById('decision-value').value;
    const reason = document.getElementById('decision-reason').value;
    if (!orderId) return alert("Enter an Order ID.");
    const body = { decision };
    if (reason) body.reason = reason;
    try {
        const res = await fetch(`${API_URL}/payments/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(body)
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-check-status').onclick = async () => {
    const orderId = document.getElementById('status-order-id').value;
    if (!orderId) return alert("Enter an Order ID.");
    try {
        const res = await fetch(`${API_URL}/orders/${orderId}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// =====================================================================
// FEAT 8 — NOTIFICATIONS (ADDED)
// =====================================================================

document.getElementById('btn-my-notifications').onclick = async () => {
    if (!currentUser) return alert("Not logged in.");
    try {
        const ordersRes = await fetch(`${API_URL}/orders/`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const orders = await ordersRes.json();
        const orderList = Array.isArray(orders) ? orders : [];
        const allNotifications = [];
        for (const order of orderList) {
            const notifRes = await fetch(`${API_URL}/notifications/order/${order.id}`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            });
            const notifData = await notifRes.json();
            allNotifications.push(...(notifData.notifications || []));
        }
        const recipientRes = await fetch(`${API_URL}/notifications/recipient/${currentUser.id}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const recipientData = await recipientRes.json();
        const recipientNotifs = recipientData.notifications || [];
        const seen = new Set();
        const merged = [...allNotifications, ...recipientNotifs].filter(n => {
            if (seen.has(n.id)) return false;
            seen.add(n.id);
            return true;
        });
        merged.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        logData({ notifications: merged });
    } catch (err) { handleError(err); }
};

document.getElementById('btn-order-notifications').onclick = async () => {
    const orderId = document.getElementById('notif-order-id').value;
    if (!orderId) return alert("Enter an Order ID.");
    try {
        const res = await fetch(`${API_URL}/notifications/order/${orderId}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-order-timeline').onclick = async () => {
    const orderId = document.getElementById('timeline-order-id').value;
    if (!orderId) return alert("Enter an Order ID.");
    if (!currentUser) return alert("Not logged in.");
    try {
        const res = await fetch(`${API_URL}/notifications/order/${orderId}/recipient/${currentUser.id}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// =====================================================================
// M4 — SCHEDULED ORDERS (ADDED)
// =====================================================================

function refreshScheduledOrderDropdowns() {
    const restSelect = document.getElementById('sched-restaurant');
    if (!restSelect) return;
    const restaurants = {};
    Object.values(menuItemsCache).forEach(item => {
        if (!restaurants[item.restaurant_id]) {
            restaurants[item.restaurant_id] = `Restaurant ${item.restaurant_id}`;
        }
    });
    restSelect.innerHTML = '<option value="">Select a Restaurant</option>';
    Object.entries(restaurants).forEach(([id, name]) => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.text = name;
        restSelect.appendChild(opt);
    });
}

document.getElementById('sched-restaurant').onchange = () => {
    const restId = parseInt(document.getElementById('sched-restaurant').value);
    const itemSelect = document.getElementById('sched-item');
    itemSelect.innerHTML = '<option value="">Select a Menu Item</option>';
    if (!restId) return;
    Object.values(menuItemsCache)
        .filter(item => item.restaurant_id === restId)
        .forEach(item => {
            const opt = document.createElement('option');
            opt.value = JSON.stringify({ id: item.id, name: item.name, price: item.price, restaurant_id: item.restaurant_id });
            opt.text = `${item.name} — $${item.price.toFixed(2)}`;
            itemSelect.appendChild(opt);
        });
};

document.getElementById('sched-restaurant').onfocus = async () => {
    if (Object.keys(menuItemsCache).length === 0) {
        try {
            const res = await fetch(`${API_URL}/menu?limit=50&offset=0`);
            const data = await res.json();
            (data.items || []).forEach(item => { menuItemsCache[item.id] = item; });
            refreshScheduledOrderDropdowns();
        } catch (err) { handleError(err); }
    } else {
        refreshScheduledOrderDropdowns();
    }
};

document.getElementById('btn-place-scheduled').onclick = async () => {
    const restId = parseInt(document.getElementById('sched-restaurant').value);
    const itemRaw = document.getElementById('sched-item').value;
    const schedTime = document.getElementById('sched-time').value;
    if (!restId || !itemRaw || !schedTime) {
        return alert("Please select a restaurant, menu item, and scheduled time.");
    }
    const item = JSON.parse(itemRaw);
    const payload = {
        cart: {
            id: Math.floor(Math.random() * 10000),
            menu_items: [{
                id: item.id, name: item.name, description: "Scheduled order item",
                price: item.price, image_url: "", add_ons: [], is_available: true, restaurant_id: restId
            }]
        },
        scheduled_time: new Date(schedTime).toISOString()
    };
    try {
        const res = await fetch(`${API_URL}/scheduled-orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to place scheduled order.");
        const estimatedTime = new Date(data.estimated_delivery_time);
        const formatted = estimatedTime.toLocaleString('en-CA', {
            hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric', timeZoneName: 'short'
        });
        alert(`Scheduled order placed! Estimated delivery by ${formatted}. (${Math.round(data.estimated_delivery_minutes)} minutes from now)`);
        logData(data);
    } catch (err) { handleError(err); }
};

document.getElementById('btn-my-scheduled').onclick = async () => {
    try {
        const res = await fetch(`${API_URL}/scheduled-orders/my-orders/all`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-cancel-scheduled').onclick = async () => {
    const schedId = document.getElementById('cancel-sched-id').value;
    const reason = document.getElementById('cancel-sched-reason').value;
    if (!schedId) return alert("Enter a Scheduled Order ID.");
    const body = {};
    if (reason) body.reason = reason;
    try {
        const res = await fetch(`${API_URL}/scheduled-orders/${schedId}/cancel`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to cancel.");
        logData(data);
    } catch (err) { handleError(err); }
};

document.getElementById('btn-get-scheduled').onclick = async () => {
    const schedId = document.getElementById('get-sched-id').value;
    if (!schedId) return alert("Enter a Scheduled Order ID.");
    try {
        const res = await fetch(`${API_URL}/scheduled-orders/${schedId}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// Owner: Payment decision (ADDED)
document.getElementById('btn-owner-submit-decision').onclick = async () => {
    const orderId = document.getElementById('owner-decision-order-id').value;
    const decision = document.getElementById('owner-decision-value').value;
    const reason = document.getElementById('owner-decision-reason').value;
    if (!orderId) return alert("Enter an Order ID.");
    const body = { decision };
    if (reason) body.reason = reason;
    try {
        const res = await fetch(`${API_URL}/payments/${orderId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(body)
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

// Owner: Notifications (ADDED)
document.getElementById('btn-owner-my-notifications').onclick = async () => {
    if (!currentUser) return alert("Not logged in.");
    try {
        const res = await fetch(`${API_URL}/notifications/recipient/${currentUser.id}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

document.getElementById('btn-owner-timeline').onclick = async () => {
    const orderId = document.getElementById('owner-timeline-order-id').value;
    if (!orderId) return alert("Enter an Order ID.");
    if (!currentUser) return alert("Not logged in.");
    try {
        const res = await fetch(`${API_URL}/notifications/order/${orderId}/recipient/${currentUser.id}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        logData(await res.json());
    } catch (err) { handleError(err); }
};

refreshScheduledOrderDropdowns();

// Logout
document.getElementById('btn-logout').onclick = () => {
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