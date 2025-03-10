import requests
import json
import sys
from typing import Dict, Any, List, Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test email"  # Fill in your credentials
PASSWORD = "test password"  # Fill in your credentials

class DeckApiTester:
    """Test the decks API endpoints"""
    
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email 
        self.password = password
        self.token = None
        self.created_decks = []
    
    def login(self) -> bool:
        """Login and get access token"""
        print("\n🔑 Logging in to get access token...")
        login_url = f"{self.base_url}/auth/token"
        
        try:
            response = requests.post(
                login_url,
                data={"username": self.email, "password": self.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"✅ Login successful! Token received")
                return True
            else:
                print(f"❌ Login failed with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def create_deck(self, name: str) -> Optional[Dict[str, Any]]:
        """Create a new deck"""
        print(f"\n📚 Creating deck with name '{name}'...")
        url = f"{self.base_url}/decks"
        
        try:
            response = requests.post(
                url,
                json={"name": name},
                headers=self._get_auth_header()
            )
            
            if response.status_code == 201:
                deck = response.json()
                self.created_decks.append(deck)
                print(f"✅ Deck created with ID: {deck['id']}")
                return deck
            else:
                print(f"❌ Failed to create deck with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating deck: {e}")
            return None
    
    def get_all_decks(self) -> Optional[List[Dict[str, Any]]]:
        """Get all user decks"""
        print("\n📋 Getting all decks...")
        url = f"{self.base_url}/decks"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header()
            )
            
            if response.status_code == 200:
                decks = response.json()
                print(f"✅ Found {len(decks)} decks")
                for deck in decks:
                    print(f"   - Deck ID: {deck['id']}, Name: {deck['name']}")
                return decks
            else:
                print(f"❌ Failed to get decks with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting decks: {e}")
            return None
    
    def get_deck(self, deck_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific deck by ID"""
        print(f"\n🔍 Getting deck with ID {deck_id}...")
        url = f"{self.base_url}/decks/{deck_id}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header()
            )
            
            if response.status_code == 200:
                deck = response.json()
                print(f"✅ Found deck: {deck['name']} (ID: {deck['id']})")
                return deck
            else:
                print(f"❌ Failed to get deck with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting deck: {e}")
            return None
    
    def update_deck(self, deck_id: int, new_name: str) -> Optional[Dict[str, Any]]:
        """Update a deck's name"""
        print(f"\n✏️ Updating deck {deck_id} to name '{new_name}'...")
        url = f"{self.base_url}/decks/{deck_id}"
        
        try:
            response = requests.put(
                url,
                json={"name": new_name},
                headers=self._get_auth_header()
            )
            
            if response.status_code == 200:
                deck = response.json()
                print(f"✅ Deck updated: {deck['name']} (ID: {deck['id']})")
                return deck
            else:
                print(f"❌ Failed to update deck with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error updating deck: {e}")
            return None
    
    def delete_deck(self, deck_id: int) -> bool:
        """Delete a deck"""
        print(f"\n🗑️ Deleting deck with ID {deck_id}...")
        url = f"{self.base_url}/decks/{deck_id}"
        
        try:
            response = requests.delete(
                url,
                headers=self._get_auth_header()
            )
            
            if response.status_code == 204:
                print(f"✅ Deck deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete deck with status code {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting deck: {e}")
            return False
    
    def run_all_tests(self):
        """Run all deck API tests"""
        if not self.login():
            print("❌ Cannot continue tests without authentication")
            return False
        
        print("\n=========================================")
        print("🧪 RUNNING DECK API TESTS")
        print("=========================================")
        
        # Test creating decks
        deck1 = self.create_deck("Mathematics")
        deck2 = self.create_deck("History")
        
        if not deck1 or not deck2:
            print("❌ Cannot continue tests without created decks")
            return False
        
        # Test getting all decks
        self.get_all_decks()
        
        # Test getting a specific deck
        self.get_deck(deck1['id'])
        
        # Test updating a deck
        self.update_deck(deck1['id'], "Advanced Mathematics")
        
        # Verify the update
        self.get_deck(deck1['id'])
        
        # Test deleting a deck
        self.delete_deck(deck2['id'])
        
        # Verify the deletion by getting all decks again
        self.get_all_decks()
        
        print("\n=========================================")
        print("✅ DECK API TESTS COMPLETED")
        print("=========================================")
        return True
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Get authorization header with token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

if __name__ == "__main__":
    # Check if credentials were provided
    if not EMAIL or not PASSWORD:
        print("Please edit this file to add your email and password at the top.")
        print("Usage: python test_decks.py [email] [password]")
        
        # Try to get credentials from command line
        if len(sys.argv) >= 3:
            EMAIL = sys.argv[1]
            PASSWORD = sys.argv[2]
        else:
            # Ask for credentials interactively
            EMAIL = input("Enter your email: ")
            PASSWORD = input("Enter your password: ")
    
    tester = DeckApiTester(API_BASE_URL, EMAIL, PASSWORD)
    tester.run_all_tests()