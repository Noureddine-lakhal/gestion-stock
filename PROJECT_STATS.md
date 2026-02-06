# Project Statistics

## Code Metrics
- **Total Java Files**: 24
- **Total Lines of Code**: 2,669
- **Test Files**: 1
- **UI Components**: 11
- **Data Models**: 3
- **DAO Classes**: 3
- **Service Classes**: 2
- **Utility Classes**: 2

## File Breakdown

### Core Application (1 file)
- Main.java - Application entry point

### Models (3 files)
- User.java - User entity
- Product.java - Product entity
- Transaction.java - Transaction entity

### Data Access Layer (3 files)
- UserDAO.java - User database operations
- ProductDAO.java - Product database operations
- TransactionDAO.java - Transaction database operations

### Service Layer (2 files)
- StockService.java - Stock management business logic
- ReportService.java - Report generation logic

### User Interface (11 files)
- LoginFrame.java - Login screen
- MainFrame.java - Main application window
- ProductManagementFrame.java - Product management UI
- ProductDialog.java - Product add/edit dialog
- EntryFrame.java - Stock entry form
- ExitFrame.java - Stock exit form
- StockLevelsFrame.java - Stock levels viewer
- TransactionsFrame.java - Transaction history viewer
- StockReportFrame.java - Stock report UI
- TransactionReportFrame.java - Transaction report UI
- UserManagementFrame.java - User management UI
- UserDialog.java - User add/edit dialog

### Utilities (2 files)
- DatabaseManager.java - Database connection management
- SessionManager.java - User session management

### Test (1 file)
- TestApplication.java - Comprehensive test suite

## Documentation (4 files)
- README.md - User guide and installation instructions
- FEATURES.md - Detailed feature documentation
- IMPLEMENTATION_SUMMARY.md - Development summary
- PROJECT_STATS.md - This file

## Configuration (3 files)
- pom.xml - Maven build configuration
- .gitignore - Git ignore rules
- build.sh - Build script

## Test Results
- ✓ All 7 test scenarios pass
- ✓ Code review completed
- ✓ CodeQL security scan passed (0 vulnerabilities)

## Dependencies
- sqlite-jdbc 3.41.2.2 - Database connectivity (patched for CVE security vulnerability)
- jbcrypt 0.4 - Password hashing
- Java 11+ - Core platform
- Maven 3.6+ - Build tool

## Build Output
- gestion-stock-1.0-SNAPSHOT.jar - Basic JAR
- gestion-stock-1.0-SNAPSHOT-jar-with-dependencies.jar - Standalone executable JAR (includes all dependencies)
