// static/js/checkout.js
document.addEventListener('DOMContentLoaded', function () {
          // Load cart data into hidden form fields
          const cart = JSON.parse(localStorage.getItem('cart')) || [];
          const totalAmount = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

          document.getElementById('cart-data').value = JSON.stringify(cart);
          document.getElementById('total-amount').value = totalAmount.toFixed(2);

          // Update order summary
          const summaryItems = document.getElementById('summary-items');
          const summaryTotal = document.getElementById('summary-total');

          let html = '';
          cart.forEach(item => {
                    html += `
                  <div class="summary-item">
                      <span>${item.name} (${item.weight}g) × ${item.quantity}</span>
                      <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                  </div>
              `;
          });

          summaryItems.innerHTML = html;
          summaryTotal.textContent = `₹${totalAmount.toFixed(2)}`;

          // Form validation
          const form = document.getElementById('checkout-form');
          if (form) {
                    form.addEventListener('submit', function (e) {
                              if (cart.length === 0) {
                                        e.preventDefault();
                                        alert('Your cart is empty!');
                                        return;
                              }

                              // Additional validation can be added here
                    });
          }
      });