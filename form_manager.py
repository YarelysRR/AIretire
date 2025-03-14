import json
import os

# Store extracted data in a simple JSON file (in a real app, use a database)
USER_DATA_FILE = "user_data.json"

"""def load_user_data():
    Load existing user data if available
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}"""
    
def load_user_data(): #THIS IS NEW FUNCTION, ABOVE WAS WORKING. REMOVE IF ISSUES.
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading user data: {e}")
        return {}    

def save_user_data(user_id, data):
    """Save user data to file"""
    all_data = load_user_data()
    
    # Create or update user entry
    if user_id not in all_data:
        all_data[user_id] = {}
    
    # Update with new data (merge dictionaries)
    all_data[user_id].update(data)
    
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    return all_data[user_id]

def get_autocomplete_data(user_id, form_fields):
    """Get data to auto-complete a form for a specific user"""
    all_data = load_user_data()
    user_data = all_data.get(user_id, {})
    
    # Match form fields with stored user data
    autocomplete_data = {}
    for field in form_fields:
        if field in user_data:
            autocomplete_data[field] = user_data[field]
    
    return autocomplete_data

def extract_form_data(document_result):
    """Extract structured data from document analysis result"""
    extracted_data = {}
    
    # Extract data from key-value pairs
    key_value_pairs = document_result.get("data", {}).get("key_value_pairs", {})
    
    # Map common field names to standardized keys
    field_mapping = {
        "name": ["name", "full name", "applicant name"],
        "address": ["address", "home address", "mailing address", "residence"],
        "phone": ["phone", "telephone", "contact number", "phone number"],
        "email": ["email", "email address", "e-mail"],
        "dob": ["date of birth", "dob", "birth date"],
        "ssn": ["ssn", "social security", "social security number"],
        "income": ["income", "annual income", "monthly income"],
        "account_id": ["account id", "account number", "retirement account"],
    }
    
    # Process the extracted key-value pairs
    for extracted_key, extracted_value in key_value_pairs.items():
        # Convert to lowercase for easier matching
        key_lower = extracted_key.lower()
        
        # Check for matches in our mapping
        for standard_key, possible_matches in field_mapping.items():
            if any(match in key_lower for match in possible_matches):
                extracted_data[standard_key] = extracted_value
                break
    
    return extracted_data
