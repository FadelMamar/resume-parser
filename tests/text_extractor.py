from PIL import Image
from resumeparser.vlm import extract_text_from_images
from resumeparser.preprocessing import pdf_to_images
from dotenv import load_dotenv
import os
from examples import EXAMPLE_RESUME_PATH
load_dotenv("../.env")

def test_text_extractor(cv_path:str=EXAMPLE_RESUME_PATH):

    # Example: Load images (replace with your actual image paths)
    images = pdf_to_images(cv_path)

    model_name = os.environ.get("VLM_MODEL")

    print("Model name:", model_name)

    # Call the function
    extracted_texts = extract_text_from_images(
        model=model_name,
        images=images,
        strategy="naive",  # or "cot", "refine" if supported
        temperature=0.7,
        cache=True
    )

    # Print the results
    print(extracted_texts)

if __name__ == "__main__":
    test_text_extractor()