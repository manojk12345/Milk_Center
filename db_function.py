
import sqlite3

def user():
    # conn = sqlite3.connect('milk_collection_system.db')
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    # Create the User table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"


def farmer():
    # conn = sqlite3.connect('milk_collection_system.db')
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    # Create the Farmer table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FARMER (
            farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmerName TEXT NOT NULL UNIQUE,
            contactInfo TEXT NOT NULL
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"


def milk_collection():
    # conn = sqlite3.connect('milk_collection_system.db')
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    # Create the Milk Collection table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS MILKCOLLECTION (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recordedBy TEXT NOT NULL,
        farmerName text NOT NULL,
        quantity REAL NOT NULL,          
        reading REAL NOT NULL,           
        pricePerLiter REAL NOT NULL,     
        totalAmount REAL NOT NULL,       
        date DATE DEFAULT CURRENT_DATE,
        time TIME DEFAULT CURRENT_TIME,  
        FOREIGN KEY (farmerName) REFERENCES FARMER(farmerName)
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"

def payments():
    # conn = sqlite3.connect('milk_collection_system.db')
    conn = sqlite3.connect('milk_collection_data.db')
    cur = conn.cursor()
    
    # Create the Payments table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PAYMENTS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmerName text NOT NULL,
            totalBalance REAL NOT NULL,      
            setteled REAL NOT NULL,          
            due REAL NOT NULL,               
            FOREIGN KEY (farmerName) REFERENCES FARMER(farmerName)
        )
    ''')

    conn.commit()  
    conn.close() 
    return "success"
