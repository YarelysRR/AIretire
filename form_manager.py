from datetime import datetime
import json
import os
import difflib
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from helpers import clean_and_format_phone
from prompt_safety import process_prompt
from safety_utils import detect_sensitive_data


# Store extracted data in a simple JSON file (in a real app, use a database)
USER_DATA_FILE = "user_data.json"

_user_data_cache = None


def load_user_data():
    global _user_data_cache
    if _user_data_cache is None:
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    _user_data_cache = json.load(f)
            else:
                _user_data_cache = {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading user data: {e}")
            _user_data_cache = {}
    return _user_data_cache


def save_user_data(user_id, data):
    """Save user data to file"""
    global _user_data_cache
    
    # Process each text field through safety pipeline
    safe_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            try:
                safe_data[key] = process_prompt(value)
            except ValueError as e:
                raise ValueError(f"Safety check failed for {key}: {str(e)}")
        else:
            safe_data[key] = value
    # Remove the 'changes' key if present
    safe_data.pop("changes", None)
    
    if _user_data_cache is None:
        _user_data_cache = load_user_data()
    all_data = _user_data_cache

    # Create or update user entry
    if user_id not in all_data:
        all_data[user_id] = {}
    all_data[user_id].update(safe_data)

    with open(USER_DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    _user_data_cache = all_data
    
    # Inside save_user_data() in form_manager.py  
    print("[SAVE] Saving Data:", safe_data)  # Log data being saved  


def get_autocomplete_data(user_id, form_fields):
    """
    Get data to auto-complete a form for a specific user.

    Parameters:
    user_id (str): The ID of the user.
    form_fields (list): A list of form field names to be auto-completed.

    Returns:
    dict: A dictionary containing the auto-completed form data.
    """
    all_data = load_user_data()
    user_data = all_data.get(user_id, {})
    autocomplete_data = {field: user_data.get(field, "") for field in form_fields}

    return autocomplete_data


def extract_form_data(document_result, form_fields=None):
    """Extract and validate form data from document analysis result"""
    extracted_data = {}
    
    # Handle case where document_result is a dictionary with 'data' key
    if isinstance(document_result, dict):
        data = document_result.get('data', {})
        
        # If form_fields is specified, only extract those fields
        if form_fields:
            for field in form_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, str):
                        try:
                            value = process_prompt(value)
                        except ValueError as e:
                            raise ValueError(f"Safety check failed for {field}: {str(e)}")
                    extracted_data[field] = value
        else:
            # Extract all fields if no specific fields are requested
            for field, value in data.items():
                if isinstance(value, str):
                    try:
                        value = process_prompt(value)
                    except ValueError as e:
                        raise ValueError(f"Safety check failed for {field}: {str(e)}")
                extracted_data[field] = value
                
    return extracted_data


def auto_correct_form_data(form_data):
    """
    Auto-correct common errors in form data.

    Parameters:
    form_data (dict): A dictionary containing the form data to be corrected.

    Returns:
    dict: A dictionary containing the corrected form data and a 'changes' key with details of the corrections made.
    """
    changes = {}
    corrected_data = form_data.copy()

    # Email correction
    email = form_data.get("email")
    if email and isinstance(email, str) and "@" in email:
        domain = email.split("@")[1]
        common_domains = ["gmail.com", "yahoo.com", "outlook.com"]
        if domain not in common_domains:
            closest = difflib.get_close_matches(domain, common_domains, n=1)
            if closest:
                corrected_email = email.replace(domain, closest[0])
                corrected_data["email"] = corrected_email
                changes["email"] = f"Changed from {email} to {corrected_email}"

    # Phone number formatting
    phone = form_data.get("phone")
    if phone and isinstance(phone, str):
        formatted_phone = clean_and_format_phone(phone)
        if formatted_phone != phone:
            corrected_data["phone"] = formatted_phone
            changes["phone"] = f"Formatted phone number to {formatted_phone}"
    corrected_data["changes"] = changes
    return corrected_data


def validate_form_data(form_data, form_fields, check_required=True):
    """
    Validates user inputs against form requirements.
    Returns: (is_valid, error_messages)
    
     Parameters:
    - form_data: The data to validate
    - form_fields: The fields required in the form
    - check_required: Only check for required fields if True (default)
    """
    errors = []

    # 1. Check required fields
    required_fields_set = set(form_fields)
    missing_fields = required_fields_set.difference(form_data.keys())
    if missing_fields:
        errors.extend([f"Missing required field: {field.replace('_', ' ').title()}" for field in missing_fields])


    # 2. Validate date format for DOB
    if "dob" in form_data and form_data["dob"]:
        if isinstance(form_data["dob"], str):
            try:
                datetime.strptime(form_data["dob"], "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid date format for Date of Birth. Use YYYY-MM-DD")

    # 3. Add sensitive data check
    sensitive_fields = ["ssn", "account_number", "dob"]
    for field in sensitive_fields:
        if field in form_data and form_data[field]:
            is_flagged = detect_sensitive_data(str(form_data[field]))
            if is_flagged:
                errors.append(
                    f"⚠️ Do NOT share sensitive data in {field.replace('_', ' ').title()} field"
                )

    return (len(errors) == 0, errors)
