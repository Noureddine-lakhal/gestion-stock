import sqlite3
import os
import sys
from typing import List, Tuple, Optional

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


class DatabaseManager:
    def get_logs_filtered(self, start_date: str = None, end_date: str = None, user_id: int = None) -> List[Tuple[str, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT u.username, l.action, l.timestamp
            FROM logs l
            JOIN users u ON l.user_id = u.id
            WHERE 1=1
        '''
        params = []
        if start_date:
            query += ' AND date(l.timestamp) >= date(?)'
            params.append(start_date)
        if end_date:
            query += ' AND date(l.timestamp) <= date(?)'
            params.append(end_date)
        if user_id:
            query += ' AND l.user_id = ?'
            params.append(user_id)
        query += ' ORDER BY l.timestamp DESC'
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        return logs

    def __init__(self, db_path: Optional[str] = None):
        # Allow overriding DB path for tests
        self.db_path = db_path or DB_PATH

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    # User operations
    def authenticate_user(self, username: str, password: str) -> Optional[Tuple[int, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_users(self) -> List[Tuple[int, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        conn.close()
        return users

    def add_user(self, username: str, password: str, role: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_user(self, user_id: int, username: str, password: str, role: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?", (username, password, role, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, user_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # Category operations
    def get_all_categories(self) -> List[Tuple[int, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cursor.fetchall()
        conn.close()
        return categories

    def add_category(self, name: str) -> Optional[int]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return category_id
        except sqlite3.IntegrityError:
            return None

    # Reference operations
    def get_references_by_category(self, category_id: int) -> List[Tuple[int, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM product_references WHERE category_id = ? ORDER BY name", (category_id,))
        references = cursor.fetchall()
        conn.close()
        return references

    def add_reference(self, name: str, category_id: int) -> Optional[int]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product_references (name, category_id) VALUES (?, ?)", (name, category_id))
            ref_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return ref_id
        except sqlite3.IntegrityError:
            return None

    # Product operations
    def get_inventory(self) -> List[Tuple[int, str, str, str, int, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, c.name, r.name, p.quantity, p.created_at,
                (SELECT sh.date || ' ' || sh.time FROM stock_history sh WHERE sh.product_id = p.id ORDER BY sh.date DESC, sh.time DESC LIMIT 1) as last_exit
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_references r ON p.reference_id = r.id
            WHERE p.quantity > 0
            ORDER BY p.name
        """)
        products = cursor.fetchall()
        conn.close()
        return products

    def get_all_products(self) -> List[Tuple[int, str, str, str, int, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, c.name, r.name, p.quantity, p.created_at,
                (SELECT sh.date || ' ' || sh.time FROM stock_history sh WHERE sh.product_id = p.id ORDER BY sh.date DESC, sh.time DESC LIMIT 1) as last_exit
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_references r ON p.reference_id = r.id
            ORDER BY p.name
        """)
        products = cursor.fetchall()
        conn.close()
        return products

    def get_all_product(self) -> List[Tuple[int, str, str, str, int, str, str]]:
        return self.get_all_products()

    def get_product(self, product_id: int) -> Optional[Tuple[int, str, str, str, int, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, c.name, r.name, p.quantity, p.created_at,
                (SELECT sh.date || ' ' || sh.time FROM stock_history sh WHERE sh.product_id = p.id ORDER BY sh.date DESC, sh.time DESC LIMIT 1) as last_exit
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_references r ON p.reference_id = r.id
            WHERE p.id = ?
        """, (product_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def search_products(self, query: str) -> List[Tuple[int, str, str, str, int, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, c.name, r.name, p.quantity, p.created_at,
                (SELECT sh.date || ' ' || sh.time FROM stock_history sh WHERE sh.product_id = p.id ORDER BY sh.date DESC, sh.time DESC LIMIT 1) as last_exit
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_references r ON p.reference_id = r.id
            WHERE p.name LIKE ?
            ORDER BY p.name
        """, (f'%{query}%',))
        products = cursor.fetchall()
        conn.close()
        return products

    def add_product(self, name: str, category_id: int, reference_id: Optional[int], quantity: int, created_by: int) -> Optional[int]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, category_id, reference_id, quantity, created_by) VALUES (?, ?, ?, ?, ?)", (name, category_id, reference_id, quantity, created_by))
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return product_id
        except sqlite3.IntegrityError:
            return None

    def update_product(self, product_id: int, name: str, category_id: int, reference_id: Optional[int], quantity: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Also update created_at to CURRENT_TIMESTAMP when editing
        cursor.execute("UPDATE products SET name = ?, category_id = ?, reference_id = ?, quantity = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?", (name, category_id, reference_id, quantity, product_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # Statistics
    def get_statistics(self, user_id: int = None, role: str = 'user') -> Tuple[int, int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if role == 'admin':
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM categories")
            total_categories = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT COUNT(*) FROM products WHERE created_by = ?", (user_id,))
            total_products = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM categories")
            total_categories = cursor.fetchone()[0]
        conn.close()
        return total_products, total_categories

    # Logs
    def add_log(self, user_id: int, action: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action))
        conn.commit()
        conn.close()

    def get_logs(self) -> List[Tuple[str, str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, l.action, l.timestamp
            FROM logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
        """)
        logs = cursor.fetchall()
        conn.close()
        return logs

    def get_username_by_id(self, user_id: int) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    # Stock history operations
    def add_stock_exit(self, product_id: int, quantity: int, person: str, reason: str, user_id: Optional[int] = None) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Begin transaction
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False
            current_qty = row[0]
            if quantity <= 0 or quantity > current_qty:
                conn.close()
                return False
            cursor.execute("INSERT INTO stock_history (product_id, quantity, person, reason, user_id) VALUES (?, ?, ?, ?, ?)", (product_id, quantity, person, reason, user_id))
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding stock exit: {e}")
            return False

    def batch_stock_exit(self, items: list, person: str, reason: str, user_id: Optional[int] = None) -> bool:
        """Perform atomic stock exits.
        items: list of tuples (product_id, quantity)
        Returns True if all succeeded, False and no changes if any validation fails or an error occurs.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # validate all
            for product_id, qty in items:
                cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
                if not row:
                    conn.close()
                    return False
                if qty <= 0 or qty > row[0]:
                    conn.close()
                    return False
            # perform all inserts/updates
            for product_id, qty in items:
                cursor.execute("INSERT INTO stock_history (product_id, quantity, person, reason, user_id) VALUES (?, ?, ?, ?, ?)", (product_id, qty, person, reason, user_id))
                cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            print(f"Error in batch_stock_exit: {e}")
            return False

    def undo_last_stock_exit(self, product_id: int) -> bool:
        """Undo the most recent stock exit for the given product by deleting the history entry and restoring the quantity.
        Returns True if undo succeeded, False otherwise."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity FROM stock_history WHERE product_id = ? ORDER BY date DESC, time DESC LIMIT 1", (product_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False
            sh_id, qty = row
            # Restore product quantity
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (qty, product_id))
            # Delete history row
            cursor.execute("DELETE FROM stock_history WHERE id = ?", (sh_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error undoing stock exit: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False

    def get_stock_history(self, product_id: Optional[int] = None) -> List[Tuple[int, str, int, str, str, str, str, Optional[int]]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if product_id:
            cursor.execute("""
                SELECT sh.id, p.name, sh.quantity, sh.person, sh.reason, sh.date, sh.time, sh.user_id
                FROM stock_history sh
                JOIN products p ON sh.product_id = p.id
                WHERE sh.product_id = ?
                ORDER BY sh.date DESC, sh.time DESC
            """, (product_id,))
        else:
            cursor.execute("""
                SELECT sh.id, p.name, sh.quantity, sh.person, sh.reason, sh.date, sh.time, sh.user_id
                FROM stock_history sh
                JOIN products p ON sh.product_id = p.id
                ORDER BY sh.date DESC, sh.time DESC
            """)
        history = cursor.fetchall()
        conn.close()
        return history

    # Backup and restore
    def backup_database(self, backup_path: str):
        import shutil
        shutil.copy(self.db_path, backup_path)

    def restore_database(self, backup_path: str):
        import shutil
        shutil.copy(backup_path, self.db_path)