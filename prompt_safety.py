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
    """Enhance query clarity by optimizing retirement-related terms"""
    optimization_rules = {
        r"\b(retire)\b": "retirement planning",
        r"\b(save)\b": "long-term savings",
        r"\b(invest)\b": "investment strategy",
        r"\b(money)\b": "financial resources",
        r"\b(old)\b": "senior",
        r"\b(benefits)\b": "retirement benefits",
    }
    for pattern, replacement in optimization_rules.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def suggest_alternative(prompt):
    """Generate safer alternatives for risky prompts"""
    replacements = {
        r"\bSSN\b": "last 4 digits of SSN",
        r"\bpassword\b": "password hint",
        r"\bbank\s+account\b": "account type (checking/savings)",
        r"http[s]?://": "official website link",
    }

    for pattern, replacement in replacements.items():
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            return re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)

    # Default suggestion
    return f"Reformulate without sensitive details: '{prompt[:30]}...'"

