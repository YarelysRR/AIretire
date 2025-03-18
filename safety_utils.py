import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential

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
        response = client.analyze_text(
            text=str(text), categories=["PII"], options=options
        )
        return response.pii_results.identified
    except Exception as e:
        print(f"Content Safety API error: {e}")
        return False  # Default to false on error 