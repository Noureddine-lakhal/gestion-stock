#!/bin/bash

# Gestion de Stock - Build and Run Script

echo "==================================="
echo "  Gestion de Stock"
echo "  Inventory Management System"
echo "==================================="
echo ""

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed. Please install Maven first."
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed. Please install Java 11 or higher."
    exit 1
fi

echo "Building the application..."
mvn clean package -DskipTests

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo ""
    echo "To run the application:"
    echo "  java -jar target/gestion-stock-1.0-SNAPSHOT-jar-with-dependencies.jar"
    echo ""
    echo "To run tests:"
    echo "  java -cp target/gestion-stock-1.0-SNAPSHOT-jar-with-dependencies.jar com.gestionstock.test.TestApplication"
    echo ""
    echo "Default login credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
else
    echo ""
    echo "Build failed. Please check the errors above."
    exit 1
fi
