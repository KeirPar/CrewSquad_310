const API_URL = 'http://localhost:8000';
let currentToken = null;
let currentUser = null;
let menuItemsCache = {}; // Remembers item details to build the cart payload later

// UI Elements
const authSection = document.getElementById('auth-section');
const customerDashboard = document.getElementById('customer-dashboard');
const ownerDashboard = document.getElementById('owner-dashboard');
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

    if (currentUser.role.toUpperCase() === 'OWNER' || currentUser.role === 'Restaurant Owner') {
        ownerDashboard.style.display = 'block';
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
                html += `<li style="margin-bottom: 5px;"><strong>${item.name}</strong> - $${item.price.toFixed(2)}</li>`;
                total += item.price;
            } else {
                html += `<li>Item ID: ${id} (Details not loaded in cache)</li>`;
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
    sharedSection.style.display = 'none';
    logData("Awaiting action...");
};