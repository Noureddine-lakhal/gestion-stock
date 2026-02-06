from data.database_manager import DatabaseManager
from typing import List, Tuple, Optional

class StockManager:
    def __init__(self):
        self.db = DatabaseManager()

    # User management
    def authenticate(self, username: str, password: str) -> Optional[Tuple[int, str]]:
        result = self.db.authenticate_user(username, password)
        if result:
            user_id, role = result
            self.db.add_log(user_id, f"User '{username}' logged in.")
        return result

    def get_users(self) -> List[Tuple[int, str, str]]:
        return self.db.get_all_users()

    def add_user(self, username: str, password: str, role: str, current_user_id: int) -> bool:
        if self.db.add_user(username, password, role):
            self.db.add_log(current_user_id, f"Added user: {username}")
            return True
        return False

    def update_user(self, user_id: int, username: str, password: str, role: str, current_user_id: int) -> bool:
        if self.db.update_user(user_id, username, password, role):
            self.db.add_log(current_user_id, f"Updated user: {username}")
            return True
        return False

    def delete_user(self, user_id: int, current_user_id: int) -> bool:
        user = next((u for u in self.db.get_all_users() if u[0] == user_id), None)
        if user and self.db.delete_user(user_id):
            self.db.add_log(current_user_id, f"Deleted user: {user[1]}")
            return True
        return False

    # Category and reference management
    def get_categories(self) -> List[Tuple[int, str]]:
        return self.db.get_all_categories()

    def add_category(self, name: str, current_user_id: int) -> Optional[int]:
        category_id = self.db.add_category(name)
        if category_id:
            self.db.add_log(current_user_id, f"Added category: {name}")
        return category_id

    def get_references(self, category_id: int) -> List[Tuple[int, str]]:
        return self.db.get_references_by_category(category_id)

    def add_reference(self, name: str, category_id: int, current_user_id: int) -> Optional[int]:
        ref_id = self.db.add_reference(name, category_id)
        if ref_id:
            self.db.add_log(current_user_id, f"Added reference: {name} to category {category_id}")
        return ref_id

    # Product management
    def get_products(self) -> List[Tuple[int, str, str, str, int]]:
        return self.db.get_all_products()

    def get_product(self, product_id: int) -> Optional[Tuple[int, str, str, str, int, str, str]]:
        return self.db.get_product(product_id)

    def search_products(self, query: str) -> List[Tuple[int, str, str, str, int]]:
        return self.db.search_products(query)

    def add_product(self, name: str, category_id: int, reference_id: Optional[int], quantity: int, current_user_id: int) -> Optional[int]:
        product_id = self.db.add_product(name, category_id, reference_id, quantity, current_user_id)
        if product_id:
            self.db.add_log(current_user_id, f"Added product: {name} with quantity {quantity}")
        return product_id

    def update_product(self, product_id: int, name: str, category_id: int, reference_id: Optional[int], quantity: int, current_user_id: int) -> bool:
        if self.db.update_product(product_id, name, category_id, reference_id, quantity):
            self.db.add_log(current_user_id, f"Updated product: {name} quantity to {quantity}")
            return True
        return False

    def delete_product(self, product_id: int, current_user_id: int) -> bool:
        product = next((p for p in self.db.get_all_products() if p[0] == product_id), None)
        if product and self.db.delete_product(product_id):
            self.db.add_log(current_user_id, f"Deleted product: {product[1]}")
            return True
        return False

    # Statistics
    def get_inventory(self) -> List[Tuple[int, str, str, str, int]]:
        return self.db.get_inventory()

    def get_statistics(self, user_id: int, role: str) -> Tuple[int, int]:
        return self.db.get_statistics(user_id, role)

    # Stock history
    def add_stock_exit(self, product_id: int, quantity: int, person: str, reason: str, current_user_id: int) -> bool:
        if self.db.add_stock_exit(product_id, quantity, person, reason, current_user_id):
            self.db.add_log(current_user_id, f"Stock exit: {quantity} of product {product_id} by {person}")
            return True
        return False

    def batch_stock_exit(self, items: list, person: str, reason: str, current_user_id: int) -> bool:
        """items: list of tuples (product_id, quantity)"""
        if self.db.batch_stock_exit(items, person, reason, current_user_id):
            self.db.add_log(current_user_id, f"Batch stock exit: {items} by {person}")
            return True
        return False

    def undo_last_stock_exit(self, product_id: int, current_user_id: int) -> bool:
        if self.db.undo_last_stock_exit(product_id):
            self.db.add_log(current_user_id, f"Undo last exit (return) for product {product_id}")
            return True
        return False

    def get_stock_history(self, product_id: Optional[int] = None) -> List[Tuple[int, str, int, str, str, str, str, Optional[int]]]:
        return self.db.get_stock_history(product_id)

    def get_username(self, user_id: int) -> Optional[str]:
        return self.db.get_username_by_id(user_id)

    # Logs
    def get_logs(self) -> List[Tuple[str, str, str]]:
        return self.db.get_logs()

    # Backup and restore
    def backup_database(self, path: str):
        self.db.backup_database(path)

    def restore_database(self, path: str):
        self.db.restore_database(path)

    # Dashboard methods
    def get_total_users(self) -> int:
        users = self.db.get_all_users()
        return len(users)

    def get_total_products(self) -> int:
        products = self.db.get_all_products()
        return len(products)

    def get_low_stock_count(self) -> int:
        products = self.db.get_all_products()
        return len([p for p in products if p[4] < 10])  # Assuming qty is index 4

    def get_today_activity(self) -> int:
        import datetime
        today = datetime.date.today().isoformat()
        history = self.db.get_stock_history()
        return len([h for h in history if h[4] == today])  # Assuming date is index 4