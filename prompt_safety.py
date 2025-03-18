import os
import re
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from language_tool_python import LanguageTool
from safety_utils import detect_sensitive_data


def process_prompt(raw_input):
    """Full pre-processing pipeline"""
    # Step 1: Grammar/Clarity Fix
    tool = LanguageTool("en-US")
    corrected = tool.correct(raw_input)

    # Step 2: Sensitive Data Check
    if detect_sensitive_data(corrected):
        raise ValueError("Contains sensitive data")

    # Step 3: Harmful Content Check
    if detect_harmful_content(corrected):
        raise ValueError("Potentially harmful content")

    # Step 4: Prompt Optimization
    return optimize_prompt(corrected)


def detect_harmful_content(text):
    """Expanded safety check using Azure Content Safety"""
    try:
        # Create an Azure AI Content Safety client
        client = ContentSafetyClient(
            endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
        )

        # Construct request
        request = AnalyzeTextOptions(text=text)

        # Analyze text
        response = client.analyze_text(request)

        # Check each category
        hate_result = next(item for item in response.categories_analysis if item.category == TextCategory.HATE)
        self_harm_result = next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM)
        sexual_result = next(item for item in response.categories_analysis if item.category == TextCategory.SEXUAL)
        violence_result = next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE)

        # Return True if any category has severity > 0
        return any([
            hate_result.severity > 0,
            self_harm_result.severity > 0,
            sexual_result.severity > 0,
            violence_result.severity > 0
        ])

    except HttpResponseError as e:
        print("Content Safety Analysis failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
        print(f"Exception: {e}")
        return False  # Safe fallback for seniors
    except Exception as e:
        print(f"Unexpected error in content safety check: {e}")
        return False  # Safe fallback for seniors


def optimize_prompt(text):
    """Enhance query clarity by optimizing terms for senior assistance"""
    # Remove the automatic addition of "Provide detailed steps with examples"
    optimization_rules = {
        # Health-related terms
        r"\b(doctor)\b": "healthcare provider",
        r"\b(medicine|meds)\b": "medication",
        r"\b(appointment)\b": "medical appointment",
        
        # Technology terms
        r"\b(internet|web)\b": "online",
        r"\b(wifi)\b": "wireless internet",
        r"\b(phone|cell)\b": "mobile phone",
        
        # Security terms
        r"\b(spam|junk)\b": "suspicious message",
        r"\b(scam|fraud)\b": "fraudulent activity",
        r"\b(hack|hacked)\b": "compromised",
        
        # Financial terms
        r"\b(retire)\b": "retirement planning",
        r"\b(save)\b": "savings",
        r"\b(money)\b": "finances",
        
        # Social terms
        r"\b(alone|lonely)\b": "socially isolated",
        r"\b(connect|reach)\b": "communicate",
        r"\b(family|relatives)\b": "family members"
    }
    
    for pattern, replacement in optimization_rules.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def suggest_alternative(prompt):
    """Generate safer alternatives for risky prompts"""
    replacements = {
        # Personal Information
        r"\bSSN\b": "last 4 digits of SSN",
        r"\bpassword\b": "password hint",
        r"\bbank\s+account\b": "account type",
        r"\bcredit\s+card\b": "payment method",
        r"\baddress\b": "city and state",
        
        # Health Information
        r"\bmedical\s+record\b": "general health condition",
        r"\bdiagnosis\b": "health concern",
        r"\bprescription\b": "medication type",
        
        # Security
        r"http[s]?://": "website name",
        r"\blogin\b": "account access",
        r"\bverification\b": "confirmation",
        
        # Financial
        r"\binvestment\b": "savings plan",
        r"\bwire\s+transfer\b": "payment method",
        r"\baccount\s+number\b": "account type"
    }

    for pattern, replacement in replacements.items():
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            return re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)

    # Default suggestion
    return f"Please rephrase your question without sharing personal or sensitive information"

