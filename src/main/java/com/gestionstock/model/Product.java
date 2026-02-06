package com.gestionstock.model;

public class Product {
    private int id;
    private String code;
    private String name;
    private String description;
    private String category;
    private double unitPrice;
    private int currentStock;
    private int minStock;

    public Product() {
    }

    public Product(int id, String code, String name, String description, String category,
                   double unitPrice, int currentStock, int minStock) {
        this.id = id;
        this.code = code;
        this.name = name;
        this.description = description;
        this.category = category;
        this.unitPrice = unitPrice;
        this.currentStock = currentStock;
        this.minStock = minStock;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public double getUnitPrice() {
        return unitPrice;
    }

    public void setUnitPrice(double unitPrice) {
        this.unitPrice = unitPrice;
    }

    public int getCurrentStock() {
        return currentStock;
    }

    public void setCurrentStock(int currentStock) {
        this.currentStock = currentStock;
    }

    public int getMinStock() {
        return minStock;
    }

    public void setMinStock(int minStock) {
        this.minStock = minStock;
    }

    public boolean isLowStock() {
        return currentStock <= minStock;
    }
}
