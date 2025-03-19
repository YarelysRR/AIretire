import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
import tldextract
from prompt_safety import process_prompt
from language_analysis import enhance_text_with_links



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

def get_relevant_trusted_domains(text):
    """Get relevant trusted domains based on keywords in text"""
    domain_keywords = {
        "ssa.gov": ["social security", "ssn", "retirement benefits"],
        "medicare.gov": ["medicare", "health insurance", "medical"],
        "ftc.gov": ["scam", "fraud", "identity theft", "cybersecurity", "consumer protection"],
        "irs.gov": ["tax", "taxes", "refund"],
        "cdc.gov": ["health", "disease", "medical condition"],
        "who.int": ["health", "disease", "pandemic"],
        "aarp.org": ["retirement", "senior", "aging"],
        "usa.gov": ["government", "federal"]
    }
    
    relevant_domains = []
    text_lower = text.lower()
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            relevant_domains.append(domain)
    
    return relevant_domains

def get_ai_response(prompt):
    """Process user input through safety pipeline and get AI response"""
    try:
        # First process through safety pipeline
        safe_prompt = process_prompt(prompt)
        
        # Auto-detect potential phishing patterns
        if contains_suspicious_content(safe_prompt):
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
                - Unusual payment requests
            
            [ALERT: Potential phishing detected in query!]"""
        else:
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
        
        try:
            # Step 1: Get AI response using Gemini
            #USE #gemini-2.0 Flash IF exceeding limit, RPD,RPM or TPM quota
            model = genai.GenerativeModel('gemini-1.5-pro') #gemini-2.0 Flash 
            chat = model.start_chat(history=[])
            
            # With Gemini, we combine system and user messages
            combined_prompt = f"{system_msg}\n\nUser query: {safe_prompt}"
            response = chat.send_message(combined_prompt)
            
            # Extract raw response text
            raw_response = response.text
            
            # Step 3: Apply empathy enhancements
            empathetic_response = add_empathy_enhancements(raw_response)
            
            # Step 4: Apply link safety checks
            safe_response = process_links(empathetic_response)
            
            # Step 5: Add relevant official resources based on content
            relevant_domains = get_relevant_trusted_domains(safe_response)
            if relevant_domains:
                safe_response += "\n\nOfficial Resources:\n"
                for domain in relevant_domains:
                    if domain == "ftc.gov":
                        safe_response += f"🔗 Official FTC Cybersecurity Guide: https://consumer.ftc.gov/identity-theft-and-online-security\n"
                    elif domain == "ssa.gov":
                        safe_response += f"🔗 Official Social Security Website: https://www.ssa.gov\n"
                    elif domain == "medicare.gov":
                        safe_response += f"🔗 Official Medicare Website: https://www.medicare.gov\n"
                    else:
                        safe_response += f"🔗 Official Website: https://www.{domain}\n"
            
            return safe_response
            
        except Exception as e:
            if "429" in str(e):
                return ("I apologize, but I've reached my temporary usage limit. "
                       "Please try again in a few moments. "
                       "If you need immediate assistance, you can:\n"
                       "1. Call our support line: 1-800-555-0123\n"
                       "2. Visit the relevant official website directly:\n"
                       "   - For cybersecurity: https://consumer.ftc.gov/identity-theft-and-online-security\n"
                       "   - For Social Security: https://www.ssa.gov\n"
                       "   - For Medicare: https://www.medicare.gov")
            else:
                raise e
    
    except ValueError as e:
        # Return safety warning to user
        return str(e)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return ("I apologize, but I've reached my temporary usage limit. "
                   "Please try again in a few moments. "
                   "If you need immediate assistance, please call our support line: 1-800-555-0123")
        return f"An error occurred: {error_msg}"
