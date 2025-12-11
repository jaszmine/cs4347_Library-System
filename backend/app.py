#!/usr/bin/env python3
"""
Flask API for Library Management System
Connects React frontend to MySQL database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import sys
import os
import json
from datetime import datetime, date

# Add the parent directory to path so we can import your modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database config
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'password',  # MySQL password
    'database': 'Library',
    'port': 3306
}

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def execute_query(query, params=None, fetch=True):
    """Execute SQL query and return results"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return cursor.lastrowid
        
    except mysql.connector.Error as err:
        print(f"Query error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API and database are working"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/search', methods=['GET'])
def search_books():
    """Enhanced book search with filters"""
    try:
        # Get query parameters
        search_term = request.args.get('q', '').strip()
        status_filter = request.args.get('status', 'all')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = """
        SELECT 
            b.isbn,
            b.title,
            b.borrowed,
            GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
            b.publisher,
            b.publication_year,
            b.pages,
            b.language,
            b.genre,
            COUNT(DISTINCT bl.loan_id) as total_checkouts
        FROM books b
        LEFT JOIN book_authors ba ON b.isbn = ba.isbn
        LEFT JOIN authors a ON ba.author_id = a.author_id
        LEFT JOIN book_loans bl ON b.isbn = bl.isbn
        WHERE 1=1
        """
        
        params = []
        
        # Add search conditions
        if search_term:
            query += """
                AND (
                    b.isbn LIKE %s 
                    OR b.title LIKE %s 
                    OR a.name LIKE %s
                    OR b.publisher LIKE %s
                    OR b.genre LIKE %s
                )
            """
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
        
        # Add status filter
        if status_filter == 'available':
            query += " AND b.borrowed = 0"
        elif status_filter == 'checked-out':
            query += " AND b.borrowed = 1"
        
        # Add group by and ordering
        query += """
        GROUP BY b.isbn, b.title, b.borrowed, b.publisher, 
                 b.publication_year, b.pages, b.language, b.genre
        ORDER BY b.title
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        # Execute query
        books = execute_query(query, params)
        
        if books is None:
            return jsonify({'success': False, 'error': 'Database error'}), 500
        
        # Format results
        formatted_books = []
        for book in books:
            formatted_books.append({
                'isbn': book['isbn'],
                'title': book['title'],
                'authors': book['authors'] or 'Unknown Author',
                'availability': 'Available' if not book['borrowed'] else 'Checked Out',
                'publisher': book['publisher'] or 'Unknown',
                'publication_year': book['publication_year'],
                'pages': book['pages'],
                'language': book['language'] or 'Unknown',
                'genre': book['genre'] or 'Uncategorized',
                'total_checkouts': book['total_checkouts'] or 0
            })
        
        # Get total count for pagination
        count_query = """
        SELECT COUNT(DISTINCT b.isbn) as total
        FROM books b
        LEFT JOIN book_authors ba ON b.isbn = ba.isbn
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE 1=1
        """
        
        count_params = []
        if search_term:
            count_query += """
                AND (
                    b.isbn LIKE %s 
                    OR b.title LIKE %s 
                    OR a.name LIKE %s
                )
            """
            count_params.extend([search_pattern, search_pattern, search_pattern])
        
        if status_filter == 'available':
            count_query += " AND b.borrowed = 0"
        elif status_filter == 'checked-out':
            count_query += " AND b.borrowed = 1"
        
        count_result = execute_query(count_query, count_params)
        total = count_result[0]['total'] if count_result else 0
        
        return jsonify({
            'success': True,
            'books': formatted_books,
            'total': total,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/filters', methods=['GET'])
def get_filter_options():
    """Get available filter options"""
    try:
        # Get unique authors
        authors_query = """
        SELECT DISTINCT a.name 
        FROM authors a 
        JOIN book_authors ba ON a.author_id = ba.author_id
        ORDER BY a.name
        """
        authors_result = execute_query(authors_query)
        authors = [row['name'] for row in authors_result] if authors_result else []
        
        # Get unique genres
        genres_query = "SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL AND genre != '' ORDER BY genre"
        genres_result = execute_query(genres_query)
        genres = [row['genre'] for row in genres_result] if genres_result else []
        
        # Get year range
        year_query = "SELECT MIN(publication_year) as min_year, MAX(publication_year) as max_year FROM books"
        year_result = execute_query(year_query)
        year_range = year_result[0] if year_result else {'min_year': 1900, 'max_year': date.today().year}
        
        return jsonify({
            'success': True,
            'authors': authors,
            'genres': genres,
            'year_range': year_range
        })
        
    except Exception as e:
        print(f"Filters error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/checkout', methods=['POST'])
def checkout_book():
    """Check out a book"""
    try:
        data = request.get_json()
        isbn = data.get('isbn')
        card_id = data.get('card_id')
        
        if not isbn or not card_id:
            return jsonify({'success': False, 'error': 'ISBN and Card ID are required'}), 400
        
        # Check if book exists and is available
        book_query = "SELECT * FROM books WHERE isbn = %s"
        book = execute_query(book_query, (isbn,))
        
        if not book:
            return jsonify({'success': False, 'error': 'Book not found'}), 404
        
        if book[0]['borrowed']:
            return jsonify({'success': False, 'error': 'Book already checked out'}), 400
        
        # Check if borrower exists
        borrower_query = "SELECT * FROM borrowers WHERE card_id = %s"
        borrower = execute_query(borrower_query, (card_id,))
        
        if not borrower:
            return jsonify({'success': False, 'error': 'Borrower not found'}), 404
        
        # Check active loans (max 3)
        loans_query = """
        SELECT COUNT(*) as active_loans 
        FROM book_loans 
        WHERE card_id = %s AND date_in IS NULL
        """
        loans_result = execute_query(loans_query, (card_id,))
        active_loans = loans_result[0]['active_loans'] if loans_result else 0
        
        if active_loans >= 3:
            return jsonify({'success': False, 'error': 'Maximum 3 books already checked out'}), 400
        
        # Check unpaid fines
        fines_query = """
        SELECT SUM(f.fine_amt) as total_fines
        FROM fines f
        JOIN book_loans bl ON f.loan_id = bl.loan_id
        WHERE bl.card_id = %s AND f.paid = 0
        """
        fines_result = execute_query(fines_query, (card_id,))
        unpaid_fines = fines_result[0]['total_fines'] if fines_result and fines_result[0]['total_fines'] else 0
        
        if unpaid_fines > 0:
            return jsonify({'success': False, 'error': f'Unpaid fines: ${unpaid_fines:.2f}'}), 400
        
        # Create loan record
        loan_query = """
        INSERT INTO book_loans (isbn, card_id, date_out, due_date, date_in)
        VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY), NULL)
        """
        loan_id = execute_query(loan_query, (isbn, card_id), fetch=False)
        
        if loan_id:
            # Update book status
            update_query = "UPDATE books SET borrowed = 1 WHERE isbn = %s"
            execute_query(update_query, (isbn,), fetch=False)
            
            return jsonify({
                'success': True,
                'message': 'Book checked out successfully',
                'loan_id': loan_id,
                'due_date': (date.today().replace(day=date.today().day + 14)).isoformat()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create loan record'}), 500
            
    except Exception as e:
        print(f"Checkout error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/checkin', methods=['POST'])
def checkin_book():
    """Check in a book"""
    try:
        data = request.get_json()
        loan_id = data.get('loan_id')
        
        if not loan_id:
            return jsonify({'success': False, 'error': 'Loan ID is required'}), 400
        
        # Get loan details
        loan_query = "SELECT * FROM book_loans WHERE loan_id = %s"
        loan = execute_query(loan_query, (loan_id,))
        
        if not loan:
            return jsonify({'success': False, 'error': 'Loan not found'}), 404
        
        if loan[0]['date_in']:
            return jsonify({'success': False, 'error': 'Book already checked in'}), 400
        
        # Update loan with check-in date
        update_query = "UPDATE book_loans SET date_in = CURDATE() WHERE loan_id = %s"
        execute_query(update_query, (loan_id,), fetch=False)
        
        # Update book status
        book_query = "UPDATE books SET borrowed = 0 WHERE isbn = %s"
        execute_query(book_query, (loan[0]['isbn'],), fetch=False)
        
        # Check if fine needs to be calculated
        due_date = loan[0]['due_date']
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        if date.today() > due_date:
            late_days = (date.today() - due_date).days
            fine_amount = late_days * 0.25
            
            # Insert or update fine
            fine_query = """
            INSERT INTO fines (loan_id, fine_amt, paid) 
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE fine_amt = VALUES(fine_amt)
            """
            execute_query(fine_query, (loan_id, fine_amount), fetch=False)
        
        return jsonify({
            'success': True,
            'message': 'Book checked in successfully'
        })
        
    except Exception as e:
        print(f"Checkin error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/borrowers', methods=['GET'])
def get_borrowers():
    """Get all borrowers"""
    try:
        query = "SELECT * FROM borrowers ORDER BY name"
        borrowers = execute_query(query)
        
        return jsonify({
            'success': True,
            'borrowers': borrowers or []
        })
        
    except Exception as e:
        print(f"Borrowers error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fines', methods=['GET'])
def get_fines():
    """Get fines summary"""
    try:
        query = """
        SELECT 
            b.card_id,
            b.name,
            SUM(f.fine_amt) as total_fines,
            SUM(CASE WHEN f.paid = 0 THEN f.fine_amt ELSE 0 END) as unpaid_fines
        FROM borrowers b
        LEFT JOIN book_loans bl ON b.card_id = bl.card_id
        LEFT JOIN fines f ON bl.loan_id = f.loan_id
        GROUP BY b.card_id, b.name
        HAVING total_fines > 0
        ORDER BY total_fines DESC
        """
        fines = execute_query(query)
        
        return jsonify({
            'success': True,
            'fines': fines or []
        })
        
    except Exception as e:
        print(f"Fines error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get library statistics"""
    try:
        stats = {}
        
        # Total books
        total_books_query = "SELECT COUNT(*) as count FROM books"
        total_books = execute_query(total_books_query)
        stats['total_books'] = total_books[0]['count'] if total_books else 0
        
        # Available books
        available_query = "SELECT COUNT(*) as count FROM books WHERE borrowed = 0"
        available_books = execute_query(available_query)
        stats['available_books'] = available_books[0]['count'] if available_books else 0
        
        # Total borrowers
        borrowers_query = "SELECT COUNT(*) as count FROM borrowers"
        total_borrowers = execute_query(borrowers_query)
        stats['total_borrowers'] = total_borrowers[0]['count'] if total_borrowers else 0
        
        # Active loans
        loans_query = "SELECT COUNT(*) as count FROM book_loans WHERE date_in IS NULL"
        active_loans = execute_query(loans_query)
        stats['active_loans'] = active_loans[0]['count'] if active_loans else 0
        
        # Unpaid fines total
        fines_query = "SELECT SUM(fine_amt) as total FROM fines WHERE paid = 0"
        unpaid_fines = execute_query(fines_query)
        stats['unpaid_fines'] = float(unpaid_fines[0]['total'] or 0) if unpaid_fines else 0
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Library Management System API")
    print("=" * 50)
    print("Starting Flask server...")
    print(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print("API Endpoints:")
    print("  GET  /api/health          - Health check")
    print("  GET  /api/search?q=...    - Search books")
    print("  GET  /api/filters         - Get filter options")
    print("  POST /api/checkout        - Check out book")
    print("  POST /api/checkin         - Check in book")
    print("  GET  /api/borrowers       - Get borrowers")
    print("  GET  /api/fines           - Get fines")
    print("  GET  /api/stats           - Get statistics")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)