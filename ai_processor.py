import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
import tldextract

load_dotenv()

# Initialize GeminiAPI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Define trusted domains at the top
TRUSTED_DOMAINS = {
    "ssa.gov",  # Social Security Administration
    "medicare.gov",  # Official Medicare
    "ftc.gov",  # Federal Trade Commission
    "irs.gov",  # IRS
    "aarp.org",  # Trusted senior organization
    "usa.gov",  # Official US government
    "myretirement.gov",  # (Example fictional trusted domain)
    "CDC.gov" # Centers for Disease Control and Prevention
    "Medicare.gov" # Official Medicare
    "NIH.gov" # National Institutes of Health
    "WHO.int" # World Health Organization
    "FTC.gov" # Federal Trade Commission
}


def contains_suspicious_content(text):
    """Check for phishing indicators"""
    phishing_patterns = [
        r"\b(account\s*verification)\b",
        r"\b(urgent\s*action\s*required)\b",
        r"\b(wire\s*transfer)\b",
        r"\b(password\s*expiration)\b",
        r"http[s]?://(?!ssa\.gov|medicare\.gov)[^\s]+",
    ]

    return any(re.search(pattern, text, re.IGNORECASE) for pattern in phishing_patterns)


def add_empathy_enhancements(response):
    """Add emotional validation to responses"""
    empathy_keywords = {
        r"\b(phish|scam|fraud)\b": "I understand how worrying this must feel",
        r"\b(health|medical)\b": "Your health and safety are most important",
        r"\b(money|funds)\b": "Financial security is crucial at this stage",
    }

    for pattern, phrase in empathy_keywords.items():
        if re.search(pattern, response, re.IGNORECASE):
            response = f"{phrase}. {response}"
            break

    return response


def process_links(text):
    """Validate and replace suspicious links"""
    # Find all URLs including www. prefixes
    url_pattern = r"\b(?:https?://|www\.)\S+\b"
    urls = re.findall(url_pattern, text)

    for url in urls:
        # Extract main domain using professional-grade parsing
        parsed = tldextract.extract(url)
        main_domain = f"{parsed.domain}.{parsed.suffix}".lower()

        if main_domain not in TRUSTED_DOMAINS:
            # Create senior-friendly warning
            warning = (
                "[Security Alert] This link appears unfamiliar. "
                "For safety, please: \n"
                "1. Do NOT click\n"
                "2. Call our support team: 1-800-555-0123\n"
                "3. Forward the message to phishing@airetire.com"
            )
            text = text.replace(url, warning)

    return text

def get_ai_response(prompt):
    """Get AI response with empathy, security, and link safety checks"""
    
    system_msg = """You're a Senior Support Assistant specializing in retirement, health, and digital security. You are a friendly, patient, and trustworthy AI assistant designed to support seniors. Always prioritize clear, simple, and empathetic communication
    
    Always:
    1. Use simple, empathetic language (reading level: 6th grade)
    2. Identify emotional cues in health/security questions
    3. Check ALL links/emails for phishing signs
    4. Provide actionable steps using this framework:
       - Acknowledge concern
       - Explain risk
       - Suggest verification methods
    5. Cite ONLY these official sources:
       - Social Security Administration (ssa.gov)
       - FTC Phishing Guidelines (consumer.ftc.gov)
       - Medicare (medicare.gov)
    6. Phishing detection checklist:
        - Urgent requests for personal info
        - Mismatched sender domains
        - Suspicious attachments
        - Grammar/spelling errors
        - Unusual payment requests"""
    
    # Auto-detect potential phishing patterns
    if contains_suspicious_content(prompt):
        system_msg += "\n[ALERT: Potential phishing detected in query!]"
    
    try:
        # Step 1: Get AI response using Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        chat = model.start_chat(history=[])
        
        # With Gemini, we combine system and user messages
        combined_prompt = f"{system_msg}\n\nUser query: {prompt}"
        response = chat.send_message(combined_prompt)
        
        # Extract raw response text
        raw_response = response.text
        
        # Step 3: Apply empathy enhancements
        empathetic_response = add_empathy_enhancements(raw_response)
        
        # Step 4: Apply link safety checks
        safe_response = process_links(empathetic_response)
        
        return safe_response
    
    except Exception as e:
        print(f"AI Response Error: {e}")
        return "Sorry, I found an error. Please try again later."
