# Description: This is the main application file for the AIretire application. It contains the Streamlit code for the user interface and application logic.
import os
import base64
import streamlit as st
import time

from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai

from document_processor import process_document
from document_quality import check_image_quality
from voice_assistant import text_to_speech, speech_to_text
from form_manager import (
    extract_form_data,
    save_user_data,
    get_autocomplete_data,
    auto_correct_form_data,
    validate_form_data,
)
from mock_data import mock_users, fraud_db, form_templates, format_balance
from prompt_safety import suggest_alternative, process_prompt
from ai_processor import get_ai_response

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Initialize session state
if "verified_user" not in st.session_state:
    st.session_state.verified_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "extracted_form_data" not in st.session_state:
    st.session_state.extracted_form_data = {}
if "current_form" not in st.session_state:
    st.session_state.current_form = None
if "font_size" not in st.session_state:
    st.session_state.font_size = 18
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False
if "audio_played" not in st.session_state:
    st.session_state.audio_played = False
if "success_message_shown" not in st.session_state:
    st.session_state.success_message_shown = False
if "error_message_shown" not in st.session_state:
    st.session_state.error_message_shown = False
if "info_message_shown" not in st.session_state:
    st.session_state.info_message_shown = False
if "dashboard_audio_played" not in st.session_state:
    st.session_state.dashboard_audio_played = False
if "text_to_speech_enabled" not in st.session_state:
    st.session_state.text_to_speech_enabled = True  # Default to enabled
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False
if "form_submission_in_progress" not in st.session_state:
    st.session_state.form_submission_in_progress = False
if "welcome_message_played" not in st.session_state:
    st.session_state.welcome_message_played = False


# Set page configuration
st.set_page_config(
    page_title="AIretire: Senior Account Access",
    page_icon=":guardsman:",
    # Start with sidebar collapsed for simplicity
    initial_sidebar_state="collapsed",
)


# Apply custom CSS for senior-friendly design
def apply_custom_styling():
    # Get current settings from session state
    contrast_bg = (
        "#000" if st.session_state.high_contrast else "#ffffff"
    )  # Pure white background
    contrast_text = (
        "#fff" if st.session_state.high_contrast else "#e0e0e0"
    )  # Dark text color
    text_size = st.session_state.font_size

    st.markdown(
        f"""
        <style>
        /* Base styles */
        :root {{
            --primary: #1b5e8a;
            --text-size: {text_size}px;
            --text: {contrast_text};
            --background: {contrast_bg};
            --button-bg: #1b5e8a;
            --button-bg-contrast: #fff;
        }}

        /* Apply text size globally */
        p, .stTextInput>div>div>input, .stButton>button, .stMarkdown {{
            font-size: var(--text-size) !important;
        }}

        /* High-contrast overrides */
        .stButton>button {{
            background-color: var(--button-bg);
            color: var(--button-text);
        }}
        
        

        /* Fix help text visibility */
        .stFileUploader .stAlert, .stMarkdown {{
            color: var(--text) !important;
        }}

        /* Card component */
        .card {{
            background-color: var(--background);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #ddd;
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


# Navigation Control
def navigate_to(page_name):
    st.session_state.current_page = page_name
    # Reset message flags only if they are True
    if st.session_state.success_message_shown:
        st.session_state.success_message_shown = False
    if st.session_state.error_message_shown:
        st.session_state.error_message_shown = False
    if st.session_state.info_message_shown:
        st.session_state.info_message_shown = False
    if page_name != "form_filling":
        st.session_state.current_form = None


# Display Top Navigation Bar
def display_navigation():
    button_state = st.session_state.verified_user is None

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Login", key="nav_login", use_container_width=True):
            navigate_to("login")

    with col2:
        if st.button(
            "Dashboard",
            key="nav_dashboard",
            disabled=button_state,
            use_container_width=True,
        ):
            navigate_to("dashboard")

    with col3:
        button_state = st.session_state.verified_user is None
        if st.button(
            "Forms", key="nav_forms", disabled=button_state, use_container_width=True
        ):
            navigate_to("form_filling")

    with col4:
        if st.button(
            "AI Assistant",
            disabled=button_state,
            key="nav_ai",
            use_container_width=True,
        ):
            navigate_to("ai_assistant")

    st.markdown("</div>", unsafe_allow_html=True)


# Display Success, Error, and Info Messages with custom styling
def display_success(message, speak=True):
    if not st.session_state.success_message_shown:
        st.session_state.success_message_shown = True

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

        if speak and st.session_state.text_to_speech_enabled:
            try:
                audio_html = text_to_speech(f"Success: {message}")
                if audio_html is not None:
                    st.markdown(audio_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error in text-to-speech: {e}")


def display_error(message, speak=True):
    if not st.session_state.error_message_shown:
        st.session_state.error_message_shown = True
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

        try:
            audio_html = text_to_speech(f"Error: {message}")
            if audio_html is not None:
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error in text-to-speech: {e}")


def display_info(message, speak=True):
    if not st.session_state.info_message_shown:
        st.session_state.info_message_shown = True

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
    )
    if speak and st.session_state.text_to_speech_enabled:
        try:
            audio_html = text_to_speech(f"Info: {message}")
            if audio_html is not None:
                st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error in text-to-speech: {e}")
        unsafe_allow_html = (True,)


# Accessibility Controls in Sidebar
def display_accessibility_controls():
    with st.sidebar:
        st.header("Accessibility Settings")

        rerun_needed = False

        # Font size control
        new_font_size = st.slider(
            "Text Size",
            min_value=16,
            max_value=28,
            value=st.session_state.font_size,
            step=2,
        )
        if new_font_size != st.session_state.font_size:
            st.session_state.font_size = new_font_size
            rerun_needed = True

        # High contrast mode
        high_contrast = st.checkbox(
            "High Contrast Mode", value=st.session_state.high_contrast
        )
        if high_contrast != st.session_state.high_contrast:
            st.session_state.high_contrast = high_contrast
            rerun_needed = True

        # Text-to-speech on/off toggle - store the state
        text_to_speech_enabled = st.checkbox(
            "Text-to-Speech",
            value=st.session_state.text_to_speech_enabled,
            help="Enable Text-to-Speech feedback",
        )
        if text_to_speech_enabled != st.session_state.text_to_speech_enabled:
            st.session_state.text_to_speech_enabled = text_to_speech_enabled
            rerun_needed = True

        if rerun_needed:
            st.rerun()

        # Instructions
        st.markdown("---")
        st.subheader("Need Help?")
        st.write("Call our support line: 1-800-555-0123")


# Login Page
def render_login_page():
    st.markdown(
        "<h2 style='text-align: center;'>Account Verification</h2>",
        unsafe_allow_html=True,
    )

    # Main login panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    # Center the uploader and instructions
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<p class='instruction' style='text-align: center;'>To login, please upload a clear photo of your Account ID for verification.</p>",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload Account ID", type=["jpg", "png", "jpeg"]
        )
        st.markdown(
            "<p class='instruction' style='text-align: center;'>Your Account ID should be clearly visible in the image.</p>",
            unsafe_allow_html=True,
        )

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()

        with st.spinner("Verifying document..."):
            # Check image quality
            quality_result = check_image_quality(image_bytes)
            if "error" in quality_result or quality_result.get("qualityScore", 0) < 0.4:
                display_error(
                    "Document quality is poor. Please upload a clearer image."
                )
                return

            # Process document
            document_result = process_document(image_bytes, "id")
            if not document_result["success"]:
                display_error(f"Error: {document_result.get('error')}")
                return

            # Extract and validate account ID
            account_id = document_result["data"].get("documentNumber", "").strip()
            needs_format_correction = account_id and not account_id.startswith("RF-")

            if needs_format_correction:
                account_id = "RF-" + account_id
                display_info(f"ID format corrected to: {account_id}", speak=False)

            if account_id in fraud_db:
                display_error("Fraud detected. Please contact support.")
                return

            # Check if this is a valid user account
            user_data = mock_users.get(account_id)
            if user_data:
                # User exists, set session state and navigate
                st.session_state.verified_user = user_data.copy()
                st.session_state.verified_user["account_id"] = account_id
                st.session_state.current_page = "dashboard"
                display_success(f"Welcome, {user_data['name']}!", speak=True)
                st.session_state.welcome_message_played = True
                st.rerun()  # imp to have is permitting user going to dashboard after verification
            else:
                # User doesn't exist
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

    # ========== Render ALL UI components first ==========
    # Welcome header
    st.markdown(
        f"<h2 style='text-align: center;'>Welcome, {user['name']}!</h2>",
        unsafe_allow_html=True,
    )

    # Account Balance Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Account Balance")
    st.markdown(
        f"<p class='big-font'>{format_balance(user['balance'])}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Forms & Applications Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Forms & Applications")
    st.markdown(
        "<p class='instruction'>Select a form type to get started</p>",
        unsafe_allow_html=True,
    )

    form_type = st.selectbox(
        "Select Form Type",
        options=list(form_templates.keys()),
        format_func=lambda x: form_templates[x]["title"],
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start New Form", use_container_width=True):
            st.session_state.current_form = form_type
            navigate_to("form_filling")

    with col2:
        if st.button("Upload Existing Form", use_container_width=True):
            st.session_state.show_upload = not st.session_state.get(
                "show_upload", False
            )

    # Upload section - properly nested inside the main panel
    if st.session_state.get("show_upload", False):
        st.markdown(
            "<div style='padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-top: 15px;'>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p class='instruction'>Upload a completed form for processing</p>",
            unsafe_allow_html=True,
        )
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

                        # Display extracted data
                        st.markdown(
                            "<table style='width:100%; border-collapse: collapse;'>",
                            unsafe_allow_html=True,
                        )
                        for key, value in extracted_data.items():
                            field_name = key.replace("_", " ").title()
                            st.markdown(
                                f"<tr>"
                                f"<td style='padding:8px; border:1px solid #ddd; font-weight:bold;'>{field_name}</td>"
                                f"<td style='padding:8px; border:1px solid #ddd;'>{value}</td>"
                                f"</tr>",
                                unsafe_allow_html=True,
                            )
                        st.markdown("</table>", unsafe_allow_html=True)
                    else:
                        display_error("Could not extract form data.")

        st.markdown("</div>", unsafe_allow_html=True)  # Close upload section div

    st.markdown("</div>", unsafe_allow_html=True)  # Close main Forms panel

    # Profile Information Panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Profile Information")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='field-label'>Name:</p>", unsafe_allow_html=True)
        st.write(user.get("name", "Not available"))

        st.markdown("<p class='field-label'>Account ID:</p>", unsafe_allow_html=True)
        st.write(user.get("account_id", "Not available"))

    with col2:
        st.markdown("<p class='field-label'>Last Login:</p>", unsafe_allow_html=True)
        st.write(user.get("last_login", "First Login"))

        st.markdown("<p class='field-label'>Account Type:</p>", unsafe_allow_html=True)
        st.write(user.get("account_type", "Standard"))

    if st.button("Sign Out", use_container_width=True):
        st.session_state.verified_user = None
        st.session_state.dashboard_audio_played = False
        navigate_to("login")

    st.markdown("</div>", unsafe_allow_html=True)  # Close Profile panel

    # ========== Audio handling AFTER UI renders ==========
    # Audio handling - Moved INSIDE the function
    if (
        not st.session_state.dashboard_audio_played
        and st.session_state.text_to_speech_enabled
        and st.session_state.verified_user
    ):
        user = st.session_state.verified_user
        audio_text = f"{user['name']}. Your account balance is {format_balance(user['balance'])}."

        try:
            audio_html = text_to_speech(audio_text)
            if audio_html:
                st.markdown(audio_html, unsafe_allow_html=True)
                st.session_state.dashboard_audio_played = True  # Set FIRST
        except Exception as e:
            st.error(f"Audio error: {e}")


def render_form_filling():
    # In render_form_filling():

    if not st.session_state.verified_user:
        display_error("Please login first.")
        navigate_to("login")
        return

    # If no form is selected yet, show form selection
    if not st.session_state.current_form:
        st.markdown(
            "<h2 style='text-align: center;'>Select a Form</h2>", unsafe_allow_html=True
        )
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown(
            "<p class='instruction'>Choose the type of form you need to fill out</p>",
            unsafe_allow_html=True,
        )

        form_options = list(form_templates.keys())
        form_cols = st.columns(len(form_options))

        for i, form_key in enumerate(form_options):
            with form_cols[i]:
                form_title = form_templates[form_key]["title"]
                st.markdown(
                    f"<p style='text-align:center; font-weight:bold;'>{form_title}</p>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"Select", key=f"select_{form_key}", use_container_width=True
                ):
                    st.session_state.current_form = form_key
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = st.session_state.verified_user
    form_type = st.session_state.current_form
    form_template = form_templates[form_type]

    st.markdown(
        f"<h2 style='text-align: center;'>{form_template['title']}</h2>",
        unsafe_allow_html=True,
    )

    # Get autocomplete data
    autocomplete_data = get_autocomplete_data(
        user["account_id"], form_template["fields"]
    )

    # Form panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    # Form instructions
    if "description" in form_template:
        st.markdown(
            f"<p class='instruction'>{form_template['description']}</p>",
            unsafe_allow_html=True,
        )

    # Add progress indicator
    st.progress(0.0)  # Start with empty progress

    # Organize form into sections if needed
    form_data = {
        field: "" for field in form_template["fields"]
    }  # Initialize form data with empty strings

    # Pre-fill Account ID
    if "account_id" in form_template["fields"]:
        st.markdown("<p class='field-label'>Account ID</p>", unsafe_allow_html=True)
        st.markdown(
            "<p class='field-help'>Your account identifier</p>", unsafe_allow_html=True
        )
        st.text_input(
            "Account ID",
            value=user["account_id"],
            disabled=True,
            key="account_id_field",
        )
        form_data["account_id"] = user["account_id"]

    # Group fields into logical sections (e.g., personal info, request details)
    personal_fields = [
        f
        for f in form_template["fields"]
        if f in ["name", "dob", "address", "phone", "email"] and f != "account_id"
    ]
    request_fields = [
        f
        for f in form_template["fields"]
        if f not in personal_fields and f != "account_id"
    ]

    if personal_fields:
        st.subheader("Personal Information")

        for field in personal_fields:
            default_value = autocomplete_data.get(field, "")
            field_label = field.replace("_", " ").title()

            st.markdown(
                f"<p class='field-label'>{field_label}</p>", unsafe_allow_html=True
            )

            if field == "dob":
                st.markdown(
                    "<p class='field-help'>Your date of birth</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.date_input(
                    "Date of Birth", value=None, key=f"field_{field}"
                )
            elif field == "phone":
                st.markdown(
                    "<p class='field-help'>Your contact phone number</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.text_input(
                    "Phone",
                    value=default_value,
                    key=f"field_{field}",
                    placeholder="(123) 456-7890",
                )
            elif field == "email":
                st.markdown(
                    "<p class='field-help'>Your email address</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.text_input(
                    "Email",
                    value=default_value,
                    key=f"field_{field}",
                    placeholder="your.email@example.com",
                )
            elif field == "address":
                st.markdown(
                    "<p class='field-help'>Your current mailing address</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.text_area(
                    "Address", value=default_value, key=f"field_{field}", height=100
                )
            else:
                form_data[field] = st.text_input(
                    field_label, value=default_value, key=f"field_{field}"
                )

    if request_fields:
        st.subheader("Request Details")

        for field in request_fields:
            default_value = autocomplete_data.get(field, "")
            field_label = field.replace("_", " ").title()

            st.markdown(
                f"<p class='field-label'>{field_label}</p>", unsafe_allow_html=True
            )

            if field == "treatment_date":
                st.markdown(
                    "<p class='field-help'>Date of treatment or service</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.date_input(
                    "Date", value=None, key=f"field_{field}"
                )
            elif field == "amount":
                st.markdown(
                    "<p class='field-help'>Dollar amount requested</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.number_input(
                    "Amount ($)", value=0.0, step=10.0, key=f"field_{field}"
                )
            elif field == "reason":
                st.markdown(
                    "<p class='field-help'>Reason for this request</p>",
                    unsafe_allow_html=True,
                )
                options = [
                    "Medical Expense",
                    "Withdrawal",
                    "Address Change",
                    "Beneficiary Update",
                    "Other",
                ]
                form_data[field] = st.selectbox(
                    "Select Reason", options=options, key=f"field_{field}"
                )
            elif field == "description":
                st.markdown(
                    "<p class='field-help'>Additional details about your request</p>",
                    unsafe_allow_html=True,
                )
                form_data[field] = st.text_area(
                    "Details", value=default_value, key=f"field_{field}", height=150
                )
            else:
                form_data[field] = st.text_input(
                    field_label, value=default_value, key=f"field_{field}"
                )
    # Form submission buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            navigate_to("dashboard")

    with col2:
        if st.button("Submit Form", use_container_width=True):
            if st.session_state.form_submission_in_progress:
                with st.spinner("Submitting form, please wait..."):
                    display_error("Submission already in progress", speak=False)
            else:
                st.session_state.form_submission_in_progress = True
                st.session_state.error_message_shown = False  # Reset error state

                try:
                    # First check if we have any data to submit
                    if any(form_data.values()):
                        # Auto-correct inputs before validation
                        corrected_data = auto_correct_form_data(form_data)

                        # Debug log
                        print(f"Validating form data: {corrected_data}")

                        # Validate corrected data
                        is_valid, errors = validate_form_data(
                            corrected_data, form_template["fields"]
                        )

                        if is_valid:
                            # Show corrections to user if any
                            if "changes" in corrected_data and corrected_data["changes"]:
                                display_info(
                                    "We made these corrections: "
                                    + str(corrected_data.get("changes", {}))
                                )

                            # Save the corrected data
                            save_user_data(user["account_id"], corrected_data)
                            display_success("Form submitted successfully!")

                            # Submission summary
                            st.subheader("Submission Summary")
                            st.markdown(
                                "<table style='width:100%; border-collapse: collapse;'>",
                                unsafe_allow_html=True,
                            )
                            for key, value in corrected_data.items():
                                if key != "account_id" and key != "changes":
                                    field_name = key.replace("_", " ").title()
                                    st.markdown(
                                        f"<tr><td style='padding:8px; border:1px solid #ddd; font-weight:bold;'>{field_name}</td>"
                                        f"<td style='padding:8px; border:1px solid #ddd;'>{value}</td></tr>",
                                        unsafe_allow_html=True,
                                    )
                            st.markdown("</table>", unsafe_allow_html=True)

                            if st.button("Return to Dashboard", use_container_width=True):
                                navigate_to("dashboard")
                        else:
                            # Display each validation error
                            for error in errors:
                                display_error(error)
                    else:
                        display_error("Please fill out the form before submitting.")
                finally:
                    # Ensure flag is reset whether success/failure
                    st.session_state.form_submission_in_progress = False
                    st.rerun()  # To update UI

    st.markdown("</div>", unsafe_allow_html=True)

    # Help panel
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Need Help?")
    st.write("If you need assistance filling out this form:")
    st.markdown("1. Call our support line at 1-800-555-0123")
    st.markdown("2. Visit your local branch for in-person help")
    st.markdown("3. Email us at support@airetire.com")
    st.markdown("</div>", unsafe_allow_html=True)


# Add to AIretire.py
def render_ai_assistant():
    # Initialize session state variables at the top level
    for key, default_value in {
        "messages": [],
        "is_recording": False,
        "recording_start_time": None,
        "voice_input": None,
        "is_speaking": False,
        "stop_speech_requested": False,
        "processing_input": False,
        "current_transcription": None,
        "transcription_complete": False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    st.markdown(
        "<h2 style='text-align: center;'>Trusted Companion</h2>",
        unsafe_allow_html=True,
    )

    # Display chat messages from history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if (msg["role"] == "assistant" and 
                st.session_state.text_to_speech_enabled and 
                st.session_state.is_speaking and 
                idx == len(st.session_state.messages) - 1):
                if st.button("🔇 Stop Reading", key=f"stop_{idx}"):
                    st.session_state.stop_speech_requested = True
                    st.session_state.is_speaking = False
                    st.rerun()

    # Input area with improved layout
    input_container = st.container()
    with input_container:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            text_input = st.chat_input(
                "Type your message or click the microphone to speak",
                key="chat_input",
                disabled=st.session_state.is_recording
            )
        
        with col2:
            if not st.session_state.is_recording:
                if st.button("🎤", help="Click to start speaking", key="start_mic"):
                    # Clear any previous states first
                    st.session_state.voice_input = None
                    st.session_state.current_transcription = None
                    st.session_state.is_speaking = False
                    st.session_state.transcription_complete = False
                    # Then start recording
                    st.session_state.is_recording = True
                    st.session_state.recording_start_time = datetime.now()
                    st.rerun()
            else:
                if st.button("🔴", help="Click to stop recording", key="stop_mic"):
                    # Only attempt final transcription if we don't have one yet
                    if not st.session_state.transcription_complete:
                        final_input = speech_to_text()
                        if final_input:
                            st.session_state.current_transcription = final_input
                            st.session_state.transcription_complete = True
                    
                    # Reset recording states
                    st.session_state.is_recording = False
                    st.session_state.recording_start_time = None
                    
                    # Force immediate rerun to update UI
                    st.rerun()

    # Recording handler with precise timing and feedback
    if st.session_state.is_recording and st.session_state.recording_start_time:
        # Show recording status
        st.markdown(f"""
            <div style='padding: 1rem; border-radius: 0.5rem; background-color: #d32f2f; margin: 1rem 0;'>
                <p style='color: white; margin: 0; font-size: 1.2rem; font-weight: bold;'>
                    🎙️ Recording... (will stop automatically after 3s of silence)
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Only attempt speech recognition if we don't have a transcription yet
        if not st.session_state.transcription_complete:
            voice_input = speech_to_text()
            if voice_input:
                st.session_state.current_transcription = voice_input
                st.session_state.transcription_complete = True
                # Stop recording when we get a transcription
                st.session_state.is_recording = False
                st.session_state.recording_start_time = None
                st.rerun()
        
        # Force rerun to keep UI responsive
        time.sleep(0.1)
        st.rerun()

    # Transcription review and submission
    if st.session_state.current_transcription and not st.session_state.is_recording:
        st.markdown(f"""
            <div style='padding: 1rem; border-radius: 0.5rem; background-color: #1976d2; margin: 1rem 0;'>
                <p style='color: white; margin: 0; font-size: 1.1rem;'>Review your message:</p>
                <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: bold;'>
                    "{st.session_state.current_transcription}"
                </p>
            </div>
        """, unsafe_allow_html=True)

        submit_col, cancel_col = st.columns(2)
        with submit_col:
            if st.button("✅ Submit", use_container_width=True, key="submit_voice"):
                # First clear transcription states
                transcription = st.session_state.current_transcription
                st.session_state.current_transcription = None
                st.session_state.voice_input = None
                st.session_state.transcription_complete = False
                
                # Then process the input and get response
                response, audio_html = process_voice_input(transcription)
                
                # Set speaking state and rerun to update UI
                if audio_html:
                    st.session_state.is_speaking = True
                    st.markdown(audio_html, unsafe_allow_html=True)
                
                st.rerun()

        with cancel_col:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_voice"):
                # Clear states without processing
                st.session_state.current_transcription = None
                st.session_state.voice_input = None
                st.session_state.transcription_complete = False
                st.rerun()

    # Text input handler
    if text_input:
        response, audio_html = process_voice_input(text_input)
        if audio_html:
            st.session_state.is_speaking = True
            st.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()

def process_voice_input(input_text):
    """Helper function to process both voice and text input"""
    try:
        processed_prompt = process_prompt(input_text)
        with st.spinner("Processing..."):
            response = get_ai_response(processed_prompt)
            
        # First update chat history
        st.session_state.messages.append({"role": "user", "content": input_text})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Return the response and audio_html separately
        audio_html = None
        if st.session_state.text_to_speech_enabled:
            audio_html = text_to_speech(response)
        
        return response, audio_html
    
    except ValueError as e:
        st.error(f"Safety check failed: {str(e)}")
        suggestion = suggest_alternative(input_text)
        st.info(f"Try asking instead: '{suggestion}'")
        if st.session_state.text_to_speech_enabled:
            audio_html = text_to_speech(f"Safety check failed. Try asking instead: {suggestion}")
            return None, audio_html
        return None, None


# Main Application Flow
def main():
    # Logo and Title
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/AIretire_Logo.png", width=200)  # Replace with actual logo path
        st.markdown(
            "<h1 style='text-align: center;'>AIretire: <br> Your all-in-one service </br> </h1>",
            unsafe_allow_html=True,
        )

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
    elif st.session_state.current_page == "ai_assistant":  # NEW LINE
        render_ai_assistant()

    # Footer
    st.markdown(
        "<footer>© 2025 AIretire. All rights reserved.</footer>", unsafe_allow_html=True
    )


if __name__ == "__main__":

    main()
