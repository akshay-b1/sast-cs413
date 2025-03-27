from flask import Flask, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'products.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/init_db')
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY, name TEXT, price REAL)''')
    # Sample data
    products = [
        ('iPhone', 999.99),
        ('Samsung Galaxy', 899.99),
        ('Google Pixel', 799.99),
        ('OnePlus', 699.99)
    ]
    cursor.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)
    conn.commit()
    return "Database initialized with sample products."

# Vulnerable version (testupdate3)
@app.route('/search_vulnerable', methods=['GET', 'POST'])
def search_vulnerable():
    if request.method == 'POST':
        search_term = request.form['search']
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return f"Results: {results}"
        except sqlite3.Error as e:
            return f"An error occurred: {str(e)}"
    return '''
        <h3>Vulnerable Search</h3>
        <form method="post">
        Search products: <input type="text" name="search">
        <input type="submit" value="Search">
        </form>
    '''

# Secure version
@app.route('/search_secure', methods=['GET', 'POST'])
def search_secure():
    if request.method == 'POST':
        search_term = request.form['search']
        conn = get_db()
        cursor = conn.cursor()
        try:
            # prepared statement
            cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{search_term}%',)) 
            results = cursor.fetchall()
            return f"Results: {results}"
        except sqlite3.Error as e:
            return f"An error occurred: {str(e)}"
    return '''
        <h3>Secure Search</h3>
        <form method="post">
        Search products: <input type="text" name="search">
        <input type="submit" value="Search">
        </form>
    '''

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
