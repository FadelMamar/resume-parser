from resumeparser.llm import extract_resume_fields
from dotenv import load_dotenv
import os
from examples import EXAMPLE_RESUME_TEXT
load_dotenv("../.env")


def test_field_extractor(resume_text: str = ""):
    if not resume_text:
        # Example resume text
        resume_text = EXAMPLE_RESUME_TEXT
        
    model_name = os.environ.get("LLM_MODEL")
    if not isinstance(model_name, str) or not model_name:
        raise ValueError("LLM_MODEL environment variable must be set and be a string.")
    print("Model name:", model_name)

    # Call the function
    extracted_fields = extract_resume_fields(
        model=model_name,
        text=resume_text,
        strategy="naive",  # or "cot", "refine" if supported
        temperature=0.7,
        cache=True
    )

    # Print the results
    print(extracted_fields)

if __name__ == "__main__":
    test_field_extractor()
