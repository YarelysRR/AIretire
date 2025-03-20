def clean_and_format_phone(phone_str):
    """
    Cleans and formats a phone number string to (XXX) XXX-XXXX format.
    Non-numeric characters are removed. If there are extra digits, 
    it will attempt to clean them up to fit the standard 10-digit format.
    """
    if not phone_str:
        return phone_str
    
    # Remove all non-numeric characters in one step
    cleaned = ''.join(c for c in phone_str if c.isdigit())
    
    # Handle 11-digit numbers starting with "1" (remove the leading "1")
    if len(cleaned) == 11 and cleaned[0] == '1':
        cleaned = cleaned[1:]

    # If there are more than 10 digits, truncate to the first 10 digits
    cleaned = cleaned[:10]
    
    # Return formatted phone number if we have exactly 10 digits
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    
    # If invalid, return the original string
    return phone_str
