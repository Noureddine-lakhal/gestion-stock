# Gestion de Stock - Features Documentation

## Core Features

### 1. User Authentication & Authorization
- **Secure Login System**: BCrypt-based password hashing for enhanced security
- **Role-Based Access Control**: 
  - ADMIN: Full access to all features including user management
  - USER: Access to product and transaction management
- **Session Management**: Track logged-in users throughout the application
- **Default Admin Account**: Pre-configured admin user (admin/admin123)

### 2. Product Management
- **CRUD Operations**: Create, Read, Update, and Delete products
- **Product Information**:
  - Unique product code
  - Product name and description
  - Category classification
  - Unit price
  - Current stock level
  - Minimum stock threshold
- **Stock Level Monitoring**: Automatic low stock alerts
- **Product Search & Filtering**: Easy-to-use table interface

### 3. Stock Entry Management
- **Record Incoming Stock**: 
  - Select product from dropdown
  - Enter quantity received
  - Specify unit price
  - Add optional notes
- **Automatic Stock Updates**: Current stock automatically increases
- **Transaction Logging**: All entries are recorded with timestamp and user

### 4. Stock Exit Management
- **Record Outgoing Stock**:
  - Select product from dropdown
  - View available stock before exit
  - Enter quantity to exit
  - Specify unit price
  - Add optional notes
- **Stock Validation**: Prevents exits exceeding available stock
- **Automatic Stock Updates**: Current stock automatically decreases
- **Transaction Logging**: All exits are recorded with timestamp and user

### 5. Transaction History
- **Complete Audit Trail**: View all stock movements
- **Filter Options**:
  - All transactions
  - Entry transactions only
  - Exit transactions only
- **Transaction Details**:
  - Date and time
  - Product name
  - Transaction type (ENTRY/EXIT)
  - Quantity
  - Unit price
  - Total value
  - User who performed the transaction

### 6. Stock Level Tracking
- **Real-time Stock Levels**: View current stock for all products
- **Low Stock Alerts**: Highlight products below minimum threshold
- **Filter Options**:
  - View all products
  - View low stock items only
- **Status Indicators**: Visual cues for stock status

### 7. Report Generation & Printing
- **Stock Report**:
  - Current stock levels for all products
  - Minimum stock thresholds
  - Low stock indicators
  - Category information
- **Transaction Report**:
  - Complete transaction history
  - Date, product, type, quantity details
  - Total value calculations
- **Report Actions**:
  - View in application
  - Print directly from application
  - Export to text file

### 8. User Management (Admin Only)
- **User CRUD Operations**: Create, view, edit, and delete users
- **User Information**:
  - Username (unique)
  - Password (securely hashed)
  - Role (ADMIN or USER)
  - Active status
- **User Activation/Deactivation**: Enable or disable user accounts

## Technical Features

### Database
- **SQLite**: Lightweight, embedded database
- **Automatic Schema Creation**: Database tables created on first run
- **Data Integrity**: Foreign key constraints and unique constraints
- **Transaction Support**: ACID-compliant operations

### Security
- **Password Encryption**: BCrypt hashing with salt
- **SQL Injection Prevention**: Prepared statements for all queries
- **Session Management**: Secure user session handling
- **Role-Based Permissions**: Access control based on user roles

### User Interface
- **Swing-Based GUI**: Native Java desktop interface
- **Responsive Design**: Adapts to system look and feel
- **Menu-Driven Navigation**: Easy access to all features
- **Dashboard View**: Quick access to common operations
- **Table Views**: Sortable, scrollable data displays
- **Dialog Forms**: User-friendly data entry

### Architecture
- **MVC Pattern**: Separation of concerns
  - Model: Data classes (User, Product, Transaction)
  - DAO: Database access layer
  - Service: Business logic layer
  - UI: Presentation layer
- **Modular Design**: Easy to extend and maintain
- **Exception Handling**: Comprehensive error handling and user feedback

## Usage Scenarios

### Scenario 1: Daily Stock Entry
1. Login to application
2. Navigate to Transactions > Record Entry
3. Select product from dropdown
4. Enter quantity and price
5. Add notes (supplier, invoice number, etc.)
6. Click "Record Entry"

### Scenario 2: Processing Customer Orders
1. Navigate to Transactions > Record Exit
2. Select product
3. View available stock
4. Enter quantity to ship
5. Add order notes
6. Click "Record Exit"

### Scenario 3: End-of-Day Reporting
1. Navigate to Reports > Stock Report
2. Review current stock levels
3. Check for low stock items
4. Print or export report
5. Navigate to Reports > Transaction Report
6. Review daily transactions
7. Print or export for records

### Scenario 4: Monthly Inventory Review
1. Login as admin
2. View Stock Levels with low stock filter
3. Generate stock report
4. Review transaction history for the period
5. Generate transaction report
6. Export reports for management review

### Scenario 5: User Management
1. Login as admin
2. Navigate to Users > Manage Users
3. Add new user accounts for staff
4. Assign appropriate roles
5. Deactivate accounts when staff leave

## Benefits for Small Businesses

1. **No Recurring Costs**: One-time setup, no subscription fees
2. **Simple to Use**: Intuitive interface requires minimal training
3. **Complete Audit Trail**: Track all inventory movements
4. **Low Stock Alerts**: Never run out of critical items
5. **Report Generation**: Easy end-of-period reporting
6. **Multi-User Support**: Multiple staff can use the system
7. **Secure**: Password-protected access
8. **Portable**: Lightweight, runs on any computer
9. **No Internet Required**: Works offline
10. **Easy Backup**: Single database file to backup

## Future Enhancement Possibilities

- Barcode scanning support
- Advanced reporting with charts and graphs
- Multi-warehouse support
- Supplier management
- Purchase order generation
- Email notifications for low stock
- Data export to Excel/CSV
- Cloud synchronization
- Mobile app companion
