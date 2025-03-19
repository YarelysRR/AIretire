import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv

load_dotenv()

def initialize_text_analytics_client():
    """Initialize Azure Text Analytics client"""
    try:
        endpoint = os.getenv("LANGUAGE_SERVICE_ENDPOINT")
        key = os.getenv("LANGUAGE_SERVICE_KEY")
        
        if not endpoint or not key:
            raise ValueError(
                "LANGUAGE_SERVICE_ENDPOINT or LANGUAGE_SERVICE_KEY not found in environment variables"
            )
            
        credential = AzureKeyCredential(key)
        return TextAnalyticsClient(endpoint=endpoint, credential=credential)
    except Exception as e:
        print(f"Error initializing Text Analytics client: {e}")
        return None

def detect_pii(text):
    """
    Detect PII (Personal Identifiable Information) in text.
    Returns a dictionary with detected PII entities and redacted text.
    """
    try:
        client = initialize_text_analytics_client()
        if not client:
            return None
            
        response = client.recognize_pii_entities([text])[0]
        
        if not response.is_error:
            pii_results = {
                "detected_entities": [
                    {
                        "text": entity.text,
                        "category": entity.category,
                        "confidence_score": entity.confidence_score
                    }
                    for entity in response.entities
                ],
                "redacted_text": response.redacted_text
            }
            return pii_results
            
        return None
        
    except Exception as e:
        print(f"Error in PII detection: {e}")
        return None

def get_linked_entities(text):
    """
    Get entities linked to well-known databases (like Wikipedia).
    Useful for providing authoritative links when mentioning organizations or concepts.
    """
    try:
        client = initialize_text_analytics_client()
        if not client:
            print("Could not initialize Text Analytics client")
            return []
            
        response = client.recognize_linked_entities([text])[0]
        
        if not response.is_error:
            linked_entities = []
            for entity in response.entities:
                # Only include entities with high confidence matches
                high_confidence_matches = [
                    match for match in entity.matches 
                    if match.confidence_score > 0.8
                ]
                
                if high_confidence_matches and entity.url:
                    linked_entities.append({
                        "name": entity.name,
                        "url": entity.url,
                        "data_source": entity.data_source,
                        "matches": [
                            {
                                "text": match.text,
                                "confidence_score": match.confidence_score
                            }
                            for match in high_confidence_matches
                        ]
                    })
            return linked_entities
            
        print(f"Entity recognition error: {response.error}")
        return []
        
    except Exception as e:
        print(f"Error in entity linking: {e}")
        return []

def enhance_text_with_links(text):
    """
    Enhance text by adding authoritative links for recognized entities.
    Particularly useful for organizations like FTC, FBI, or financial institutions.
    """
    try:
        linked_entities = get_linked_entities(text)
        if not linked_entities:
            return text, []
            
        references = []
        enhanced_text = text
        
        # Process entities and create references
        for entity in linked_entities:
            if entity.get("url"):
                # Clean and validate URL
                url = entity["url"].strip()
                if url.startswith(('http://', 'https://')):
                    references.append({
                        "name": entity["name"],
                        "url": url,
                        "data_source": entity.get("data_source", "Unknown")
                    })
        
        return enhanced_text, references
        
    except Exception as e:
        print(f"Error enhancing text: {e}")
        return text, []

def test_analysis(sample_text):
    """
    Test function to demonstrate PII detection and entity linking.
    """
    print("\n=== Text Analysis Test ===")
    print(f"Input text: {sample_text}")
    
    # Test PII detection
    pii_results = detect_pii(sample_text)
    if pii_results:
        print("\nPII Detection Results:")
        print(f"Redacted text: {pii_results['redacted_text']}")
        print("\nDetected PII entities:")
        for entity in pii_results['detected_entities']:
            print(f"- {entity['category']}: {entity['text']} (Confidence: {entity['confidence_score']:.2f})")
    
    # Test entity linking
    linked_entities = get_linked_entities(sample_text)
    if linked_entities:
        print("\nLinked Entities:")
        for entity in linked_entities:
            print(f"\n- {entity['name']} ({entity['data_source']})")
            print(f"  URL: {entity['url']}")
            print("  Matches:")
            for match in entity['matches']:
                print(f"    - {match['text']} (Confidence: {match['confidence_score']:.2f})")
    
    return pii_results, linked_entities

# Example usage:
if __name__ == "__main__":
    sample_queries = [
        "I received an email from someone claiming to be from the FTC about my social security number 123-45-6789",
        "The FBI and SEC warned about investment scams targeting retirement accounts",
        "My Medicare number is 1EG4-TE5-MK73 and I'm worried about identity theft"
    ]
    
    for query in sample_queries:
        test_analysis(query)
