import streamlit as st
from resume_parser.preprocessing import pdf_to_images
from resume_parser.vlm import extract_text_from_images
from resume_parser.llm import extract_resume_fields
from resume_parser.schema import ResumeFields
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Resume Parser Demo", layout="wide")
st.title("Resume Parser Demo")

uploaded_file = st.file_uploader("Upload a PDF resume", type=["pdf"])
#language = st.selectbox("Select document language", ["en", "de", "fr"], format_func=lambda x: {"en": "English", "de": "German", "fr": "French"}[x])

if uploaded_file:
    
    with st.spinner("Converting PDF to images..."):
        images = pdf_to_images(uploaded_file.getvalue())

    with st.spinner("Extracting text from images (VLM)..."):
        page_texts = extract_text_from_images(images)
        full_text = "\n".join(page_texts)

    with st.spinner("Extracting structured fields (LLM)..."):
        resume_fields = extract_resume_fields(full_text)

    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("Resume Preview")
        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1}", use_column_width=True)
    with col2:
        st.subheader("Extracted Fields (Editable)")
        with st.form("edit_fields_form"):
            name = st.text_input("Name", value=resume_fields.name or "")
            surname = st.text_input("Surname", value=resume_fields.surname or "")
            current_profession = st.text_input("Current Profession", value=resume_fields.current_profession or "")
            profile_category = st.selectbox("Profile Category", ["", "commercial", "technical"], index=["", "commercial", "technical"].index(resume_fields.profile_category or ""))
            years_experience = st.number_input("Years of Experience", value=resume_fields.years_experience or 0.0, min_value=0.0, step=0.1)
            submitted = st.form_submit_button("Save Corrections")
            if submitted:
                st.success("Corrections saved!")
                # Here you could save or process the corrected data
