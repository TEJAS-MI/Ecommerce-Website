// Function to run when the page loads
window.onload = function() {
    var updateBtns = document.getElementsByClassName('update-cart');

    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function() {
            var productId = this.dataset.product;
            var action = this.dataset.action;
            
            console.log('Product ID:', productId, 'Action:', action);
            console.log('USER:', user);

            if (user === 'AnonymousUser') {
                // *** NEW LOGIC FOR ANONYMOUS USERS ***
                // Call a new function to handle cart locally using localStorage
                addGuestItem(productId, action);
            } else {
                // Existing logic for Authenticated Users (sends data to the server)
                updateuserorder(productId, action);
            }
        });
    }
}

// -------------------------------------------------------------
// NEW FUNCTION FOR ANONYMOUS USERS (Client-Side Cart)
// -------------------------------------------------------------
function addGuestItem(productId, action) {
    console.log('User is not authenticated. Adding item to local storage...');

    // 1. Get the current cart from localStorage, or initialize an empty object
    var cart = JSON.parse(localStorage.getItem('cart')) || {};

    // Ensure the cart exists in localStorage
    if (cart[productId] === undefined) {
        // If product is new, initialize it
        cart[productId] = {'quantity': 0};
    }

    // 2. Update the quantity based on the action
    if (action === 'add') {
        cart[productId]['quantity'] += 1;
    } else if (action === 'remove') {
        cart[productId]['quantity'] -= 1;
    }

    // 3. Clean up (remove item if quantity is zero or less)
    if (cart[productId]['quantity'] <= 0) {
        console.log('Item removed from Guest Cart');
        delete cart[productId];
    }

    // 4. Save the updated cart back to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    
    console.log('Guest Cart:', cart);
    
    // Refresh the page to update the cart count/display
    location.reload();
}


// -------------------------------------------------------------
// EXISTING FUNCTION FOR AUTHENTICATED USERS (Server-Side Cart)
// -------------------------------------------------------------
function updateuserorder(productId, action) {
    console.log('User is authenticated, sending data to server...');
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'content-Type': 'application/json',
            'x-CSRFToken': csrftoken, // Assumes 'csrftoken' is defined globally
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log('Data:', data)
        location.reload()
    });
}