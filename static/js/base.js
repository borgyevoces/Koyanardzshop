/* Product */
    document.addEventListener('DOMContentLoaded', function () {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        const cartButtons = document.querySelectorAll('.add-to-cart-btn');

        cartButtons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();

                const productId = this.dataset.productId;

                fetch(`/add-to-cart/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ quantity: 1 })
                })
                .then(response => response.json())
                .then(data => {
                    alert('Product added to cart!');

                    const cartCountElement = document.getElementById('cart-count');
                    if (cartCountElement) {
                        cartCountElement.textContent = data.cart_count;
                    }

                    const popup = document.getElementById('cart-popup');
                    if (popup) {
                        popup.classList.add('show');
                        setTimeout(() => popup.classList.remove('show'), 2200);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    });

/* Carousel Item */
    const slider = document.querySelector('.checkout_slider');
    const slides = document.querySelectorAll('.checkout_left');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    let currentIndex = 0;

    function updateSlider() {
        slider.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    nextBtn.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
            updateSlider();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlider();
        }
    });

    updateSlider();

/* Favorites */
/* Favorites: event delegation handles clicks on favorite buttons and dropdown remove buttons */
document.addEventListener('click', function (e) {
    // Favorite button on product cards
    const favBtn = e.target.closest && e.target.closest('.favorite_btn');
    if (favBtn) {
        e.preventDefault();
        const productId = favBtn.getAttribute('data-product-id');

        fetch(`/toggle_favorite/${productId}/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'added') {
                favBtn.classList.add('favorited');

                const dropdown = document.getElementById('favoriteDropdown');
                // If server returned HTML for the favorite item, insert it directly
                if (data.html && dropdown) {
                    // avoid duplicate
                    if (!dropdown.querySelector(`.fav-item[data-product-id="${data.product.id}"]`)) {
                        dropdown.insertAdjacentHTML('afterbegin', data.html);
                    }
                } else if (data.product) {
                    // Fallback: build minimal DOM client-side
                    if (dropdown) {
                        if (!dropdown.querySelector(`.fav-item[data-product-id="${data.product.id}"]`)) {
                            const item = document.createElement('div');
                            item.className = 'fav-item';
                            item.setAttribute('data-product-id', data.product.id);
                            item.innerHTML = `
                                <img src="${data.product.img || ''}" alt="${data.product.name}">
                                <div class="fav-details">${data.product.name}</div>
                                <button class="fav-remove-btn" data-product-id="${data.product.id}">Remove</button>
                            `;
                            dropdown.prepend(item);
                        }
                    }
                }
            } else if (data.status === 'removed') {
                favBtn.classList.remove('favorited');

                // Remove from favorites dropdown if present
                const dropdown = document.getElementById('favoriteDropdown');
                if (dropdown) {
                    const card = dropdown.querySelector(`.fav-item[data-product-id="${productId}"]`);
                    if (card) card.remove();
                }

                // If this favorite button lives on the dedicated favorites page, remove its card
                const favCard = favBtn.closest('.favorites');
                if (favCard) {
                    favCard.remove();
                }

                // Also handle product-card layout
                const productCard = favBtn.closest('.product-card');
                if (productCard) {
                    productCard.remove();
                }
            }
        })
        .catch(err => console.error('Error toggling favorite:', err));
    }

    // Remove button inside favorites dropdown
    const removeBtn = e.target.closest && e.target.closest('.fav-remove-btn');
    if (removeBtn) {
        e.preventDefault();
        const productId = removeBtn.getAttribute('data-product-id');

        fetch(`/toggle_favorite/${productId}/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'removed') {
                // remove the dropdown item
                const item = removeBtn.closest('.fav-item');
                if (item) item.remove();

                // also update any open product cards on the page
                const prodBtn = document.querySelector(`.favorite_btn[data-product-id="${productId}"]`);
                if (prodBtn) prodBtn.classList.remove('favorited');
            }
        })
        .catch(err => console.error('Error removing favorite from dropdown:', err));
    }
});


/* Appointment */
document.addEventListener('DOMContentLoaded', function() {
    let calendarEl = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/appointments/json/',
        eventColor: '#0b7285'
    });
    calendar.render();
});

/* AIBOT */
function sendMessage() {
    var userMessage = document.getElementById('ai_input').value;
    var chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += '<div class="message"><strong>You:</strong> ' + userMessage + '</div>';

    fetch('/intent/?message=' + encodeURIComponent(userMessage))
        .then(response => response.json())
        .then(data => {
            chatbox.innerHTML += '<div class="aibot_message"><strong>Bot:</strong> ' + data.reply + '</div>';
            document.getElementById('ai_input').value = '';
        });
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('ai_input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});