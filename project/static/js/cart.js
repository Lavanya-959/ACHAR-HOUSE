// static/js/cart.js
document.addEventListener('DOMContentLoaded', function () {
    // Quantity Selector Functionality
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        const minusBtn = selector.querySelector('.minus');
        const plusBtn = selector.querySelector('.plus');
        const input = selector.querySelector('.qty-input');

        minusBtn.addEventListener('click', () => {
            let value = parseInt(input.value);
            if (value > 1) {
                input.value = value - 1;
            }
        });

        plusBtn.addEventListener('click', () => {
            let value = parseInt(input.value);
            input.value = value + 1;
        });
    });

    // Add to Cart Functionality
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function () {
            const productCard = this.closest('.product-card');
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const selectedWeight = productCard.querySelector('input[name^="weight"]:checked');
            const price = parseFloat(selectedWeight.dataset.price);
            const quantity = parseInt(productCard.querySelector('.qty-input').value);

            addToCart({
                id: productId,
                name: productName,
                weight: selectedWeight.value,
                price: price,
                quantity: quantity
            });
        });
    });

    function addToCart(item) {
        let cart = JSON.parse(localStorage.getItem('cart')) || [];

        // Check if item already exists in cart
        const existingItem = cart.find(cartItem =>
            cartItem.id === item.id && cartItem.weight === item.weight);

        if (existingItem) {
            existingItem.quantity += item.quantity;
        } else {
            cart.push(item);
        }

        localStorage.setItem('cart', JSON.stringify(cart));

        // Show notification
        showNotification(`${item.quantity} × ${item.name} (${item.weight}g) added to cart!`);

        // Update cart count in header
        updateCartCount();
    }

    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    function updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);

        const cartCountElements = document.querySelectorAll('.cart-count');
        cartCountElements.forEach(el => {
            el.textContent = totalItems;
            el.style.display = totalItems > 0 ? 'inline-block' : 'none';
        });
    }

    // Initialize cart count on page load
    updateCartCount();
});