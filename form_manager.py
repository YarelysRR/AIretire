from datetime import datetime
import json
import os
import difflib
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from helpers import clean_and_format_phone


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
    if _user_data_cache is None:
        _user_data_cache = load_user_data()
    all_data = _user_data_cache

    # Create or update user entry
    if user_id not in all_data:
        all_data[user_id] = {}
    all_data[user_id].update(data)

    with open(USER_DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    _user_data_cache = all_data


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
    """Extract structured data from document analysis result"""
    extracted_data = {}

    key_value_pairs = document_result.get("data", {}).get("key_value_pairs", {})

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

    for standard_key, possible_matches in field_mapping.items():
        possible_matches_set = set(possible_matches)
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            if any(match in key_lower for match in possible_matches_set):
                extracted_value = value
                # Phone formatting centralized
                if standard_key == "phone":
                    extracted_value = clean_and_format_phone(extracted_value)
                break

    # Optional form field filtering
    if form_fields:
        extracted_data = {k: v for k, v in extracted_data.items() if k in form_fields}

    return extracted_data


def detect_sensitive_data(text):
    """Detect sensitive data using Azure Content Safety API"""
    try:
        endpoint = os.getenv("CONTENT_SAFETY_ENDPOINT")
        key = os.getenv("CONTENT_SAFETY_KEY")
        if not endpoint or not key:
            raise ValueError(
                "CONTENT_SAFETY_ENDPOINT or CONTENT_SAFETY_KEY environment variable is not set."
            )
        client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        
        options = {}
        response = client.analyze_text(text=str(text), categories=["PII"], options=options)
        return response.pii_results.identified
    except Exception as e:
        print(f"Content Safety API error: {e}")
        return False  # Default to false on error


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


def validate_form_data(form_data, form_fields):
    """
    Validates user inputs against form requirements.
    Returns: (is_valid, error_messages)
    """
    errors = []

    # 1. Check required fields
    for field in form_fields:
        if field not in form_data or not form_data.get(field):
            errors.append(f"Missing required field: {field.replace('_', ' ').title()}")

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
