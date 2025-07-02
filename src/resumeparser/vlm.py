import os
import base64
from typing import List
from PIL import Image
from io import BytesIO
import dspy

VLM_API_BASE = os.getenv("VLM_API_BASE")
VLM_API_KEY = os.getenv("VLM_API_KEY")

class VLMExtractionSignature(dspy.Signature):
    """
    Extract all visible text from the provided image as accurately as possible. Do not translate or summarize; return the recognized text exactly as it appears in the image.
    """
    images: list[dspy.Image] = dspy.InputField(des="The image to extract text from")
    extracted_text: str = dspy.OutputField(des="The extracted text from the image")

class TextExtractor:
    """
    VLM Extractor with configurable prompting strategies (e.g., CoT, Refine) using dspy modules.
    """

    def __init__(self,model:str, strategy:str,temperature=0.7, cache=True):
        # Configure Dspy to use the local VLM endpoint
        if VLM_API_BASE is None or VLM_API_KEY is None:
            raise ValueError("VLM_API_BASE and VLM_API_KEY must be set in the environment variables")
        
        if not isinstance(model,str):
            raise ValueError(f"model must be a string, got {type(model)}")
        
        if model.startswith("gemini/"):
            self.base_vlm = dspy.LM(model, 
                         temperature=temperature,
                         cache=cache,
                         api_key=VLM_API_KEY,
                        )
        else:
            self.base_vlm = dspy.LM(model, 
                            temperature=temperature,
                            cache=cache,
                            api_key=VLM_API_KEY,
                            base_url=VLM_API_BASE,
                            )
        self.strategy = strategy

        assert self.strategy in ["cot", "refine","naive"], "Strategy must be either 'cot' or 'refine'"
    
    def image_to_base64(self,img: Image.Image) -> str:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def preprocess(self, input_data:Image.Image)->dspy.Image:
        """
        Preprocess input: if str, treat as base64-encoded image and convert to bytes.
        If bytes, return as is.
        """
        assert isinstance(input_data, Image.Image), "Input must be a PIL Image."
        buf = BytesIO()
        input_data.convert("RGB").save(buf, format="JPEG")
        image = buf.getvalue()
        return dspy.Image.from_file(image)
    
    def run(self, images:List[Image.Image],):
        """
        Run the extraction inside a dspy.context manager.
        Accepts input_data as base64 string or bytes.
        """

        # You can extend this to support different strategies
        if self.strategy == "cot":
            vlm = dspy.ChainOfThought(VLMExtractionSignature)
        elif self.strategy == "refine":
            vlm = dspy.Refine(VLMExtractionSignature)
        elif self.strategy == "naive":
            vlm = dspy.Predict(VLMExtractionSignature)
        else:
            raise ValueError(f"Invalid strategy: {self.strategy}")

        images = [self.preprocess(image) for image in images]
        try:
            with dspy.context(llm=self.base_vlm):
                result = vlm(images=images).extracted_text
        except Exception as e:
            dspy.configure(lm=self.base_vlm)
            result = vlm(images=images).extracted_text
        return result

def extract_text_from_images(model,images: List[Image.Image],strategy:str="naive",temperature:float=0.7, cache:bool=True) -> List[str]:
    """
    Use Dspy (VLM) to extract text from each image.
    """
    extractor = TextExtractor(model=model, strategy=strategy,temperature=temperature, cache=cache)
    return extractor.run(images)