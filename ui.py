import streamlit as st
from resumeparser.preprocessing import pdf_to_images
from resumeparser.vlm import extract_text_from_images
from resumeparser.llm import extract_resume_fields
from resumeparser.schema import ResumeFields
import os
from dotenv import load_dotenv

def save_settings(strategy, model_vlm, model_llm, api_key_vlm, api_key_llm):
    os.environ["PROMTPING_MODE"] = strategy
    os.environ["TEMPERATURE"] = "0.7"
    os.environ["VLM_MODEL"] = model_vlm
    os.environ["LLM_MODEL"] = model_llm
    os.environ["VLM_API_KEY"] = api_key_vlm
    os.environ["LLM_API_KEY"] = api_key_llm

def get_settings()->dict[str, str | None]:
    settings = ["PROMTPING_MODE", "TEMPERATURE", "VLM_MODEL", "LLM_MODEL", "VLM_API_KEY", "LLM_API_KEY"]
    settings = {s:os.environ.get(s) for s in settings}
    return settings

def display_resume_fields(resume_fields:ResumeFields):
    name = st.text_input("Name", value=resume_fields.name or "")
    surname = st.text_input("Surname", value=resume_fields.surname or "")
    current_profession = st.text_input("Current Profession", value=resume_fields.current_profession or "")
    profile_category = st.selectbox("Profile Category", ["", "commercial", "technical"], index=["", "commercial", "technical"].index(resume_fields.profile_category or ""))
    years_experience = st.text_input("Years of Experience", value=str(resume_fields.years_experience))


def main():
    if os.path.exists(".env"):
        load_dotenv(".env")

    st.set_page_config(page_title="Resume Parser Demo", layout="wide")
    st.title("Resume Parser Demo")

    with st.sidebar:
        st.title("Settings")
        strategy = st.sidebar.selectbox("Prompting Mode", ["naive", "cot"])
        cache = st.sidebar.checkbox("Cache", value=True)
        model_vlm = st.sidebar.text_input("VLM Model", value=os.environ.get("VLM_MODEL","No model provided"))
        model_llm = st.sidebar.text_input("LLM Model", value=os.environ.get("LLM_MODEL","No model provided"))
        api_key_vlm = st.sidebar.text_input("VLM API Key", value=os.environ.get("VLM_API_KEY","No API key provided"),)
        api_key_llm = st.sidebar.text_input("LLM API Key", value=os.environ.get("LLM_API_KEY","No API key provided"))

        if st.sidebar.button("Save Settings"):
            save_settings(strategy, model_vlm, model_llm, api_key_vlm, api_key_llm)
            st.success("Settings saved successfully!")
        elif any(x is None for x in get_settings().values()):
            st.error("No settings saved. Please save settings first.")
        else:
            st.success("Settings loaded successfully!")
    
    with st.form("resume_parser_form"):
        uploaded_file = st.file_uploader("Upload a PDF resume", type=["pdf"])
        submitted = st.form_submit_button("Parse Resume")

    if uploaded_file and submitted:        
        with st.spinner("Converting PDF to images..."):
            images = pdf_to_images(uploaded_file.getvalue())

        with st.spinner("Extracting text..."):
            page_texts = extract_text_from_images(model=os.environ.get("VLM_MODEL"),
            images=images,
            strategy=get_settings().get("PROMTPING_MODE","naive"),
            temperature=float(get_settings().get("TEMPERATURE",0.7)),
            cache=cache
            )
            full_text = "\n".join(page_texts)

        with st.spinner("Extracting structured fields..."):
            resume_fields = extract_resume_fields(model=os.environ.get("LLM_MODEL"),
            text=full_text,
            strategy=os.environ.get("PROMTPING_MODE","naive"),
            temperature=float(os.environ.get("TEMPERATURE",0.7)),
            cache=cache
            )

        col1, col2 = st.columns([2, 3])
        with col1:
            st.subheader("Resume Preview")
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i+1}", use_container_width=True)
        with col2:
                st.subheader("Extracted Fields (Editable)")
                display_resume_fields(resume_fields)

                with st.form("edit_fields_form"):
                    submitted = st.form_submit_button("Save Corrections")
                    if submitted:
                        st.success("Corrections saved!")
                


if __name__ == "__main__":
    main()