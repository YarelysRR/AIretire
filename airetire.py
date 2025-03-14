import streamlit as st
from document_processor import process_document
from document_quality import check_image_quality
from voice_assistant import text_to_speech
from form_manager import extract_form_data, save_user_data, get_autocomplete_data
from mock_data import mock_users, fraud_db, form_templates
from gtts import gTTS
import os
import base64

# Initialize session state
if 'verified_user' not in st.session_state:
    st.session_state.verified_user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'extracted_form_data' not in st.session_state:
    st.session_state.extracted_form_data = {}
if 'current_form' not in st.session_state:
    st.session_state.current_form = None
if 'font_size' not in st.session_state:
    st.session_state.font_size = 18
if 'high_contrast' not in st.session_state:
    st.session_state.high_contrast = False

# Set page configuration
st.set_page_config(
    page_title="AIretire: Senior Account Access",
    page_icon=":guardsman:",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed for simplicity
)

# Apply custom CSS for senior-friendly design
def apply_custom_styling():
    contrast_bg = "#000" if st.session_state.high_contrast else "#f8f9fa"
    contrast_text = "#fff" if st.session_state.high_contrast else "#333"
    contrast_button_bg = "#fff" if st.session_state.high_contrast else "#3498db"
    contrast_button_text = "#000" if st.session_state.high_contrast else "#fff"
    contrast_border = "#fff" if st.session_state.high_contrast else "#bdc3c7"

    st.markdown(
        f"""
        <style>
        /* Professional color palette */
        :root {{
            --primary: #1b5e8a;
            --primary-light: #2a7cb3;
            --secondary: #3d9970;
            --background: {contrast_bg};
            --card-bg: #ffffff;
            --text: {contrast_text};
            --text-light: #6c757d;
            --border: {contrast_border};
            --error: #dc3545;
            --success: #28a745;
            --info: #17a2b8;
        }}

        /* Responsive container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
            width: 100%;
        }}

        /* Card component */
        .card {{
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }}

        /* Button styling */
        .stButton>button {{
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 15px 30px;
            font-size: {st.session_state.font_size}px;
            font-weight: 500;
            transition: background-color 0.3s;
            max-width: 300px;
        }}

        .stButton>button:hover {{
            background-color: var(--primary-light);
        }}

        /* Form controls */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stDateInput>div>div>input {{
            font-size: {st.session_state.font_size}px;
            padding: 15px;
            border: 1px solid var(--border);
            border-radius: 4px;
        }}

        /* Typography */
        h1 {{
            font-size: max(24px, min(32px, 3vw));
            color: var(--primary);
            font-weight: 600;
        }}

        h2 {{
            font-size: max(20px, min(28px, 2.5vw));
            color: var(--primary);
            font-weight: 500;
        }}

        h3 {{
            font-size: max(18px, min(24px, 2vw));
            color: var(--text);
            font-weight: 500;
        }}

        p {{
            font-size: {st.session_state.font_size}px;
            color: var(--text);
            line-height: 1.6;
        }}

        /* Responsive grid */
        @media (max-width: 768px) {{
            .hide-mobile {{
                display: none;
            }}
            .mobile-full {{
                width: 100%;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_custom_styling()

# Function for speech interaction
def text_to_speech(message):
    tts = gTTS(text=message, lang='en')
    tts.save("temp_audio.mp3")
    with open("temp_audio.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# Navigation Control
def navigate_to(page_name):
    st.session_state.current_page = page_name
    if page_name != "form_filling":
        st.session_state.current_form = None

# Display Top Navigation Bar
def display_navigation():
    st.markdown("<div class='navigation-bar'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Login", key="nav_login", use_container_width=True):
            navigate_to("login")

    with col2:
        button_state = st.session_state.verified_user is None
        if st.button("Dashboard", key="nav_dashboard", disabled=button_state, use_container_width=True):
            navigate_to("dashboard")

    with col3:
        button_state = st.session_state.verified_user is None
        if st.button("Forms", key="nav_forms", disabled=button_state, use_container_width=True):
            navigate_to("form_filling")

    st.markdown("</div>", unsafe_allow_html=True)

# Display Success, Error, and Info Messages with custom styling
def display_success(message, speak=True):
    st.markdown(
        f"""
        <div style='
            background-color: #e8f5e9;
            color: #2e7d32;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: {st.session_state.font_size}px;
        '>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if speak:
        text_to_speech(f"Success: {message}")

def display_error(message, speak=True):
    st.markdown(
        f"""
        <div style='
            background-color: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: {st.session_state.font_size}px;
        '>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if speak:
        text_to_speech(f"Error: {message}")
        
def display_info(message, speak=True):
    st.markdown(
        f"""
        <div style='
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: {st.session_state.font_size}px;
        '>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if speak:
        text_to_speech(f"Info: {message}")

# Accessibility Controls in Sidebar
def display_accessibility_controls():
    with st.sidebar:
        st.header("Accessibility Settings")

        # Font size control
        new_font_size = st.slider(
            "Text Size",
            min_value=16,
            max_value=28,
            value=st.session_state.font_size,
            step=2
        )
        if new_font_size != st.session_state.font_size:
            st.session_state.font_size = new_font_size
            st.rerun()

        # High contrast mode
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=st.session_state.high_contrast
        )
        if high_contrast != st.session_state.high_contrast:
            st.session_state.high_contrast = high_contrast
            st.rerun()

        # Text-to-speech on/off toggle
        st.checkbox("Text-to-Speech", value=True, help="Enable voice feedback")

        # Instructions
        st.markdown("---")
        st.subheader("Need Help?")
        st.write("Call our support line: 1-800-555-0123")

# Login Page
def render_login_page():
    st.markdown("<h2 style='text-align: center;'>Account Verification</h2>", unsafe_allow_html=True)

    # Main login panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    
    # Center the uploader and instructions
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p class='instruction' style='text-align: center;'>Please upload a clear photo of your Account ID for verification.</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Account ID", type=["jpg", "png", "jpeg"])
        st.markdown("<p class='instruction' style='text-align: center;'>Your Account ID should be clearly visible in the image.</p>", unsafe_allow_html=True)

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()

        with st.spinner("Verifying document..."):
            quality_result = check_image_quality(image_bytes)
            if "error" in quality_result or quality_result.get("qualityScore", 0) < 0.4:
                display_error("Document quality is poor. Please upload a clearer image.")
                return

            document_result = process_document(image_bytes, "id")
            if not document_result["success"]:
                display_error(f"Error: {document_result.get('error')}")
                return

            account_id = document_result["data"].get("documentNumber", "").strip()
            needs_format_correction = account_id and not account_id.startswith("RF-")
            
            if needs_format_correction:
                account_id = "RF-" + account_id
                display_info(f"ID format corrected to: {account_id}", speak=False)  # Don't speak this

            if account_id in fraud_db:
                display_error("Fraud detected. Please contact support.")
                return

            # Check if this is a valid user account
            user_data = mock_users.get(account_id)
            if user_data:
                # User exists, set session state and navigate
                st.session_state.verified_user = user_data.copy()
                st.session_state.verified_user["account_id"] = account_id
                display_success(f"Welcome, {user_data['name']}!")
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                # User doesn't exist
                if needs_format_correction:
                    # If we already displayed a format correction, don't speak the error message
                    display_error("Invalid Account ID. Please try again.")
                else:
                    display_error("Invalid Account ID. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Additional help panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Need Help?")
    st.write("If you're having trouble logging in:")
    st.markdown("1. Make sure your Account ID card is clearly visible in the photo")
    st.markdown("2. Ensure there's good lighting when taking the photo")
    st.markdown("3. Call our support line at 1-800-555-0123 for assistance")
    st.markdown("</div>", unsafe_allow_html=True)
    
def render_dashboard():
    if not st.session_state.verified_user:
        display_error("Please log in first.")
        navigate_to("login")
        return

    user = st.session_state.verified_user
    st.markdown(f"<h2 style='text-align: center;'>Welcome, {user['name']}!</h2>", unsafe_allow_html=True)

    # Account Balance Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Account Balance")
    st.markdown(f"<p class='big-font'>${user['balance']}</p>", unsafe_allow_html=True)
    text_to_speech(f"Your balance is {user['balance']} dollars.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Forms & Applications Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Forms & Applications")
    st.markdown("<p class='instruction'>Select a form type to get started</p>", unsafe_allow_html=True)

    form_type = st.selectbox(
        "Select Form Type",
        options=list(form_templates.keys()),
        format_func=lambda x: form_templates[x]["title"]
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start New Form", use_container_width=True):
            st.session_state.current_form = form_type
            navigate_to("form_filling")

    with col2:
        if st.button("Upload Existing Form", use_container_width=True):
            st.session_state.show_upload = True if not st.session_state.get('show_upload', False) else False

    if st.session_state.get('show_upload', False):
        st.markdown("<div style='padding: 10px; background-color: #f0f0f0; border-radius: 5px;'>", unsafe_allow_html=True)
        st.markdown("<p class='instruction'>Upload a completed form for processing</p>", unsafe_allow_html=True)
        uploaded_form = st.file_uploader("Upload Form", type=["jpg", "png", "pdf"])

        if uploaded_form:
            form_bytes = uploaded_form.read()
            quality_result = check_image_quality(form_bytes)
            if "error" in quality_result or quality_result.get("qualityScore", 0) < 0.6:
                display_error("Form quality is poor. Please upload a clearer image.")
            else:
                form_result = process_document(form_bytes, "form")
                if not form_result["success"]:
                    display_error(f"Error: {form_result.get('error')}")
                else:
                    extracted_data = extract_form_data(form_result)
                    if extracted_data:
                        save_user_data(user["account_id"], extracted_data)
                        display_success("Form data extracted successfully.")

                        # Display extracted data in a table format
                        st.markdown("<table style='width:100%; border-collapse: collapse;'>", unsafe_allow_html=True)
                        for key, value in extracted_data.items():
                            field_name = key.replace("_", " ").title()
                            st.markdown(f"<tr><td style='padding:8px; border:1px solid #ddd; font-weight:bold;'>{field_name}</td><td style='padding:8px; border:1px solid #ddd;'>{value}</td></tr>", unsafe_allow_html=True)
                        st.markdown("</table>", unsafe_allow_html=True)
                    else:
                        display_error("Could not extract form data.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Profile Information Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Profile Information")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='field-label'>Name:</p>", unsafe_allow_html=True)
        st.write(user.get('name', 'Not available'))

        st.markdown("<p class='field-label'>Account ID:</p>", unsafe_allow_html=True)
        st.write(user.get('account_id', 'Not available'))

    with col2:
        st.markdown("<p class='field-label'>Last Login:</p>", unsafe_allow_html=True)
        st.write(user.get('last_login', 'First Login'))

        st.markdown("<p class='field-label'>Account Type:</p>", unsafe_allow_html=True)
        st.write(user.get('account_type', 'Standard'))

    if st.button("Sign Out", use_container_width=True):
        st.session_state.verified_user = None
        navigate_to("login")

    st.markdown("</div>", unsafe_allow_html=True)
    
def render_form_filling():
    if not st.session_state.verified_user:
        display_error("Please login first.")
        navigate_to("login")
        return

    # If no form is selected yet, show form selection
    if not st.session_state.current_form:
        st.markdown("<h2 style='text-align: center;'>Select a Form</h2>", unsafe_allow_html=True)
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<p class='instruction'>Choose the type of form you need to fill out</p>", unsafe_allow_html=True)

        form_options = list(form_templates.keys())
        form_cols = st.columns(len(form_options))

        for i, form_key in enumerate(form_options):
            with form_cols[i]:
                form_title = form_templates[form_key]["title"]
                st.markdown(f"<p style='text-align:center; font-weight:bold;'>{form_title}</p>", unsafe_allow_html=True)
                if st.button(f"Select", key=f"select_{form_key}", use_container_width=True):
                    st.session_state.current_form = form_key
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = st.session_state.verified_user
    form_type = st.session_state.current_form
    form_template = form_templates[form_type]

    st.markdown(f"<h2 style='text-align: center;'>{form_template['title']}</h2>", unsafe_allow_html=True)

    # Get autocomplete data
    autocomplete_data = get_autocomplete_data(user["account_id"], form_template["fields"])

    # Form panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    # Form instructions
    if "description" in form_template:
        st.markdown(f"<p class='instruction'>{form_template['description']}</p>", unsafe_allow_html=True)

    # Add progress indicator
    total_fields = len(form_template["fields"])
    st.progress(0.0)  # Start with empty progress

    # Organize form into sections if needed
    form_data = {}

    # Pre-fill Account ID
    if "account_id" in form_template["fields"]:
        st.markdown("<p class='field-label'>Account ID</p>", unsafe_allow_html=True)
        st.markdown("<p class='field-help'>Your account identifier</p>", unsafe_allow_html=True)
        st.text_input("Account ID", value=user["account_id"], disabled=True, key="account_id_field")
        form_data["account_id"] = user["account_id"]

    # Group fields into logical sections (e.g., personal info, request details)
    personal_fields = [f for f in form_template["fields"] if f in ["name", "dob", "address", "phone", "email"] and f != "account_id"]
    request_fields = [f for f in form_template["fields"] if f not in personal_fields and f != "account_id"]

    if personal_fields:
        st.subheader("Personal Information")

        for field in personal_fields:
            default_value = autocomplete_data.get(field, "")
            field_label = field.replace("_", " ").title()

            st.markdown(f"<p class='field-label'>{field_label}</p>", unsafe_allow_html=True)

            if field == "dob":
                st.markdown("<p class='field-help'>Your date of birth</p>", unsafe_allow_html=True)
                form_data[field] = st.date_input("Date of Birth", value=None, key=f"field_{field}")
            elif field == "phone":
                st.markdown("<p class='field-help'>Your contact phone number</p>", unsafe_allow_html=True)
                form_data[field] = st.text_input("Phone", value=default_value, key=f"field_{field}", placeholder="(123) 456-7890")
            elif field == "email":
                st.markdown("<p class='field-help'>Your email address</p>", unsafe_allow_html=True)
                form_data[field] = st.text_input("Email", value=default_value, key=f"field_{field}", placeholder="your.email@example.com")
            elif field == "address":
                st.markdown("<p class='field-help'>Your current mailing address</p>", unsafe_allow_html=True)
                form_data[field] = st.text_area("Address", value=default_value, key=f"field_{field}", height=100)
            else:
                form_data[field] = st.text_input(field_label, value=default_value, key=f"field_{field}")

    if request_fields:
        st.subheader("Request Details")

        for field in request_fields:
            default_value = autocomplete_data.get(field, "")
            field_label = field.replace("_", " ").title()

            st.markdown(f"<p class='field-label'>{field_label}</p>", unsafe_allow_html=True)

            if field == "treatment_date":
                st.markdown("<p class='field-help'>Date of treatment or service</p>", unsafe_allow_html=True)
                form_data[field] = st.date_input("Date", value=None, key=f"field_{field}")
            elif field == "amount":
                st.markdown("<p class='field-help'>Dollar amount requested</p>", unsafe_allow_html=True)
                form_data[field] = st.number_input("Amount ($)", value=0.0, step=10.0, key=f"field_{field}")
            elif field == "reason":
                st.markdown("<p class='field-help'>Reason for this request</p>", unsafe_allow_html=True)
                options = ["Medical Expense", "Withdrawal", "Address Change", "Beneficiary Update", "Other"]
                form_data[field] = st.selectbox("Select Reason", options=options, key=f"field_{field}")
            elif field == "description":
                st.markdown("<p class='field-help'>Additional details about your request</p>", unsafe_allow_html=True)
                form_data[field] = st.text_area("Details", value=default_value, key=f"field_{field}", height=150)
            else:
                form_data[field] = st.text_input(field_label, value=default_value, key=f"field_{field}")

    # Form submission buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            navigate_to("dashboard")

    with col2:
        if st.button("Submit Form", use_container_width=True):
            # Updated to handle the tuple return value from validate_form_data
            validation_result, errors = validate_form_data(form_data, form_template["fields"])
            if validation_result:
                save_user_data(user["account_id"], form_data)
                display_success("Form submitted successfully!")

                # Show summary of submitted data
                st.subheader("Submission Summary")

                # Format the summary in a table
                st.markdown("<table style='width:100%; border-collapse: collapse;'>", unsafe_allow_html=True)
                for key, value in form_data.items():
                    if key != "account_id":  # Skip account ID in summary
                        field_name = key.replace("_", " ").title()
                        st.markdown(f"<tr><td style='padding:8px; border:1px solid #ddd; font-weight:bold;'>{field_name}</td><td style='padding:8px; border:1px solid #ddd;'>{value}</td></tr>", unsafe_allow_html=True)
                st.markdown("</table>", unsafe_allow_html=True)

                # Add a button to return to dashboard
                if st.button("Return to Dashboard", use_container_width=True):
                    navigate_to("dashboard")
            else:
                # Display each validation error message
                for error in errors:
                    display_error(error)

    st.markdown("</div>", unsafe_allow_html=True)

    # Help panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Need Help?")
    st.write("If you need assistance filling out this form:")
    st.markdown("1. Call our support line at 1-800-555-0123")
    st.markdown("2. Visit your local branch for in-person help")
    st.markdown("3. Email us at support@airetire.com")
    st.markdown("</div>", unsafe_allow_html=True)

# Validate form data
def validate_form_data(form_data, form_fields):
    """
    Validates user inputs against form requirements with Azure-enhanced checks.
    Returns: (is_valid, error_messages)
    """
    errors = []
    
    # 1. Check required fields
    for field in form_fields:
        if not form_data.get(field):
            errors.append(f"Missing required field: {field.replace('_', ' ').title()}")
    
    # 2. Add Azure Content Safety check for sensitive data
    sensitive_fields = ["ssn", "account_number", "dob"]
    for field in sensitive_fields:
        if field in form_data:
            # Use Azure Content Safety API
            is_flagged = detect_sensitive_data(form_data[field])
            if is_flagged:
                errors.append(f"⚠️ Do NOT share sensitive data in {field.replace('_', ' ').title()} field")

    return (len(errors) == 0, errors)

# This function needs to be implemented to use Azure Content Safety
def detect_sensitive_data(value):
    """
    Checks if a value contains sensitive data using Azure Content Safety API.
    Returns: True if sensitive data detected, False otherwise
    
    TODO: Implement this function with Azure Content Safety API
    """
    # Placeholder for Azure Content Safety API implementation
    # Example implementation (replace with actual API call):
    # from azure.ai.contentsafety import ContentSafetyClient
    # from azure.core.credentials import AzureKeyCredential
    # client = ContentSafetyClient(endpoint="your_endpoint", credential=AzureKeyCredential("your_key"))
    # result = client.analyze_text(text=str(value))
    # return result.harmful_content_detected
    
    # For now, return False (no sensitive data detected)
    # but you will replace this with actual implementation
    return False


#def validate_form_data(form_data, required_fields):
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            return False
    #return True""" # THIS WAS WORKING BEFORE BUT ADDED EXTRA CODE FOR MORE FUNCTIONALITY, DELETE IF NOT IN USE

# Main Application Flow
def main():
    # Logo and Title
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/AIretire_Logo.png", width=200)  # Replace with actual logo path
        st.markdown("<h1 style='text-align: center;'>AIretire: <br> Your all-in-one service </br> </h1>", unsafe_allow_html=True)

    # Display accessibility sidebar
    display_accessibility_controls()

    # Display navigation
    display_navigation()

    # Display the current page
    if st.session_state.current_page == "login":
        render_login_page()
    elif st.session_state.current_page == "dashboard":
        render_dashboard()
    elif st.session_state.current_page == "form_filling":
        render_form_filling()

    # Footer
    st.markdown("<footer>© 2025 AIretire. All rights reserved.</footer>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()