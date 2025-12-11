// Main JavaScript

// Config
const CONFIG = {
    API_BASE_URL: 'http://localhost:5001/api',
    DEBOUNCE_DELAY: 300, // milliseconds
    ITEMS_PER_PAGE: 12
};

// State Management
const STATE = {
    currentSearch: '',
    currentFilter: 'all',
    currentPage: 1,
    totalResults: 0,
    totalPages: 1,
    isLoading: false,
    books: []
};

// DOM Elements Cache
const DOM = {
    searchInput: null,
    clearSearchBtn: null,
    filterButtons: null,
    resultsGrid: null,
    resultsCount: null,
    resultsTitle: null,
    loadingElement: null,
    paginationElement: null,
    bookTemplate: null
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
    setupKeyboardShortcuts();
    performInitialSearch();
});

// Cache DOM elements for better performance
function initializeElements() {
    DOM.searchInput = document.getElementById('searchInput');
    DOM.clearSearchBtn = document.getElementById('clearSearch');
    DOM.filterButtons = document.querySelectorAll('.filter-btn');
    DOM.resultsGrid = document.getElementById('resultsGrid');
    DOM.resultsCount = document.getElementById('resultsCount');
    DOM.resultsTitle = document.getElementById('resultsTitle');
    DOM.loadingElement = document.getElementById('loading');
    DOM.bookTemplate = document.getElementById('bookTemplate');
    
    // Create pagination container if it doesn't exist
    if (!document.getElementById('pagination')) {
        const paginationDiv = document.createElement('div');
        paginationDiv.id = 'pagination';
        paginationDiv.className = 'pagination';
        DOM.resultsGrid.parentNode.insertBefore(paginationDiv, DOM.resultsGrid.nextSibling);
        DOM.paginationElement = paginationDiv;
    } else {
        DOM.paginationElement = document.getElementById('pagination');
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Search input with debouncing
    let debounceTimer;
    DOM.searchInput.addEventListener('input', (event) => {
        STATE.currentSearch = event.target.value.trim();
        DOM.clearSearchBtn.style.display = STATE.currentSearch ? 'block' : 'none';
        
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            STATE.currentPage = 1; // Reset to first page on new search
            performSearch();
        }, CONFIG.DEBOUNCE_DELAY);
    });

    // Clear search button
    DOM.clearSearchBtn.addEventListener('click', () => {
        DOM.searchInput.value = '';
        STATE.currentSearch = '';
        DOM.clearSearchBtn.style.display = 'none';
        STATE.currentPage = 1;
        performSearch();
        DOM.searchInput.focus();
    });

    // Filter buttons
    DOM.filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            DOM.filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update state and search
            STATE.currentFilter = btn.dataset.filter;
            STATE.currentPage = 1;
            performSearch();
        });
    });

    // Handle Enter key in search
    DOM.searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            STATE.currentPage = 1;
            performSearch();
        }
    });
}

// Setup keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Ctrl/Cmd + K to focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            DOM.searchInput.focus();
            DOM.searchInput.select();
        }
        
        // Escape to clear search when focused
        if (event.key === 'Escape' && document.activeElement === DOM.searchInput) {
            DOM.searchInput.value = '';
            STATE.currentSearch = '';
            DOM.clearSearchBtn.style.display = 'none';
            performSearch();
        }
        
        // Navigation shortcuts (when not in input)
        if (document.activeElement !== DOM.searchInput) {
            // Right arrow for next page
            if (event.key === 'ArrowRight' && STATE.currentPage < STATE.totalPages) {
                STATE.currentPage++;
                performSearch();
            }
            // Left arrow for previous page
            if (event.key === 'ArrowLeft' && STATE.currentPage > 1) {
                STATE.currentPage--;
                performSearch();
            }
        }
    });
}

// Perform initial search on page load
async function performInitialSearch() {
    try {
        // Check API health first
        const health = await checkApiHealth();
        if (!health.status === 'healthy') {
            showError('API is not responding. Please start the Flask server.');
            return;
        }
        
        // Load initial books
        await performSearch();
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize. Please check your connection.');
    }
}

// Main search function - calls Flask API
async function performSearch() {
    if (STATE.isLoading) return;
    
    setLoading(true);
    
    try {
        // Build query parameters
        const params = new URLSearchParams({
            q: STATE.currentSearch,
            status: STATE.currentFilter === 'all' ? '' : STATE.currentFilter,
            limit: CONFIG.ITEMS_PER_PAGE,
            offset: (STATE.currentPage - 1) * CONFIG.ITEMS_PER_PAGE
        });
        
        // Make API call to Flask backend
        const response = await fetch(`${CONFIG.API_BASE_URL}/search?${params}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update state with results
            STATE.books = data.books || [];
            STATE.totalResults = data.total || 0;
            STATE.totalPages = Math.ceil(STATE.totalResults / CONFIG.ITEMS_PER_PAGE);
            
            // Update UI
            updateResultsDisplay();
            renderBooks();
            renderPagination();
        } else {
            throw new Error(data.error || 'Search failed');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError(`Search failed: ${error.message}. Make sure Flask server is running on port 5000.`);
        
        // Fallback to sample data for demo
        useSampleData();
    } finally {
        setLoading(false);
    }
}

// Check if API is available
async function checkApiHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`, {
            timeout: 5000
        });
        return await response.json();
    } catch (error) {
        return { status: 'unhealthy', message: error.message };
    }
}

// Update results count and title
function updateResultsDisplay() {
    DOM.resultsCount.textContent = STATE.totalResults.toLocaleString();
    
    if (STATE.currentSearch) {
        DOM.resultsTitle.textContent = `Search Results for "${STATE.currentSearch}"`;
    } else if (STATE.currentFilter !== 'all') {
        const filterText = STATE.currentFilter === 'available' ? 'Available' : 'Checked Out';
        DOM.resultsTitle.textContent = `${filterText} Books`;
    } else {
        DOM.resultsTitle.textContent = 'All Books';
    }
}

// Render books to the grid
function renderBooks() {
    // Clear previous results
    DOM.resultsGrid.innerHTML = '';
    
    if (STATE.books.length === 0) {
        showNoResults();
        return;
    }
    
    // Create and append book cards
    STATE.books.forEach(book => {
        const bookCard = createBookCard(book);
        DOM.resultsGrid.appendChild(bookCard);
    });
}

// Create a single book card element
function createBookCard(book) {
    const template = DOM.bookTemplate.content.cloneNode(true);
    const card = template.querySelector('.book-card');
    
    // Set book data
    const titleElement = card.querySelector('.book-title');
    titleElement.textContent = book.title || 'Untitled';
    titleElement.title = book.title || '';
    
    const authorsElement = card.querySelector('.authors-text');
    authorsElement.textContent = book.authors || 'Unknown Author';
    authorsElement.title = book.authors || '';
    
    // Set other details if available
    const details = {
        '.isbn': book.isbn || 'N/A',
        '.year': book.publication_year || 'Unknown',
        '.pages': book.pages ? `${book.pages} pages` : 'Pages unknown',
        '.publisher': book.publisher || 'Unknown',
        '.genre': book.genre || 'Uncategorized'
    };
    
    Object.entries(details).forEach(([selector, value]) => {
        const element = card.querySelector(selector);
        if (element) element.textContent = value;
    });
    
    // Set availability status
    const statusElement = card.querySelector('.book-status');
    const isAvailable = book.availability === 'Available' || book.availability === 'IN';
    
    statusElement.textContent = isAvailable ? 'Available' : 'Checked Out';
    statusElement.className = `book-status ${isAvailable ? 'available' : 'checked-out'}`;
    
    // Set up action buttons
    const viewBtn = card.querySelector('.view-btn');
    const checkoutBtn = card.querySelector('.checkout-btn');
    
    viewBtn.addEventListener('click', () => showBookDetails(book));
    checkoutBtn.addEventListener('click', () => handleCheckout(book));
    
    // Disable checkout if book is not available
    if (!isAvailable) {
        checkoutBtn.disabled = true;
        checkoutBtn.textContent = 'Unavailable';
        checkoutBtn.innerHTML = '<i class="fas fa-times"></i> Unavailable';
    }
    
    return card;
}

// Render pagination controls
function renderPagination() {
    DOM.paginationElement.innerHTML = '';
    
    if (STATE.totalPages <= 1) return;
    
    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'pagination-controls';
    
    // Previous button
    const prevBtn = createPaginationButton('Previous', STATE.currentPage > 1, () => {
        if (STATE.currentPage > 1) {
            STATE.currentPage--;
            performSearch();
        }
    });
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i> Previous';
    paginationDiv.appendChild(prevBtn);
    
    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, STATE.currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(STATE.totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // First page
    if (startPage > 1) {
        const firstBtn = createPaginationButton('1', true, () => {
            STATE.currentPage = 1;
            performSearch();
        });
        paginationDiv.appendChild(firstBtn);
        
        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            paginationDiv.appendChild(ellipsis);
        }
    }
    
    // Numbered pages
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = createPaginationButton(
            i.toString(),
            true,
            () => {
                STATE.currentPage = i;
                performSearch();
            },
            i === STATE.currentPage
        );
        paginationDiv.appendChild(pageBtn);
    }
    
    // Last page
    if (endPage < STATE.totalPages) {
        if (endPage < STATE.totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'pagination-ellipsis';
            ellipsis.textContent = '...';
            paginationDiv.appendChild(ellipsis);
        }
        
        const lastBtn = createPaginationButton(
            STATE.totalPages.toString(),
            true,
            () => {
                STATE.currentPage = STATE.totalPages;
                performSearch();
            }
        );
        paginationDiv.appendChild(lastBtn);
    }
    
    // Next button
    const nextBtn = createPaginationButton('Next', STATE.currentPage < STATE.totalPages, () => {
        if (STATE.currentPage < STATE.totalPages) {
            STATE.currentPage++;
            performSearch();
        }
    });
    nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
    paginationDiv.appendChild(nextBtn);
    
    DOM.paginationElement.appendChild(paginationDiv);
}

// Helper: Create pagination button
function createPaginationButton(text, enabled, onClick, isActive = false) {
    const button = document.createElement('button');
    button.textContent = text;
    button.className = 'pagination-btn';
    
    if (isActive) {
        button.classList.add('active');
    }
    
    if (enabled) {
        button.addEventListener('click', onClick);
    } else {
        button.disabled = true;
    }
    
    return button;
}

// Show book details modal
function showBookDetails(book) {
    const modalContent = `
        <div class="modal-overlay" id="bookModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${book.title || 'Untitled'}</h2>
                    <button class="modal-close" onclick="closeModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="book-detail-row">
                        <strong>Authors:</strong> ${book.authors || 'Unknown'}
                    </div>
                    <div class="book-detail-row">
                        <strong>ISBN:</strong> ${book.isbn || 'N/A'}
                    </div>
                    <div class="book-detail-row">
                        <strong>Publisher:</strong> ${book.publisher || 'Unknown'}
                    </div>
                    <div class="book-detail-row">
                        <strong>Year:</strong> ${book.publication_year || 'Unknown'}
                    </div>
                    <div class="book-detail-row">
                        <strong>Pages:</strong> ${book.pages || 'Unknown'}
                    </div>
                    <div class="book-detail-row">
                        <strong>Genre:</strong> ${book.genre || 'Uncategorized'}
                    </div>
                    <div class="book-detail-row">
                        <strong>Status:</strong> 
                        <span class="status-badge ${book.availability === 'Available' ? 'available' : 'checked-out'}">
                            ${book.availability === 'Available' ? 'Available' : 'Checked Out'}
                        </span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="closeModal()">Close</button>
                    ${book.availability === 'Available' ? 
                        `<button class="btn-primary" onclick="handleCheckout(${JSON.stringify(book)})">
                            <i class="fas fa-shopping-cart"></i> Check Out
                        </button>` : ''
                    }
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalContent;
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Add modal styles if not already present
    addModalStyles();
}

// Handle book checkout
async function handleCheckout(book) {
    // Check if book is available
    const isAvailable = book.availability === 'Available' || book.availability === 'IN';
    if (!isAvailable) {
        showMessage('This book is currently checked out.', 'error');
        return;
    }
    
    // Get borrower ID
    const borrowerId = prompt('Enter Borrower Card ID (numeric):');
    if (!borrowerId || !/^\d+$/.test(borrowerId)) {
        showMessage('Please enter a valid numeric Card ID.', 'error');
        return;
    }
    
    setLoading(true);
    
    try {
        // Call checkout API
        const response = await fetch(`${CONFIG.API_BASE_URL}/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                isbn: book.isbn,
                card_id: parseInt(borrowerId)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(`Successfully checked out "${book.title}" to borrower ${borrowerId}`, 'success');
            
            // Refresh search results
            setTimeout(() => {
                performSearch();
                closeModal();
            }, 1500);
        } else {
            throw new Error(data.error || 'Checkout failed');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showMessage(`Checkout failed: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

// Utility Functions

function setLoading(isLoading) {
    STATE.isLoading = isLoading;
    if (DOM.loadingElement) {
        DOM.loadingElement.style.display = isLoading ? 'block' : 'none';
    }
    DOM.searchInput.disabled = isLoading;
    DOM.filterButtons.forEach(btn => btn.disabled = isLoading);
}

function showNoResults() {
    DOM.resultsGrid.innerHTML = `
        <div class="no-results">
            <i class="fas fa-book-open"></i>
            <h3>No books found</h3>
            <p>${STATE.currentSearch ? 'Try a different search term or filter' : 'Start typing to search for books'}</p>
        </div>
    `;
}

function showError(message) {
    console.error('Error:', message);
    
    // Show error in results area
    DOM.resultsGrid.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Error Loading Books</h3>
            <p>${message}</p>
            <p>Please make sure:</p>
            <ul>
                <li>Flask server is running on port 5000</li>
                <li>Database is properly set up</li>
                <li>Check browser console for details</li>
            </ul>
            <button class="btn-primary" onclick="performSearch()">
                <i class="fas fa-sync"></i> Retry
            </button>
        </div>
    `;
}

function showMessage(message, type = 'info') {
    // Remove any existing messages
    const existingMsg = document.querySelector('.message-toast');
    if (existingMsg) existingMsg.remove();
    
    const toast = document.createElement('div');
    toast.className = `message-toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Fallback to sample data (for demo/testing)
function useSampleData() {
    const sampleBooks = [
        {
            id: 1,
            title: "The Great Gatsby",
            authors: "F. Scott Fitzgerald",
            isbn: "9780743273565",
            publication_year: 1925,
            pages: 180,
            availability: "Available",
            publisher: "Scribner",
            genre: "Fiction"
        },
        {
            id: 2,
            title: "To Kill a Mockingbird",
            authors: "Harper Lee",
            isbn: "9780446310789",
            publication_year: 1960,
            pages: 281,
            availability: "Checked Out",
            publisher: "J.B. Lippincott & Co.",
            genre: "Fiction"
        }
    ];
    
    STATE.books = sampleBooks.filter(book => {
        const matchesSearch = !STATE.currentSearch || 
            book.title.toLowerCase().includes(STATE.currentSearch.toLowerCase()) ||
            book.authors.toLowerCase().includes(STATE.currentSearch.toLowerCase());
        
        const matchesFilter = STATE.currentFilter === 'all' ||
            (STATE.currentFilter === 'available' && book.availability === 'Available') ||
            (STATE.currentFilter === 'checked-out' && book.availability === 'Checked Out');
        
        return matchesSearch && matchesFilter;
    });
    
    STATE.totalResults = STATE.books.length;
    STATE.totalPages = Math.ceil(STATE.totalResults / CONFIG.ITEMS_PER_PAGE);
    
    updateResultsDisplay();
    renderBooks();
    renderPagination();
}

// Modal utility functions (exposed globally)
window.closeModal = function() {
    const modal = document.getElementById('bookModal');
    if (modal) {
        modal.remove();
    }
};

window.handleCheckout = handleCheckout;

// Add modal styles dynamically
function addModalStyles() {
    if (document.getElementById('modal-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'modal-styles';
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .modal-content {
            background: white;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .modal-header {
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-header h2 {
            margin: 0;
            color: #1e293b;
            font-size: 1.5rem;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            color: #64748b;
            cursor: pointer;
            padding: 5px;
        }
        
        .modal-close:hover {
            color: #475569;
        }
        
        .modal-body {
            padding: 20px;
        }
        
        .book-detail-row {
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .book-detail-row:last-child {
            border-bottom: none;
        }
        
        .modal-footer {
            padding: 20px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .message-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 1001;
            animation: slideIn 0.3s ease;
        }
        
        .message-toast.success {
            border-left: 4px solid #10b981;
        }
        
        .message-toast.error {
            border-left: 4px solid #ef4444;
        }
        
        .message-toast i {
            font-size: 1.2rem;
        }
        
        .message-toast.success i {
            color: #10b981;
        }
        
        .message-toast.error i {
            color: #ef4444;
        }
        
        .toast-close {
            background: none;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            padding: 2px;
        }
        
        .pagination {
            margin-top: 30px;
            display: flex;
            justify-content: center;
        }
        
        .pagination-controls {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .pagination-btn {
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            color: #475569;
        }
        
        .pagination-btn:hover:not(:disabled) {
            background: #f8fafc;
            border-color: #94a3b8;
        }
        
        .pagination-btn.active {
            background: #4f46e5;
            border-color: #4f46e5;
            color: white;
        }
        
        .pagination-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pagination-ellipsis {
            padding: 8px 4px;
            color: #94a3b8;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .error-message {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            background: #fef2f2;
            border-radius: 8px;
            border: 1px solid #fee2e2;
        }
        
        .error-message i {
            font-size: 3rem;
            color: #ef4444;
            margin-bottom: 20px;
        }
        
        .error-message ul {
            text-align: left;
            max-width: 400px;
            margin: 20px auto;
            color: #475569;
        }
        
        .error-message li {
            margin-bottom: 8px;
        }
    `;
    
    document.head.appendChild(style);
}

// Make fetch requests timeout
fetch = (function(originalFetch) {
    return function(url, options) {
        const timeout = options?.timeout || 10000;
        
        return Promise.race([
            originalFetch(url, options),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timeout')), timeout)
            )
        ]);
    };
})(fetch);