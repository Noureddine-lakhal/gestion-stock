import tempfile
import os
from database.init_db import create_database
from data.database_manager import DatabaseManager


def setup_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    db_path = tmp.name
    create_database(db_path)
    return db_path


def test_undo_last_exit():
    db_path = setup_temp_db()
    try:
        db = DatabaseManager(db_path)
        conn = db._get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('u1', 'p', 'user'))
        user_id = c.lastrowid
        c.execute("INSERT INTO categories (name) VALUES (?)", ('cat1',))
        cat_id = c.lastrowid
        c.execute("INSERT INTO products (name, category_id, reference_id, quantity, created_by) VALUES (?, ?, ?, ?, ?)", ('prodA', cat_id, None, 10, user_id))
        prod_id = c.lastrowid
        conn.commit()
        conn.close()

        # perform a normal exit
        ok = db.add_stock_exit(prod_id, 4, 'Operator', 'reason', user_id)
        assert ok
        # undo last exit
        undone = db.undo_last_stock_exit(prod_id)
        assert undone
        conn = db._get_connection()
        c = conn.cursor()
        c.execute("SELECT quantity FROM products WHERE id = ?", (prod_id,))
        qty = c.fetchone()[0]
        assert qty == 10
        c.execute("SELECT COUNT(*) FROM stock_history WHERE product_id = ?", (prod_id,))
        count = c.fetchone()[0]
        assert count == 0
        conn.close()
    finally:
        os.unlink(db_path)
