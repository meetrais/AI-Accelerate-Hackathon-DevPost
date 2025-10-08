// Global state
let conversationId = generateUUID();
let selectedFlight = null;
let bookingContext = {};

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// ============================================================================
// Chat Functionality with Interactive Elements
// ============================================================================

function addMessage(content, isUser = false, isHTML = false) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    if (isHTML) {
        messageDiv.innerHTML = content;
    } else {
        // Format text with markdown-like styling
        const formatted = formatMessage(content);
        messageDiv.innerHTML = formatted;
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return messageDiv;
}

function formatMessage(text) {
    // Convert markdown-like syntax to HTML
    let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
        .replace(/\n/g, '<br>')                             // Line breaks
        .replace(/• /g, '<br>• ');                          // Bullet points
    
    return formatted;
}

function addFlightCard(flight) {
    const card = `
        <div class="flight-card-inline">
            <div class="flight-header">
                <div class="flight-route">
                    <i class="fas fa-plane-departure"></i>
                    <span class="route-text">${flight.origin} → ${flight.destination}</span>
                </div>
                <div class="flight-price">${flight.price.amount}</div>
            </div>
            <div class="flight-details">
                <div class="detail-item">
                    <i class="fas fa-clock"></i>
                    <span>${formatTime(flight.departure_time)} - ${formatTime(flight.arrival_time)}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-hourglass-half"></i>
                    <span>${formatDuration(flight.duration_minutes)}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-plane"></i>
                    <span>${flight.airline} ${flight.flight_number}</span>
                </div>
            </div>
            <button class="btn-book" onclick="bookFlight('${flight.flight_id}', ${JSON.stringify(flight).replace(/"/g, '&quot;')})">
                <i class="fas fa-check-circle"></i> Book This Flight
            </button>
        </div>
    `;
    return card;
}

function addFlightOptions(flights) {
    let html = '<div class="flight-options">';
    html += '<h3><i class="fas fa-plane"></i> Available Flights</h3>';
    
    flights.forEach((flight, index) => {
        html += addFlightCard(flight);
    });
    
    html += '</div>';
    addMessage(html, false, true);
}

async function sendMessage() {
    console.log('sendMessage called');
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    console.log('Message:', message);
    
    if (!message) {
        console.log('Empty message, returning');
        return;
    }
    
    addMessage(message, true);
    input.value = '';
    
    // Check if user wants to book flights
    const bookingKeywords = ['book flight', 'book a flight', 'find flight', 'search flight', 'fly to', 'flights to'];
    const isBookingIntent = bookingKeywords.some(keyword => message.toLowerCase().includes(keyword));
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = addMessage('', false);
        let fullText = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            fullText += chunk;
            assistantMessage.innerHTML = formatMessage(fullText);
            
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // After AI response, if booking intent detected, show quick action buttons
        if (isBookingIntent) {
            setTimeout(() => {
                showFlightSearchPrompt();
            }, 500);
        }
        
    } catch (error) {
        addMessage('Sorry, I encountered an error. Please try again.', false);
        console.error('Error:', error);
    }
}

function showFlightSearchPrompt() {
    const promptHTML = `
        <div class="quick-actions">
            <p><strong>Let's find you the perfect flight! ✈️</strong></p>
            <div class="action-buttons">
                <button class="btn-action" onclick="showFlightForm()">
                    <i class="fas fa-search"></i> Search Flights
                </button>
                <button class="btn-action-secondary" onclick="askMoreQuestions()">
                    <i class="fas fa-question-circle"></i> I need help deciding
                </button>
            </div>
        </div>
    `;
    addMessage(promptHTML, false, true);
}

function showFlightForm() {
    const formHTML = `
        <div class="inline-form">
            <h4><i class="fas fa-plane-departure"></i> Flight Search</h4>
            <div class="form-grid">
                <div class="form-field">
                    <label>From</label>
                    <input type="text" id="inline-origin" placeholder="e.g., SFO" value="SFO">
                </div>
                <div class="form-field">
                    <label>To</label>
                    <input type="text" id="inline-destination" placeholder="e.g., NRT" value="NRT">
                </div>
                <div class="form-field">
                    <label>Date</label>
                    <input type="date" id="inline-date" value="${getTomorrowDate()}">
                </div>
                <div class="form-field">
                    <label>Passengers</label>
                    <input type="number" id="inline-passengers" value="2" min="1" max="9">
                </div>
            </div>
            <button class="btn-primary" onclick="searchFlightsInline()">
                <i class="fas fa-search"></i> Find Flights
            </button>
        </div>
    `;
    addMessage(formHTML, false, true);
}

function getTomorrowDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
}

async function searchFlightsInline() {
    const origin = document.getElementById('inline-origin').value;
    const destination = document.getElementById('inline-destination').value;
    const date = document.getElementById('inline-date').value;
    const passengers = document.getElementById('inline-passengers').value;
    
    addMessage(`Searching for flights from ${origin} to ${destination} on ${date} for ${passengers} passenger(s)...`, false);
    
    try {
        const response = await fetch('/api/v2/flights/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ origin, destination, date, passengers: parseInt(passengers) })
        });
        
        const data = await response.json();
        
        if (data.flights && data.flights.length > 0) {
            addMessage(`Great news! I found ${data.flights.length} flights for you! 🎉`, false);
            addFlightOptions(data.flights);
        } else {
            addMessage('Sorry, no flights found for those dates. Would you like to try different dates?', false);
        }
    } catch (error) {
        addMessage('Oops! There was an error searching for flights. Please try again.', false);
        console.error('Error:', error);
    }
}

function askMoreQuestions() {
    addMessage("I'd love to help you find the perfect destination! Tell me more about:\n\n• What kind of experience are you looking for? (Beach, mountains, city, adventure)\n• What's your budget range?\n• How long do you want to travel?\n• Any specific interests? (Food, culture, nature, nightlife)", false);
}

// Event listeners - script is at end of body so DOM is ready
console.log('Setting up event listeners...');

const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');

if (!sendBtn) {
    console.error('ERROR: Send button not found!');
} else {
    console.log('✓ Send button found');
    sendBtn.addEventListener('click', () => {
        console.log('>>> Send button clicked');
        sendMessage();
    });
}

if (!userInput) {
    console.error('ERROR: User input not found!');
} else {
    console.log('✓ User input found');
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            console.log('>>> Enter key pressed');
            sendMessage();
        }
    });
}

console.log('✓ Event listeners setup complete');

// ============================================================================
// Booking Functions
// ============================================================================

function bookFlight(flightId, flight) {
    selectedFlight = flight;
    addMessage(`Perfect choice! Let's book the ${flight.airline} flight for ${flight.price.amount}. 🎫`, false);
    
    setTimeout(() => {
        showPaymentForm(flight);
    }, 500);
}

function showPaymentForm(flight) {
    const formHTML = `
        <div class="inline-form payment-form">
            <h4><i class="fas fa-credit-card"></i> Complete Your Booking</h4>
            <div class="booking-summary">
                <p><strong>Flight:</strong> ${flight.airline} ${flight.flight_number}</p>
                <p><strong>Route:</strong> ${flight.origin} → ${flight.destination}</p>
                <p><strong>Total:</strong> <span class="price-highlight">${flight.price.amount}</span></p>
            </div>
            <div class="form-grid">
                <div class="form-field full-width">
                    <label>Passenger Name</label>
                    <input type="text" id="passenger-name" placeholder="John Doe">
                </div>
                <div class="form-field full-width">
                    <label>Email</label>
                    <input type="email" id="passenger-email" placeholder="john@example.com">
                </div>
                <div class="form-field full-width">
                    <label>Card Number</label>
                    <input type="text" id="card-number" placeholder="4242 4242 4242 4242" maxlength="19">
                </div>
                <div class="form-field">
                    <label>Expiry</label>
                    <input type="text" id="card-expiry" placeholder="MM/YY" maxlength="5">
                </div>
                <div class="form-field">
                    <label>CVV</label>
                    <input type="text" id="card-cvv" placeholder="123" maxlength="3">
                </div>
            </div>
            <div class="security-badge">
                <i class="fas fa-shield-alt"></i>
                <span>Secured by AP2 Protocol - Your payment is safe</span>
            </div>
            <button class="btn-primary" onclick="processPaymentInline()">
                <i class="fas fa-lock"></i> Confirm & Pay ${flight.price.amount}
            </button>
        </div>
    `;
    addMessage(formHTML, false, true);
}

async function processPaymentInline() {
    const name = document.getElementById('passenger-name').value;
    const email = document.getElementById('passenger-email').value;
    const cardNumber = document.getElementById('card-number').value;
    
    if (!name || !email || !cardNumber) {
        addMessage('Please fill in all required fields.', false);
        return;
    }
    
    addMessage('Processing your payment... 💳', false);
    
    try {
        const response = await fetch('/api/v2/payment/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                amount: selectedFlight.price.amount,
                currency: 'USD',
                payment_method: {
                    type: 'card',
                    token: 'tok_' + cardNumber.slice(-4),
                    last_four: cardNumber.slice(-4),
                    brand: 'Visa'
                },
                metadata: {
                    flight_id: selectedFlight.flight_id,
                    passenger_name: name,
                    passenger_email: email
                }
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'completed' || data.status === 'COMPLETED') {
            showBookingConfirmation(data);
        } else {
            addMessage('Payment failed. Please try again or use a different card.', false);
        }
    } catch (error) {
        addMessage('Oops! There was an error processing your payment. Please try again.', false);
        console.error('Error:', error);
    }
}

function showBookingConfirmation(payment) {
    const confirmHTML = `
        <div class="confirmation-card">
            <div class="confirmation-header">
                <i class="fas fa-check-circle"></i>
                <h3>Booking Confirmed!</h3>
            </div>
            <div class="confirmation-details">
                <p><strong>Confirmation Code:</strong> <span class="code">${payment.transaction_id || 'CONF' + Math.random().toString(36).substr(2, 9).toUpperCase()}</span></p>
                <p><strong>Flight:</strong> ${selectedFlight.airline} ${selectedFlight.flight_number}</p>
                <p><strong>Route:</strong> ${selectedFlight.origin} → ${selectedFlight.destination}</p>
                <p><strong>Amount Paid:</strong> ${selectedFlight.price.amount}</p>
            </div>
            <div class="confirmation-message">
                <p>🎉 Your booking is confirmed! A confirmation email has been sent to your email address.</p>
                <p>Have a wonderful trip! ✈️</p>
            </div>
        </div>
    `;
    addMessage(confirmHTML, false, true);
    
    setTimeout(() => {
        addMessage("Is there anything else I can help you with? I can help you find hotels, activities, or plan your itinerary!", false);
    }, 1000);
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

// Card formatting
document.addEventListener('input', (e) => {
    if (e.target.id === 'card-number') {
        let value = e.target.value.replace(/\s/g, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formattedValue;
    }
    
    if (e.target.id === 'card-expiry') {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.slice(0, 2) + '/' + value.slice(2, 4);
        }
        e.target.value = value;
    }
});

// ============================================================================
// Legacy Flight Search (keeping for compatibility)
// ============================================================================

const flightSearchForm = document.getElementById('flightSearchForm');
if (flightSearchForm) {
    flightSearchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
    
    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const date = document.getElementById('date').value;
    const passengers = parseInt(document.getElementById('passengers').value);
    
    const resultsDiv = document.getElementById('flightResults');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Searching flights...</p></div>';
    
    try {
        const response = await fetch('/api/v2/flights/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ origin, destination, date, passengers })
        });
        
        const data = await response.json();
        displayFlights(data.flights || []);
    } catch (error) {
        resultsDiv.innerHTML = '<p class="empty-state">Error searching flights. Please try again.</p>';
        console.error('Error:', error);
    }
});

function displayFlights(flights) {
    const resultsDiv = document.getElementById('flightResults');
    
    if (!flights || flights.length === 0) {
        resultsDiv.innerHTML = '<p class="empty-state">No flights found. Try different dates or destinations.</p>';
        return;
    }
    
    resultsDiv.innerHTML = '<h3>Available Flights</h3>';
    
    flights.forEach(flight => {
        const card = document.createElement('div');
        card.className = 'flight-card';
        card.innerHTML = `
            <div class="flight-header">
                <div class="airline">${flight.airline} ${flight.flight_number}</div>
                <div class="price">$${flight.price.amount}</div>
            </div>
            <div class="flight-details">
                <div class="detail-item">
                    <div class="detail-label">Departure</div>
                    <div class="detail-value">${formatTime(flight.departure_time)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Duration</div>
                    <div class="detail-value">${formatDuration(flight.duration_minutes)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Arrival</div>
                    <div class="detail-value">${formatTime(flight.arrival_time)}</div>
                </div>
            </div>
            <div class="flight-footer">
                <div class="flight-info">
                    ${flight.stops === 0 ? 'Direct' : flight.stops + ' stop(s)'} • 
                    ${flight.cabin_class} • 
                    ${flight.seats_available} seats left
                </div>
                <button class="btn-primary" onclick="selectFlight('${flight.flight_id}', ${JSON.stringify(flight).replace(/"/g, '&quot;')})">
                    Book Now
                </button>
            </div>
        `;
        resultsDiv.appendChild(card);
    });
}

} // Close if (flightSearchForm) block

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

// ============================================================================
// Booking and Payment
// ============================================================================

function selectFlight(flightId, flight) {
    selectedFlight = flight;
    
    const modal = document.getElementById('paymentModal');
    const selectedDiv = document.getElementById('selectedFlight');
    
    selectedDiv.innerHTML = `
        <h4>${flight.airline} ${flight.flight_number}</h4>
        <p>${flight.origin} → ${flight.destination}</p>
        <p>${formatTime(flight.departure_time)} - ${formatTime(flight.arrival_time)}</p>
        <p><strong>$${flight.price.amount}</strong></p>
    `;
    
    document.getElementById('totalAmount').textContent = `$${flight.price.amount}`;
    
    modal.classList.add('show');
}

// Close modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('paymentModal').classList.remove('show');
});

// Payment form
document.getElementById('paymentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const passengerName = document.getElementById('passengerName').value;
    const passengerEmail = document.getElementById('passengerEmail').value;
    const cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;
    
    try {
        // Process payment
        const paymentResponse = await fetch('/api/v2/payment/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                amount: selectedFlight.price.amount,
                currency: 'USD',
                payment_method: {
                    type: 'card',
                    token: 'tok_' + cardNumber.slice(-4),
                    last_four: cardNumber.slice(-4),
                    brand: 'Visa'
                },
                metadata: {
                    flight_id: selectedFlight.flight_id,
                    passenger_name: passengerName,
                    passenger_email: passengerEmail
                }
            })
        });
        
        const paymentData = await paymentResponse.json();
        
        if (paymentData.status === 'completed' || paymentData.status === 'COMPLETED') {
            // Show success
            showSuccess(selectedFlight, paymentData);
        } else {
            alert('Payment failed. Please try again.');
        }
    } catch (error) {
        alert('Error processing payment. Please try again.');
        console.error('Error:', error);
    } finally {
        submitBtn.textContent = 'Pay Now';
        submitBtn.disabled = false;
    }
});

function showSuccess(flight, payment) {
    document.getElementById('paymentModal').classList.remove('show');
    
    const successModal = document.getElementById('successModal');
    const detailsDiv = document.getElementById('confirmationDetails');
    
    detailsDiv.innerHTML = `
        <p><strong>Booking Reference:</strong> ${payment.transaction_id || 'CONF' + Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
        <p><strong>Flight:</strong> ${flight.airline} ${flight.flight_number}</p>
        <p><strong>Route:</strong> ${flight.origin} → ${flight.destination}</p>
        <p><strong>Amount Paid:</strong> $${flight.price.amount}</p>
        <p style="margin-top: 20px;">Confirmation email sent!</p>
    `;
    
    successModal.classList.add('show');
    
    // Reset form
    document.getElementById('paymentForm').reset();
}

function closeSuccessModal() {
    document.getElementById('successModal').classList.remove('show');
    // Switch to bookings tab
    document.querySelector('[data-tab="bookings"]').click();
}

// ============================================================================
// Bookings Management
// ============================================================================

async function loadBookings() {
    const listDiv = document.getElementById('bookingsList');
    listDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading bookings...</p></div>';
    
    try {
        const response = await fetch('/api/v2/bookings?user_id=demo_user');
        const data = await response.json();
        
        if (data.bookings && data.bookings.length > 0) {
            displayBookings(data.bookings);
        } else {
            listDiv.innerHTML = '<p class="empty-state">No bookings yet. Start by searching for flights!</p>';
        }
    } catch (error) {
        listDiv.innerHTML = '<p class="empty-state">Error loading bookings.</p>';
        console.error('Error:', error);
    }
}

function displayBookings(bookings) {
    const listDiv = document.getElementById('bookingsList');
    listDiv.innerHTML = '';
    
    bookings.forEach(booking => {
        const card = document.createElement('div');
        card.className = 'booking-card';
        card.innerHTML = `
            <span class="booking-status status-${booking.status}">${booking.status.toUpperCase()}</span>
            <h4>${booking.type.toUpperCase()} Booking</h4>
            <p><strong>Confirmation:</strong> ${booking.confirmation_number || 'Pending'}</p>
            <p><strong>Amount:</strong> $${booking.amount} ${booking.currency}</p>
            <p><strong>Date:</strong> ${new Date(booking.created_at).toLocaleDateString()}</p>
        `;
        listDiv.appendChild(card);
    });
}

// Card formatting - handled via event delegation since elements are created dynamically
document.addEventListener('input', (e) => {
    if (e.target.id === 'card-number') {
        let value = e.target.value.replace(/\s/g, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formattedValue;
    }
    
    if (e.target.id === 'card-expiry') {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.slice(0, 2) + '/' + value.slice(2, 4);
        }
        e.target.value = value;
    }
});

// Welcome message
window.addEventListener('load', () => {
    const welcomeHTML = `
        <div class="welcome-message">
            <h2>👋 Welcome to Your AI Travel Assistant!</h2>
            <p>I'm here to help you plan and book your perfect trip. I can:</p>
            <ul>
                <li>✈️ Search and book flights</li>
                <li>🏨 Find accommodations</li>
                <li>🗺️ Suggest destinations</li>
                <li>📅 Plan your itinerary</li>
            </ul>
            <p><strong>Just tell me where you'd like to go, and I'll take care of the rest!</strong></p>
        </div>
    `;
    addMessage(welcomeHTML, false, true);
    
    setTimeout(() => {
        addMessage("So, where would you like to go? 🌍", false);
    }, 500);
});
