// ===== MOBILE NAV TOGGLE =====
const navToggle = document.getElementById('navToggle');
const navLinks = document.querySelector('.nav-links');
if (navToggle) {
    navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
}

// ===== AUTO DISMISS ALERTS =====
document.querySelectorAll('.alert').forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) closeBtn.addEventListener('click', () => alert.remove());
    setTimeout(() => { if (alert.parentNode) alert.remove(); }, 5000);
});

// ===== SET MIN DATE ON DATE INPUTS =====
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    const checkIn = document.querySelector('input[name="check_in"]');
    const checkOut = document.querySelector('input[name="check_out"]');

    if (checkIn) {
        checkIn.min = today;
        checkIn.addEventListener('change', () => {
            if (checkOut) {
                checkOut.min = checkIn.value;
                if (checkOut.value && checkOut.value <= checkIn.value) {
                    // Advance check-out by 1 day
                    const d = new Date(checkIn.value);
                    d.setDate(d.getDate() + 1);
                    checkOut.value = d.toISOString().split('T')[0];
                }
            }
        });
    }
    if (checkOut) checkOut.min = today;

    // Price calculator on booking page
    const priceEl = document.querySelector('.room-price');
    if (priceEl && checkIn && checkOut) {
        function updateTotal() {
            if (!checkIn.value || !checkOut.value) return;
            const nights = Math.max(0, (new Date(checkOut.value) - new Date(checkIn.value)) / 86400000);
            const priceText = priceEl.textContent.replace(/[^\d]/g, '');
            const price = parseInt(priceText);
            if (nights > 0 && price) {
                let totalEl = document.getElementById('total-display');
                if (!totalEl) {
                    totalEl = document.createElement('div');
                    totalEl.id = 'total-display';
                    totalEl.style.cssText = 'background:#fff3cd;border-radius:8px;padding:0.75rem;margin-top:1rem;font-weight:700;color:#856404;';
                    priceEl.closest('.booking-summary-card').appendChild(totalEl);
                }
                totalEl.innerHTML = `<i class="fas fa-calculator"></i> ${nights} night(s) × ৳${price.toLocaleString()} = <strong>৳${(nights * price).toLocaleString()}</strong>`;
            }
        }
        checkIn.addEventListener('change', updateTotal);
        checkOut.addEventListener('change', updateTotal);
    }
});

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
});

// ===== TABLE ROW HOVER EFFECT =====
document.querySelectorAll('.data-table tbody tr').forEach(row => {
    row.style.cursor = 'default';
    row.addEventListener('mouseenter', () => row.style.background = '#fafafa');
    row.addEventListener('mouseleave', () => row.style.background = '');
});

// ===== CONFIRM DELETE PROMPTS =====
document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
        if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
});

console.log('🏨 LuxStay Hotel Management System — Loaded');
