# src/data/contact_manager.py
# Manages contact list with SQLite database

import sqlite3
import os
from pathlib import Path

class ContactManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = str(Path.home() / ".simple_sideband" / "contacts.db")
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._create_table()
        print("Contact manager initialized: " + db_path)
    
    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL UNIQUE,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def add_contact(self, name, address):
        """Add a new contact"""
        if len(address) != 32:
            print("Invalid address length")
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO contacts (name, address) VALUES (?, ?)",
                (name, address)
            )
            conn.commit()
            conn.close()
            print("Contact added: " + name)
            return True
        except Exception as e:
            print("Error adding contact: " + str(e))
            return False
    
    def get_all_contacts(self):
        """Get all contacts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, address, added_date FROM contacts ORDER BY name")
            contacts = cursor.fetchall()
            conn.close()
            return contacts
        except Exception as e:
            print("Error getting contacts: " + str(e))
            return []
    
    def get_contact_by_address(self, address):
        """Get contact by LXMF address"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM contacts WHERE address = ?", (address,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print("Error getting contact: " + str(e))
            return None
    
    def delete_contact(self, address):
        """Delete a contact"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE address = ?", (address,))
            conn.commit()
            conn.close()
            print("Contact deleted: " + address)
            return True
        except Exception as e:
            print("Error deleting contact: " + str(e))
            return False
    
    def export_contacts(self, export_path):
        """Export contacts to JSON"""
        try:
            contacts = self.get_all_contacts()
            data = [{"name": c[0], "address": c[1], "added": c[2]} for c in contacts]
            import json
            with open(export_path, "w") as f:
                json.dump(data, f, indent=2)
            print("Contacts exported to: " + export_path)
            return True
        except Exception as e:
            print("Error exporting contacts: " + str(e))
            return False
    
    def import_contacts(self, import_path):
        """Import contacts from JSON"""
        try:
            import json
            with open(import_path, "r") as f:
                data = json.load(f)
            for contact in data:
                self.add_contact(contact["name"], contact["address"])
            print("Contacts imported from: " + import_path)
            return True
        except Exception as e:
            print("Error importing contacts: " + str(e))
            return False
