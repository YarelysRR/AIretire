# Function to format balance properly
def format_balance(amount):
    return f"${amount:,.2f}"


# Mock user database with consistent fields
mock_users = {
    "RF-1234": {
        "account_id": "RF-1234",
        "name": "Alberto Torres",
        "balance": 5000,  # Stored as a number
        "account_type": "401(k)",
        "last_login": "2025-03-10",
        "address": "123 Main St, Anytown, USA",
        "phone": "(555) 123-4567",
        "email": "john.doe@example.com",
        "dob": "1955-01-01",
        "preferred_payment_method": "direct deposit",
        "emergency_contact": {"name": "Jane Doe", "phone": "(555) 987-6543"},
    },
    "RF-5678": {
        "account_id": "RF-5678",
        "name": "Jane Smith",
        "balance": 350000,  # Stored as a number
        "account_type": "IRA",
        "last_login": "2025-03-11",
        "address": "456 Oak St, Somecity, USA",  # Added missing address
        "phone": "(555) 789-0123",  # Added missing phone
        "email": "jane.smith@example.com",  # Added missing email
        "dob": "1965-05-22",  # Added missing DOB
        "preferred_payment_method": "check",  # Added missing payment method
        "emergency_contact": {"name": "Robert Smith", "phone": "(555) 567-8901"},
    },
}

# Mock fraud database
fraud_db = {"RF-9012": {"reason": "suspicious activity", "date_flagged": "2025-02-15"}}


# Function to check if an account is flagged as fraudulent
def is_fraudulent(account_id):
    return fraud_db.get(account_id, None) is not None


# Sample form fields for benefit applications
benefit_form_fields = [
    "name",
    "address",
    "phone",
    "email",
    "dob",
    "account_id",  # Ensured consistency with user data
    "preferred_payment_method",
    "emergency_contact",
]

# Mock form templates
form_templates = {
    "benefit_application": {
        "title": "Senior Benefit Application",
        "fields": benefit_form_fields,
        "description": "Apply for benefits and services"
    },
    "contact_update": {
        "title": "Contact Information Update",
        "fields": ["name", "address", "phone", "email"],
        "description": "Update your contact information"
    },
    "medical_claim": {
        "title": "Medical Expense Claim",
        "fields": [
            "name",
            "account_id",
            "treatment_date",
            "provider",
            "amount",
            "description",
        ],
        "description": "Submit claims for medical expenses"
    },
    "address_change": {
        "title": "Address Change Request",
        "fields": [
            "name",
            "account_id",
            "old_address",
            "new_address",
            "effective_date",
        ],
        "description": "Update your residential address"
    },
    "beneficiary_update": {
        "title": "Beneficiary Update",
        "fields": [
            "name",
            "account_id",
            "current_beneficiary",
            "new_beneficiary",
            "relationship",
        ],
        "description": "Update your beneficiary information"
    },
    # New Categories
    "medication_tracker": {
        "title": "Medication Management",
        "fields": [
            "name",
            "account_id",
            "medication_name",
            "dosage",
            "frequency",
            "prescribing_doctor",
            "pharmacy",
            "start_date",
            "end_date",
            "notes"
        ],
        "description": "Track and manage your medications"
    },
    "appointment_scheduler": {
        "title": "Appointment Record",
        "fields": [
            "name",
            "account_id",
            "appointment_type",
            "provider_name",
            "location",
            "date",
            "time",
            "purpose",
            "preparation_notes",
            "followup_notes"
        ],
        "description": "Keep track of your appointments"
    },
    "emergency_contacts": {
        "title": "Emergency Contacts Update",
        "fields": [
            "name",
            "account_id",
            "primary_contact_name",
            "primary_contact_relationship",
            "primary_contact_phone",
            "primary_contact_email",
            "secondary_contact_name",
            "secondary_contact_relationship",
            "secondary_contact_phone",
            "secondary_contact_email",
            "preferred_hospital",
            "allergies",
            "medical_conditions"
        ],
        "description": "Manage your contacts and critical information"
    },
    "document_storage": {
        "title": "Important Document Storage",
        "fields": [
            "name",
            "account_id",
            "document_type",
            "document_title",
            "issue_date",
            "expiry_date",
            "issuing_authority",
            "document_number",
            "storage_location",
            "digital_copy",
            "notes"
        ],
        "description": "Store and track important document information"
    },
    "service_provider": {
        "title": "Service Provider Directory",
        "fields": [
            "name",
            "account_id",
            "provider_type",
            "provider_name",
            "contact_person",
            "phone",
            "email",
            "address",
            "service_description",
            "contract_details",
            "payment_info"
        ],
        "description": "Manage your service providers' information"
    }
}


# Example usage
def display_user_info(user_id):
    user = mock_users.get(user_id)
    if user:
        return f"""
        **Name:** {user['name']}
        **Balance:** {format_balance(user['balance'])}
        **Account Type:** {user['account_type']}
        **Last Login:** {user['last_login']}
        **Email:** {user['email']}
        **Phone:** {user['phone']}
        **Address:** {user['address']}
        **Fraud Status:** {'⚠️ Flagged' if is_fraudulent(user_id) else '✅ Clear'}
        """
    else:
        return "User not found."
