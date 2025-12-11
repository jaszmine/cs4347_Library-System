from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add src folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

app = Flask(__name__)
CORS(app)

try:
    import book_search
    import borrower_management
    import fines
    # import book_loans
    
    print("Loaded your existing Python files:")
    print(f"   - book_search.py")
    print(f"   - borrower_management.py")  
    print(f"   - fines.py")
    
except ImportError as e:
    print(f"Couldn't import: {e}")
    print("Make sure .py files are in ../src/ folder")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Using existing Python files'
    })

@app.route('/api/search', methods=['GET'])
def search():
    """Call book_search.py function"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'success': True, 'books': [], 'message': 'Enter search term'})
    
    try:
        import mysql.connector

        db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password',
            database='Library'
        )
        cursor = db.cursor()
        
        # YOUR EXACT QUERY from book_search.py
        cursor.execute('SELECT books.isbn AS isbn, books.title AS title, '
                       'GROUP_CONCAT(authors.name SEPARATOR \', \'), books.borrowed AS borrowed '
                       'FROM books '
                       'INNER JOIN book_authors ON books.isbn = book_authors.isbn '
                       'INNER JOIN authors ON authors.author_id = book_authors.author_id '
                       'WHERE books.isbn LIKE \'%' + query + '%\' '
                       '    OR books.title LIKE \'%' + query + '%\' '
                       '    OR authors.name LIKE \'%' + query + '%\' '
                       'GROUP BY isbn;')
        
        books = []
        for (isbn, title, name, borrowed) in cursor:
            books.append({
                'isbn': isbn,
                'title': title,
                'authors': name,
                'availability': 'IN' if not borrowed else 'OUT'
            })
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'books': books,
            'total': len(books)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fines', methods=['GET'])
def get_fines():
    try:
        # Use fines.py logic
        import mysql.connector
        from datetime import date
        
        db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password',
            database='Library'
        )
        cursor = db.cursor(dictionary=True)
        
        # YOUR fines.py query for listing fines
        cursor.execute("""
            SELECT br.card_id, br.name AS borrower_name,
                   SUM(f.fine_amt) AS total_fines
            FROM borrowers br
            JOIN book_loans bl ON br.card_id = bl.card_id
            JOIN fines f ON bl.loan_id = f.loan_id
            WHERE f.paid = 0
            GROUP BY br.card_id
            HAVING total_fines > 0
            ORDER BY br.card_id
        """)
        
        fines = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'fines': fines
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fines', methods=['GET'])
def pay_fines():
    card_id = request.args.get('q', '').strip()

    try:
        # Use fines.py logic
        import mysql.connector
        from datetime import date

        db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password',
            database='Library'
        )
        cursor = db.cursor(dictionary=True)

        # YOUR fines.py query for listing fines
        cursor.execute("""
            SELECT loan_id, due_date, date_in
            FROM book_loans
            WHERE (date_in > due_date)
            OR (date_in IS NULL AND due_date < CURDATE())
            """, (card_id,))

        still_out = cursor.fetchall()

        if still_out:
            print("Cannot pay fines — borrower still has books checked out.")
            cursor.close()
            db.close()
            return

        cursor.execute("""
            UPDATE fines f
            JOIN book_loans bl ON f.loan_id = bl.loan_id
            SET f.paid = 1
            WHERE bl.card_id = %s AND f.paid = 0
        """, (card_id,))

        return jsonify({
            'success': True,
            'message': "All fines successfully paid for card_id:",
            'card_id': card_id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Library API - Using YOUR Python Files")
    print("=" * 50)
    print("Your normalized data is already in MySQL!")
    print("This API calls your existing functions.")
    print("\nEndpoints:")
    print("  GET  /api/search?q=...  - Uses book_search.py logic")
    print("  GET  /api/fines         - Uses fines.py logic")
    print("  GET  /api/health        - Health check")
    print("=" * 50)
    app.run(debug=True, port=5001)

# from flask import Flask, jsonify, request
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/')
# def home():
#     return "Library API is running! Go to /api/health"

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "healthy", "message": "API is working"})

# @app.route('/api/search', methods=['GET'])
# def search():
#     query = request.args.get('q', 'test')
#     return jsonify({
#         "success": True,
#         "query": query,
#         "books": [
#             {"isbn": "123", "title": "Test Book 1", "authors": "Author 1", "availability": "IN"},
#             {"isbn": "456", "title": "Test Book 2", "authors": "Author 2", "availability": "OUT"}
#         ]
#     })

# if __name__ == '__main__':
#     print("Flask server starting...")
#     print("Open browser to: http://localhost:5001/api/health")
#     app.run(debug=True, port=5001, host='0.0.0.0')