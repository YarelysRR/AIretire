def clean_and_format_phone(phone_str):
    """
    Cleans and formats a phone number string to (XXX) XXX-XXXX format.
    Non-numeric characters are removed.
    """
    if not phone_str:
        return phone_str
    cleaned = "".join(filter(str.isdigit, phone_str))
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone_str  # Return as-is if not 10 digits
