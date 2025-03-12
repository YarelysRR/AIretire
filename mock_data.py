# Mock user database  
mock_users = {  
    "RF-1234": {  
        "name": "John Doe",  
        "balance": "$500,000",  
        "type": "401(k)",  # Added account type  
        "last_login": "March 10, 2025"  
    },  
    "RF-5678": {  
        "name": "Jane Smith",  
        "balance": "$350,000",  
        "type": "IRA",  # Added account type  
        "last_login": "March 11, 2025"  
    }  
}  

# Mock fraud database  
fraud_db = ["RF-9012"]  # Fraudulent IDs  

# Sample form fields for benefit applications  
benefit_form_fields = [  
    "name",  
    "address",  
    "phone",  
    "email",  
    "dob",  
    "account_id",  
    "preferred_payment_method",  
    "emergency_contact"  
]  

# Mock form templates  (in real app this would be actual forms")
form_templates = {  
    "benefit_application": {  
        "title": "Senior Benefit Application",  
        "fields": benefit_form_fields  
    },  
    "contact_update": {  
        "title": "Contact Information Update",  
        "fields": ["name", "address", "phone", "email"]  
    },  
    "medical_claim": {  
        "title": "Medical Expense Claim",  
        "fields": ["name", "account_id", "treatment_date", "provider", "amount", "description"]  
    }  
}  
