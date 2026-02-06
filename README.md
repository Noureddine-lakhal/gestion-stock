# Gestion de Stock

A desktop application for managing inventory, designed for small businesses. Built with Java Swing.

## Features

- **User Authentication**: Secure login system with password hashing
- **Product Management**: Add, edit, delete, and view products with details
- **Stock Tracking**: Monitor current stock levels and minimum stock thresholds
- **Batch Entries**: Record incoming stock with quantity and pricing
- **Batch Exits**: Record outgoing stock with validation for available quantities
- **Transaction History**: View all stock movements (entries and exits)
- **Reports**: Generate and print stock and transaction reports
- **User Management**: Admin panel to manage users and roles

## Requirements

- Java 11 or higher
- Maven 3.6 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Noureddine-lakhal/gestion-stock.git
cd gestion-stock
```

2. Build the project:
```bash
mvn clean package
```

## Running the Application

Run the application using Maven:
```bash
mvn exec:java -Dexec.mainClass="com.gestionstock.Main"
```

Or run the JAR file:
```bash
java -jar target/gestion-stock-1.0-SNAPSHOT.jar
```

## Default Credentials

- **Username**: admin
- **Password**: admin123

## Usage

### Login
Start the application and log in with your credentials.

### Managing Products
1. Navigate to **Products > Manage Products**
2. Click **Add Product** to create new products
3. Select a product and click **Edit** to modify it
4. Select a product and click **Delete** to remove it

### Recording Stock Entry
1. Navigate to **Transactions > Record Entry**
2. Select a product from the dropdown
3. Enter quantity and unit price
4. Add optional notes
5. Click **Record Entry**

### Recording Stock Exit
1. Navigate to **Transactions > Record Exit**
2. Select a product from the dropdown
3. The available stock will be displayed
4. Enter quantity to exit (cannot exceed available stock)
5. Click **Record Exit**

### Viewing Stock Levels
1. Navigate to **Products > View Stock Levels**
2. Use the "Show Low Stock Only" checkbox to filter products below minimum stock

### Viewing Transactions
1. Navigate to **Transactions > View Transactions**
2. Use the filter dropdown to view all, entry, or exit transactions

### Generating Reports
1. Navigate to **Reports** menu
2. Select **Stock Report** or **Transaction Report**
3. Use **Print** to print the report
4. Use **Export to File** to save as a text file

### Managing Users (Admin Only)
1. Navigate to **Users > Manage Users**
2. Add, edit, or delete users
3. Assign roles (ADMIN or USER)

## Database

The application uses SQLite for data storage. The database file (`gestion_stock.db`) is created automatically in the application directory on first run.

## Technologies Used

- **Java 11**: Programming language
- **Swing**: GUI framework
- **SQLite**: Embedded database
- **BCrypt**: Password hashing
- **Maven**: Build and dependency management

## License

This project is open source and available under the MIT License.