// profile.js - Profile Page Functionality
document.addEventListener('DOMContentLoaded', function() {
    // ============ STATE MANAGEMENT ============
    let currentUser = null;
    let currentLoans = [];
    let finesData = [];
    let readingHistory = [];

    // ============ API CONFIGURATION ============
    const API_BASE_URL = 'http://localhost:5001/api';

    // ============ INITIALIZATION ============
    initProfilePage();

    // ============ INITIALIZATION FUNCTION ============
    async function initProfilePage() {
        console.log('Initializing profile page...');

        // Check if user is logged in (simulated)
        const cardId = getCardIdFromStorage();
        if (!cardId) {
            // Redirect to login/home if no card ID
            alert('Please log in to view your profile');
            window.location.href = 'index.html';
            return;
        }

        // Load all user data
        await loadUserData(cardId);
        await loadCurrentLoans(cardId);
        await loadFinesData(cardId);
        await loadReadingHistory(cardId);

        // Setup event listeners
        setupEventListeners();

        // Show personal info by default
        showSection('personal');
    }

    // ============ DATA LOADING FUNCTIONS ============

    async function loadUserData(cardId) {
        try {
            console.log(`Loading user data for card ID: ${cardId}`);

            // Try to get user from API
            const response = await fetch(`${API_BASE_URL}/borrower/${cardId}`);

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    currentUser = data.borrower;
                    updateUserProfile(currentUser);
                    return;
                }
            }

            // Fallback: Query database directly
            const dbResponse = await fetch(`${API_BASE_URL}/search?q=&limit=1`);
            if (dbResponse.ok) {
                const dbData = await dbResponse.json();
                if (dbData.success && dbData.books.length > 0) {
                    // Create mock user from first book's data
                    currentUser = {
                        card_id: cardId,
                        name: "Library User",
                        email: "user@library.edu",
                        phone: "(555) 123-4567",
                        address: "123 Library Lane",
                        ssn: "123-45-6789",
                        member_since: new Date().toISOString().split('T')[0],
                        total_books: dbData.total || 0
                    };
                    updateUserProfile(currentUser);
                    return;
                }
            }

            // Ultimate fallback: Mock data
            currentUser = createMockUser(cardId);
            updateUserProfile(currentUser);

        } catch (error) {
            console.error('Error loading user data:', error);
            currentUser = createMockUser(cardId);
            updateUserProfile(currentUser);
        }
    }

    async function loadCurrentLoans(cardId) {
        try {
            console.log(`Loading loans for card ID: ${cardId}`);

            // Try API first
            const response = await fetch(`${API_BASE_URL}/loans/${cardId}`);

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    currentLoans = data.loans;
                    renderCurrentLoans();
                    updateLoanStats();
                    return;
                }
            }

            // Fallback: Query book_loans table
            const dbResponse = await fetch(`${API_BASE_URL}/search?q=&limit=10`);
            if (dbResponse.ok) {
                const dbData = await dbResponse.json();
                if (dbData.success) {
                    // Create mock loans from search results
                    currentLoans = dbData.books.slice(0, 3).map((book, index) => ({
                        loan_id: index + 1000,
                        isbn: book.isbn,
                        title: book.title,
                        authors: book.authors,
                        date_out: new Date(Date.now() - (index * 7 * 24 * 60 * 60 * 1000)).toISOString().split('T')[0],
                        due_date: new Date(Date.now() + ((3 - index) * 7 * 24 * 60 * 60 * 1000)).toISOString().split('T')[0],
                        date_in: null,
                        status: index === 0 ? 'overdue' : (index === 1 ? 'due-soon' : 'good')
                    }));
                    renderCurrentLoans();
                    updateLoanStats();
                    return;
                }
            }

            // Ultimate fallback: Mock data
            currentLoans = createMockLoans();
            renderCurrentLoans();
            updateLoanStats();

        } catch (error) {
            console.error('Error loading loans:', error);
            currentLoans = createMockLoans();
            renderCurrentLoans();
            updateLoanStats();
        }
    }

    async function loadFinesData(cardId) {
        try {
            console.log(`Loading fines for card ID: ${cardId}`);

            // Try API first
            const response = await fetch(`${API_BASE_URL}/fines`);

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Filter fines for this user (mock filter since API might return all)
                    finesData = data.fines.filter(fine => fine.card_id == cardId);
                    renderFinesTable();
                    updateFinesStats();
                    return;
                }
            }

            // Fallback: Use fines from current loans
            const overdueLoans = currentLoans.filter(loan => {
                const dueDate = new Date(loan.due_date);
                return dueDate < new Date() && !loan.date_in;
            });

            finesData = overdueLoans.map(loan => ({
                loan_id: loan.loan_id,
                book_title: loan.title,
                isbn: loan.isbn,
                due_date: loan.due_date,
                days_overdue: Math.max(0, Math.floor((new Date() - new Date(loan.due_date)) / (1000 * 60 * 60 * 24))),
                fine_amt: (Math.max(0, Math.floor((new Date() - new Date(loan.due_date)) / (1000 * 60 * 60 * 24))) * 0.25).toFixed(2),
                paid: 0
            }));

            renderFinesTable();
            updateFinesStats();

        } catch (error) {
            console.error('Error loading fines:', error);
            finesData = createMockFines();
            renderFinesTable();
            updateFinesStats();
        }
    }

    async function loadReadingHistory(cardId) {
        try {
            console.log(`Loading reading history for card ID: ${cardId}`);

            // Try API first
            const response = await fetch(`${API_BASE_URL}/history/${cardId}`);

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    readingHistory = data.history;
                    renderReadingHistory();
                    updateHistoryStats();
                    return;
                }
            }

            // Fallback: Use search results as history
            const dbResponse = await fetch(`${API_BASE_URL}/search?q=&limit=20`);
            if (dbResponse.ok) {
                const dbData = await dbResponse.json();
                if (dbData.success) {
                    readingHistory = dbData.books.map((book, index) => ({
                        isbn: book.isbn,
                        title: book.title,
                        authors: book.authors,
                        checkout_date: new Date(Date.now() - (index * 30 * 24 * 60 * 60 * 1000)).toISOString().split('T')[0],
                        return_date: new Date(Date.now() - ((index - 1) * 30 * 24 * 60 * 60 * 1000)).toISOString().split('T')[0],
                        rating: Math.floor(Math.random() * 5) + 1,
                        favorite: index % 4 === 0
                    }));
                    renderReadingHistory();
                    updateHistoryStats();
                    return;
                }
            }

            // Ultimate fallback: Mock data
            readingHistory = createMockHistory();
            renderReadingHistory();
            updateHistoryStats();

        } catch (error) {
            console.error('Error loading history:', error);
            readingHistory = createMockHistory();
            renderReadingHistory();
            updateHistoryStats();
        }
    }

    // ============ RENDERING FUNCTIONS ============

    function updateUserProfile(user) {
        // Update user info display
        document.getElementById('userName').textContent = user.name || 'Library User';
        document.getElementById('cardId').textContent = user.card_id || '1001';
        document.getElementById('fullName').textContent = user.name || 'Library User';
        document.getElementById('cardNumber').textContent = user.card_id || '1001';
        document.getElementById('userSSN').textContent = formatSSN(user.ssn) || '123-45-6789';
        document.getElementById('userEmail').textContent = user.email || 'user@library.edu';
        document.getElementById('userPhone').textContent = user.phone || '(555) 123-4567';
        document.getElementById('userAddress').textContent = user.address || '123 Library Lane';
        document.getElementById('memberSince').textContent = formatDate(user.member_since) || 'January 15, 2024';
        document.getElementById('totalBorrowed').textContent = user.total_books || '24';

        // Update edit form values
        document.getElementById('editName').value = user.name || '';
        document.getElementById('editEmail').value = user.email || '';
        document.getElementById('editPhone').value = user.phone || '';
        document.getElementById('editAddress').value = user.address || '';
    }

    function renderCurrentLoans() {
        const loansList = document.getElementById('currentLoansList');
        const template = document.getElementById('loanTemplate');

        if (!currentLoans || currentLoans.length === 0) {
            loansList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-book-open"></i>
                    <h3>No active loans</h3>
                    <p>You don't have any books checked out at the moment.</p>
                    <a href="index.html" class="btn-primary">Browse Books</a>
                </div>
            `;
            document.getElementById('renewBtn').disabled = true;
            return;
        }

        loansList.innerHTML = '';

        currentLoans.forEach(loan => {
            const clone = template.content.cloneNode(true);
            const loanItem = clone.querySelector('.loan-item');

            // Calculate days left
            const dueDate = new Date(loan.due_date);
            const today = new Date();
            const daysLeft = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

            // Update content
            clone.querySelector('.loan-title').textContent = loan.title;
            clone.querySelector('.loan-author').textContent = `by ${loan.authors || 'Unknown Author'}`;
            clone.querySelector('.loan-isbn').textContent = `ISBN: ${loan.isbn}`;
            clone.querySelector('.date-out').textContent = formatDate(loan.date_out);
            clone.querySelector('.due-date').textContent = formatDate(loan.due_date);

            const daysLeftElement = clone.querySelector('.days-left');
            daysLeftElement.textContent = daysLeft;

            // Style based on days left
            if (daysLeft < 0) {
                daysLeftElement.textContent = `Overdue by ${Math.abs(daysLeft)} days`;
                daysLeftElement.className = 'days-left urgent';
                clone.querySelector('.loan-status').textContent = 'Overdue';
                clone.querySelector('.loan-status').className = 'loan-status overdue';
            } else if (daysLeft <= 3) {
                daysLeftElement.className = 'days-left warning';
                clone.querySelector('.loan-status').textContent = 'Due Soon';
                clone.querySelector('.loan-status').className = 'loan-status due-soon';
            } else {
                daysLeftElement.className = 'days-left good';
                clone.querySelector('.loan-status').textContent = 'Good';
                clone.querySelector('.loan-status').className = 'loan-status good';
            }

            // Add event listeners
            const selectCheckbox = clone.querySelector('.loan-select');
            selectCheckbox.dataset.loanId = loan.loan_id;

            const renewBtn = clone.querySelector('.renew-single-btn');
            renewBtn.addEventListener('click', () => renewSingleLoan(loan.loan_id));

            loansList.appendChild(clone);
        });

        // Enable renew button if there are loans
        document.getElementById('renewBtn').disabled = false;
    }

    function renderFinesTable() {
        const tableBody = document.querySelector('#finesTable tbody');

        if (!finesData || finesData.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #94a3b8;">
                        <i class="fas fa-check-circle" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                        <p>No fines outstanding. Great job!</p>
                    </td>
                </tr>
            `;
            document.getElementById('payFinesBtn').disabled = true;
            return;
        }

        tableBody.innerHTML = '';

        finesData.forEach(fine => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${fine.book_title || 'Unknown Book'}</td>
                <td>${fine.isbn || 'N/A'}</td>
                <td>${formatDate(fine.due_date)}</td>
                <td>${fine.days_overdue || 0}</td>
                <td>$${parseFloat(fine.fine_amt || 0).toFixed(2)}</td>
                <td>
                    <span class="loan-status ${fine.paid ? 'good' : 'overdue'}">
                        ${fine.paid ? 'Paid' : 'Unpaid'}
                    </span>
                </td>
            `;

            tableBody.appendChild(row);
        });

        // Enable pay fines button
        document.getElementById('payFinesBtn').disabled = false;
    }

    function renderReadingHistory() {
        const historyList = document.getElementById('readingHistory');
        const filter = document.getElementById('historyFilter').value;

        if (!readingHistory || readingHistory.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <h3>No reading history</h3>
                    <p>Your reading history will appear here once you check out books.</p>
                    <a href="index.html" class="btn-primary">Start Reading</a>
                </div>
            `;
            return;
        }

        // Filter history based on selection
        let filteredHistory = readingHistory;
        const now = new Date();

        if (filter === 'last-month') {
            const lastMonth = new Date(now.setMonth(now.getMonth() - 1));
            filteredHistory = readingHistory.filter(book =>
                new Date(book.checkout_date) >= lastMonth
            );
        } else if (filter === 'last-year') {
            const lastYear = new Date(now.setFullYear(now.getFullYear() - 1));
            filteredHistory = readingHistory.filter(book =>
                new Date(book.checkout_date) >= lastYear
            );
        } else if (filter === 'favorites') {
            filteredHistory = readingHistory.filter(book => book.favorite);
        }

        historyList.innerHTML = '';

        filteredHistory.forEach(book => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';

            const stars = '★'.repeat(book.rating || 0) + '☆'.repeat(5 - (book.rating || 0));

            historyItem.innerHTML = `
                <div class="history-book">
                    <h4>${book.title}</h4>
                    <p class="history-author">by ${book.authors || 'Unknown Author'}</p>
                    <div class="history-meta">
                        <span>ISBN: ${book.isbn}</span>
                        <span>Read: ${formatDate(book.checkout_date)}</span>
                        <span>Returned: ${formatDate(book.return_date) || 'Not returned'}</span>
                    </div>
                </div>
                <div class="history-rating">
                    <div class="stars">${stars}</div>
                    ${book.favorite ? '<span class="favorite-badge"><i class="fas fa-heart"></i> Favorite</span>' : ''}
                </div>
            `;

            historyList.appendChild(historyItem);
        });
    }

    // ============ STATS UPDATES ============

    function updateLoanStats() {
        const currentCount = currentLoans.filter(loan => !loan.date_in).length;
        const overdueCount = currentLoans.filter(loan => {
            if (loan.date_in) return false;
            const dueDate = new Date(loan.due_date);
            return dueDate < new Date();
        }).length;

        document.getElementById('currentLoans').textContent = currentCount;
        document.getElementById('overdueLoans').textContent = overdueCount;
    }

    function updateFinesStats() {
        const totalFines = finesData.reduce((sum, fine) => sum + parseFloat(fine.fine_amt || 0), 0);
        const unpaidFines = finesData.filter(fine => !fine.paid).reduce((sum, fine) => sum + parseFloat(fine.fine_amt || 0), 0);
        const paidFines = finesData.filter(fine => fine.paid).reduce((sum, fine) => sum + parseFloat(fine.fine_amt || 0), 0);
        const overdueItems = finesData.filter(fine => !fine.paid).length;

        document.getElementById('totalFines').textContent = `$${unpaidFines.toFixed(2)}`;
        document.getElementById('totalFinesAmount').textContent = `$${unpaidFines.toFixed(2)}`;
        document.getElementById('overdueItems').textContent = overdueItems;
        document.getElementById('totalPaid').textContent = `$${paidFines.toFixed(2)}`;

        // Update modal amount
        document.getElementById('modalTotalAmount').textContent = `$${unpaidFines.toFixed(2)}`;
    }

    function updateHistoryStats() {
        const totalBooks = readingHistory.length;
        const thisMonth = readingHistory.filter(book => {
            const checkoutDate = new Date(book.checkout_date);
            const now = new Date();
            return checkoutDate.getMonth() === now.getMonth() &&
                   checkoutDate.getFullYear() === now.getFullYear();
        }).length;
        const favorites = readingHistory.filter(book => book.favorite).length;

        document.getElementById('totalBooksRead').textContent = totalBooks;
        document.getElementById('booksThisMonth').textContent = thisMonth;
        document.getElementById('favoriteBooks').textContent = favorites;
    }

    // ============ EVENT HANDLERS ============

    function setupEventListeners() {
        // Section navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const section = this.dataset.section;

                // Update active states
                document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                // Show selected section
                showSection(section);
            });
        });

        // Edit personal info
        document.getElementById('editPersonalBtn').addEventListener('click', () => {
            document.getElementById('personalEditForm').style.display = 'block';
        });

        document.getElementById('cancelEditBtn').addEventListener('click', () => {
            document.getElementById('personalEditForm').style.display = 'none';
            // Reset form to current values
            updateUserProfile(currentUser);
        });

        document.getElementById('personalForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            // Update user object
            currentUser.name = document.getElementById('editName').value;
            currentUser.email = document.getElementById('editEmail').value;
            currentUser.phone = document.getElementById('editPhone').value;
            currentUser.address = document.getElementById('editAddress').value;

            // Update display
            updateUserProfile(currentUser);

            // Hide form
            document.getElementById('personalEditForm').style.display = 'none';

            // Show success message
            showToast('Personal information updated successfully!', 'success');
        });

        // Renew loans
        document.getElementById('renewBtn').addEventListener('click', renewSelectedLoans);

        // Pay fines
        document.getElementById('payFinesBtn').addEventListener('click', () => {
            document.getElementById('paymentModal').classList.add('active');
        });

        // Payment modal
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('paymentModal').classList.remove('active');
            });
        });

        document.getElementById('confirmPaymentBtn').addEventListener('click', payFines);

        // History filter
        document.getElementById('historyFilter').addEventListener('change', () => {
            renderReadingHistory();
        });

        // Settings
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.theme-option').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const theme = this.dataset.theme;
                document.body.className = theme;
                localStorage.setItem('theme', theme);

                showToast(`Theme changed to ${theme} mode`, 'success');
            });
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.className = savedTheme;
        document.querySelector(`.theme-option[data-theme="${savedTheme}"]`)?.classList.add('active');

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('libraryCardId');
            showToast('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        });
    }

    // ============ ACTION FUNCTIONS ============

    function renewSelectedLoans() {
        const selectedLoans = Array.from(document.querySelectorAll('.loan-select:checked'))
            .map(checkbox => checkbox.dataset.loanId);

        if (selectedLoans.length === 0) {
            showToast('Please select at least one loan to renew', 'error');
            return;
        }

        // Simulate renewal
        selectedLoans.forEach(loanId => {
            const loan = currentLoans.find(l => l.loan_id == loanId);
            if (loan) {
                // Extend due date by 14 days
                const currentDue = new Date(loan.due_date);
                currentDue.setDate(currentDue.getDate() + 14);
                loan.due_date = currentDue.toISOString().split('T')[0];
            }
        });

        renderCurrentLoans();
        updateLoanStats();
        showToast(`Renewed ${selectedLoans.length} book(s) successfully!`, 'success');
    }

    function renewSingleLoan(loanId) {
        const loan = currentLoans.find(l => l.loan_id == loanId);
        if (loan) {
            // Extend due date by 14 days
            const currentDue = new Date(loan.due_date);
            currentDue.setDate(currentDue.getDate() + 14);
            loan.due_date = currentDue.toISOString().split('T')[0];

            renderCurrentLoans();
            updateLoanStats();
            showToast('Book renewed successfully!', 'success');
        }
    }

    function payFines() {
        // Get selected payment method
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;

        // Mark all fines as paid
        finesData.forEach(fine => {
            fine.paid = 1;
        });

        // Update display
        renderFinesTable();
        updateFinesStats();

        // Close modal
        document.getElementById('paymentModal').classList.remove('active');

        // Show success message
        showToast(`Fines paid successfully via ${paymentMethod}!`, 'success');
    }

    // ============ UTILITY FUNCTIONS ============

    function getCardIdFromStorage() {
        // Try to get from localStorage
        const savedId = localStorage.getItem('libraryCardId');
        if (savedId) return savedId;

        // Try to get from URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const urlId = urlParams.get('card_id');
        if (urlId) {
            localStorage.setItem('libraryCardId', urlId);
            return urlId;
        }

        // Default for demo
        return '1001';
    }

    function showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.profile-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const section = document.getElementById(`${sectionId}Section`);
        if (section) {
            section.classList.add('active');
        }
    }

    function formatDate(dateString) {
        if (!dateString) return 'N/A';

        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid Date';

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    function formatSSN(ssn) {
        if (!ssn) return '';
        const clean = ssn.toString().replace(/\D/g, '');
        if (clean.length !== 9) return ssn;
        return `${clean.substr(0, 3)}-${clean.substr(3, 2)}-${clean.substr(5, 4)}`;
    }

    function showToast(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.querySelector('.toast');
        if (existingToast) existingToast.remove();

        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="toast-close">&times;</button>
        `;

        document.body.appendChild(toast);

        // Add close event
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    // Add toast styles dynamically
    const toastStyles = document.createElement('style');
    toastStyles.textContent = `
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 1001;
            animation: slideIn 0.3s ease;
        }

        .toast.success {
            border-left: 4px solid #10b981;
        }

        .toast.error {
            border-left: 4px solid #ef4444;
        }

        .toast.info {
            border-left: 4px solid #3b82f6;
        }

        .toast i {
            font-size: 1.2rem;
        }

        .toast.success i {
            color: #10b981;
        }

        .toast.error i {
            color: #ef4444;
        }

        .toast.info i {
            color: #3b82f6;
        }

        .toast-close {
            background: none;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            font-size: 1.2rem;
            padding: 2px;
            margin-left: 10px;
        }
    `;
    document.head.appendChild(toastStyles);
});