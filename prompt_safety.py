import os
import re
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from language_tool_python import LanguageTool
from form_manager import detect_sensitive_data
from  ai_processor import client


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
        client = ContentSafetyClient(
            endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY")),
        )
        options ={}

        response = client.analyze_text(
            text=text, categories=["Hate", "SelfHarm", "Sexual", "Violence"], options=options
        )

        return any(category.severity > 0 for category in response.categories_analysis)

    except Exception as e:
        print(f"Content Safety Error: {e}")
        return False  # Safe fallback for seniors


def optimize_prompt(text):
    """Enhance query clarity"""
    optimization_rules = {
        r"\b(retire)\b": "retirement planning",
        r"\b(save)\b": "long-term savings",
        r"\?$": "? Provide detailed steps with examples.",
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
