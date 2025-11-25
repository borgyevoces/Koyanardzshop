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
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.favorite_btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const productId = this.getAttribute('data-product-id');
            const heartIcon = this.querySelector('.heart_favorite')

            fetch(`/toggle_favorite/${productId}/`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'added') {
                    heartIcon.src = "{% static 'images/icon/heart-blue.png' %}";
                } else if (data.status === 'removed') {
                    heartIcon.src = "{% static 'images/icon/heart-black.png' %}";

                    const card = this.closest('.favorites');
                    if (card) card.remove(); 
                }
            })
            .catch(err => console.error('Error toggling favorite:', err));
        });
    });
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