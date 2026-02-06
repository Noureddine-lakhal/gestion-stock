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


def test_batch_exit_success():
    db_path = setup_temp_db()
    try:
        db = DatabaseManager(db_path)
        # prepare data: add a user, category, product
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

        # perform batch exit
        items = [(prod_id, 3)]
        ok = db.batch_stock_exit(items, 'Operator', 'For test', user_id)
        assert ok

        # Verify product quantity decreased
        conn = db._get_connection()
        c = conn.cursor()
        c.execute("SELECT quantity FROM products WHERE id = ?", (prod_id,))
        qty = c.fetchone()[0]
        assert qty == 7
        # Verify stock_history
        c.execute("SELECT quantity, person, reason, user_id FROM stock_history WHERE product_id = ?", (prod_id,))
        row = c.fetchone()
        assert row[0] == 3
        assert row[1] == 'Operator'
        assert row[2] == 'For test'
        assert row[3] == user_id
        conn.close()
    finally:
        os.unlink(db_path)


def test_batch_exit_insufficient():
    db_path = setup_temp_db()
    try:
        db = DatabaseManager(db_path)
        conn = db._get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('u1', 'p', 'user'))
        user_id = c.lastrowid
        c.execute("INSERT INTO categories (name) VALUES (?)", ('cat1',))
        cat_id = c.lastrowid
        c.execute("INSERT INTO products (name, category_id, reference_id, quantity, created_by) VALUES (?, ?, ?, ?, ?)", ('prodA', cat_id, None, 2, user_id))
        prod_id = c.lastrowid
        conn.commit()
        conn.close()

        items = [(prod_id, 5)]
        ok = db.batch_stock_exit(items, 'Operator', 'For test', user_id)
        assert not ok

        # verify no change
        conn = db._get_connection()
        c = conn.cursor()
        c.execute("SELECT quantity FROM products WHERE id = ?", (prod_id,))
        qty = c.fetchone()[0]
        assert qty == 2
        c.execute("SELECT COUNT(*) FROM stock_history WHERE product_id = ?", (prod_id,))
        count = c.fetchone()[0]
        assert count == 0
        conn.close()
    finally:
        os.unlink(db_path)
