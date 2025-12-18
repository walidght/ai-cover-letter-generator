import streamlit as st
import requests
import json
import os

# Constants
API_URL = "http://localhost:8000"
PROFILE_FILE = "user_profile.json"

# --- Page Config ---
st.set_page_config(page_title="Cover Letter Generator", layout="centered")

# --- Helper: Load/Save Profile ---
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {"name": "", "email": "", "phone": ""}


def save_profile(data):
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f)
    st.toast("Profile saved successfully!", icon="✅")


# --- Session State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'generated_letter' not in st.session_state:
    st.session_state.generated_letter = ""
if 'offer_data' not in st.session_state:
    st.session_state.offer_data = {
        "job_title": "",
        "company_name": "",
        "language": "English"
    }

# Load profile into state if not present
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = load_profile()


def go_to_step(step_num):
    st.session_state.step = step_num


# --- SIDEBAR: PERSONAL INFO ---
with st.sidebar:
    st.header("👤 Your Profile")
    st.info("This data is used to fill your contact info in the PDF.")

    with st.form("profile_form"):
        p_name = st.text_input(
            "Full Name", value=st.session_state.user_profile.get("name", ""))
        p_email = st.text_input(
            "Email", value=st.session_state.user_profile.get("email", ""))
        p_phone = st.text_input(
            "Phone Number", value=st.session_state.user_profile.get("phone", ""))

        save_btn = st.form_submit_button("Save Profile")

        if save_btn:
            new_profile = {"name": p_name, "email": p_email, "phone": p_phone}
            st.session_state.user_profile = new_profile
            save_profile(new_profile)

# --- MAIN UI ---
st.title("📄 Smart Cover Letter Generator")

# === TAB 1: INPUT DETAILS ===
if st.session_state.step == 1:
    st.header("Step 1: Offer Details")

    with st.form("offer_form"):
        col1, col2 = st.columns(2)
        with col1:
            job_title_input = st.text_input("Job Title", value=st.session_state.offer_data.get(
                "job_title", ""), placeholder="e.g. Senior Data Scientist")
        with col2:
            company_name_input = st.text_input("Company Name", value=st.session_state.offer_data.get(
                "company_name", ""), placeholder="e.g. Google")

        language_input = st.selectbox(
            "Language",
            ["English", "French"],
            index=0 if st.session_state.offer_data.get(
                "language") == "English" else 1
        )

        description = st.text_area(
            "Offer Description", height=200, placeholder="Paste the job description here...")

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            submit_ai = st.form_submit_button(
                "Generate with AI 🚀", type="primary", use_container_width=True)
        with b_col2:
            submit_manual = st.form_submit_button(
                "Write Manually ✍️", use_container_width=True)

        # --- Logic for AI Generation ---
        if submit_ai:
            if not job_title_input or not company_name_input or not description:
                st.error("Please fill in all fields for AI generation.")
            else:
                # Combine offer data with user profile data
                payload = {
                    "job_title": job_title_input,
                    "company_name": company_name_input,
                    "language": language_input,
                    "offer_description": description,
                    "user_name": st.session_state.user_profile.get("name", ""),
                    "user_email": st.session_state.user_profile.get("email", ""),
                    "user_phone": st.session_state.user_profile.get("phone", "")
                }

                with st.spinner("Generating your cover letter..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/generate-letter", json=payload)
                        if response.status_code == 200:
                            st.session_state.generated_letter = response.json().get("letter")
                            st.session_state.offer_data = payload
                            st.session_state.step = 2
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error(
                            "Could not connect to backend. Is FastAPI running?")

        # --- Logic for Manual Mode ---
        if submit_manual:
            st.session_state.offer_data = {
                "job_title": job_title_input,
                "company_name": company_name_input,
                "language": language_input,
                "user_name": st.session_state.user_profile.get("name", ""),
                "user_email": st.session_state.user_profile.get("email", ""),
                "user_phone": st.session_state.user_profile.get("phone", "")
            }
            if not st.session_state.generated_letter:
                st.session_state.generated_letter = ""
            st.session_state.step = 2
            st.rerun()

# === TAB 2: VALIDATE & EXPORT ===
elif st.session_state.step == 2:
    st.header("Step 2: Review & Export")

    if st.button("← Back to Offer", help="Go back to edit offer details"):
        go_to_step(1)
        st.rerun()

    st.divider()

    st.caption("Confirm these details for the PDF header:")
    col_a, col_b, col_c = st.columns([2, 2, 1])

    with col_a:
        final_job_title = st.text_input(
            "Job Title", value=st.session_state.offer_data.get("job_title", ""))
    with col_b:
        final_company_name = st.text_input(
            "Company Name", value=st.session_state.offer_data.get("company_name", ""))
    with col_c:
        final_language = st.selectbox(
            "Language",
            ["English", "French"],
            index=0 if st.session_state.offer_data.get(
                "language") == "English" else 1
        )

    st.divider()

    st.info("Edit or paste your letter below. When satisfied, click Export.")

    edited_letter = st.text_area(
        "Cover Letter Content",
        value=st.session_state.generated_letter,
        height=500,
        placeholder="Dear Hiring Manager,\n\nI am writing to express my interest..."
    )

    if st.button("Export to PDF 📥", type="primary"):
        if not final_job_title.strip() or not final_company_name.strip():
            st.error(
                "❌ You must enter a **Job Title** and **Company Name** above to generate the PDF.")
        elif not edited_letter.strip():
            st.error("❌ The cover letter content is empty.")
        else:
            # Prepare full payload including user profile
            pdf_payload = {
                "job_title": final_job_title,
                "company_name": final_company_name,
                "language": final_language,
                "edited_letter": edited_letter,
                "user_name": st.session_state.offer_data.get("user_name", ""),
                "user_email": st.session_state.offer_data.get("user_email", ""),
                "user_phone": st.session_state.offer_data.get("user_phone", "")
            }

            with st.spinner("Generating PDF..."):
                try:
                    response = requests.post(
                        f"{API_URL}/generate-pdf", json=pdf_payload)
                    if response.status_code == 200:
                        st.success("PDF Generated successfully!")
                        safe_company = final_company_name.replace(" ", "_")
                        st.download_button(
                            label="Download PDF",
                            data=response.content,
                            file_name=f"Cover_Letter_{safe_company}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to generate PDF.")
                except Exception as e:
                    st.error(f"Error: {e}")
