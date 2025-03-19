import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions
from language_analysis import detect_pii


#New implementation using Azure Text Analytics
def detect_sensitive_data(text):
    """
    Detect sensitive data using Azure Text Analytics API.
    Returns True only if actual PII is detected, not just PII-related discussion.
    """
    pii_results = detect_pii(text)
    
    if not pii_results or not pii_results["detected_entities"]:
        return False
        
    # We already filtered discussion and low confidence in detect_pii
    # This is just a final check for highly sensitive categories
    sensitive_categories = {
        "SSN", "CreditCardNumber", "BankAccount",
        "DriversLicense", "PassportNumber", "HealthID"
    }
    
    for entity in pii_results["detected_entities"]:
        if entity["category"] in sensitive_categories:
            return True
            
    return False


#LEAVING THIS HERE FOR REFERENCE, but PII detection is now done using Azure Text Analytics. Content Safety is used for Harmful Content.
# Original PII detection using Content Safety API
# def detect_sensitive_data(text):
#     """Detect sensitive data using Azure Content Safety API"""
#     try:
#         endpoint = os.getenv("CONTENT_SAFETY_ENDPOINT")
#         key = os.getenv("CONTENT_SAFETY_KEY")
#         if not endpoint or not key:
#             raise ValueError(
#                 "CONTENT_SAFETY_ENDPOINT or CONTENT_SAFETY_KEY environment variable is not set."
#             )
#         client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
#
#         options = {}
#         response = client.analyze_text(
#             text=str(text), categories=["PII"], options=options
#         )
#         return response.pii_entities
#     except Exception as e:
#         print(f"Content Safety API error: {e}")
#         return False  # Default to false on error

#