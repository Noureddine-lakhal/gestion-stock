import sqlite3
import os
import sys

# Move DB to appdata for better hiding
if sys.platform == 'win32':
    appdata = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
    db_dir = os.path.join(appdata, 'GestionStock')
else:
    db_dir = os.path.join(os.path.expanduser('~'), '.gestion_stock')

os.makedirs(db_dir, exist_ok=True)
DB_PATH = os.path.join(db_dir, 'stock.db')

# Hide the directory on Windows
if sys.platform == 'win32' and getattr(sys, 'frozen', False):
    try:
        import ctypes
        ctypes.windll.kernel32.SetFileAttributesW(db_dir, 2)  # FILE_ATTRIBUTE_HIDDEN
    except:
        pass

def create_database(db_path: str = None):
    """Create or migrate database. If db_path is provided, use it instead of default DB_PATH."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # References table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    ''')

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            reference_id INTEGER,
            quantity INTEGER DEFAULT 0,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
            FOREIGN KEY (reference_id) REFERENCES product_references (id) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # Add quantity column if not exists (for migration)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN quantity INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Robust migration for created_at column
    try:
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'created_at' not in columns:
            # 1. Create new table with correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    reference_id INTEGER,
                    quantity INTEGER DEFAULT 0,
                    created_by INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
                    FOREIGN KEY (reference_id) REFERENCES product_references (id) ON DELETE SET NULL,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            # 2. Copy data (set created_at to CURRENT_TIMESTAMP for all rows)
            cursor.execute('''
                INSERT INTO products_new (id, name, category_id, reference_id, quantity, created_by)
                SELECT id, name, category_id, reference_id, quantity, created_by FROM products
            ''')
            # 3. Drop old table
            cursor.execute('DROP TABLE products')
            # 4. Rename new table
            cursor.execute('ALTER TABLE products_new RENAME TO products')
            conn.commit()
    except Exception as e:
        print("[DB MIGRATION] Could not migrate products table for created_at:", e)

    # Add created_by column if not exists (for migration)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN created_by INTEGER NOT NULL DEFAULT 1')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Stock history table for exits (includes user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            person TEXT NOT NULL,
            reason TEXT NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            time TIME DEFAULT CURRENT_TIME,
            user_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration step: ensure user_id column exists in older DBs
    try:
        cursor.execute('ALTER TABLE stock_history ADD COLUMN user_id INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Insert default admin user
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database created successfully.")