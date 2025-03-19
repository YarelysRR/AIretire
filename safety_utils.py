import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions
from language_analysis import detect_pii


#New implementation using Azure Text Analytics
def detect_sensitive_data(text):
    """Detect sensitive data using Azure Text Analytics API"""
    pii_results = detect_pii(text)
    return bool(pii_results and pii_results["detected_entities"])


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