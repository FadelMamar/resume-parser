import os
import dspy
from .schema import ResumeFields

LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_API_KEY = os.getenv("LLM_API_KEY")

class ResumeExtractionSignature(dspy.Signature):
    """
    Extract the following structured fields from the provided resume text as accurately as possible:
    - name: The candidate's first name.
    - surname: The candidate's last name.
    - current_profession: The candidate's current job title or profession.
    - profile_category: "commercial" or "technical" (choose the most appropriate).
    - years_experience: The number of years of professional experience (as a number).

    Return only the information explicitly present in the text. If a field is not found, leave it blank or null. Do not infer or guess missing information. Do not summarize or translate; extract the fields exactly as they appear.

    Example:
    Input text:
    "Jane Doe is a software engineer with 5 years of experience in backend development. She is seeking technical roles."

    Output:
    {
        "name": "Jane",
        "surname": "Doe",
        "current_profession": "software engineer",
        "profile_category": "technical",
        "years_experience": 5
    }
    """
    text: str = dspy.InputField(des="The text to extract fields from")
    extracted_fields: ResumeFields = dspy.OutputField(des="The extracted fields from the resume")

class FieldExtractor:
    """
    LLM Field Extractor with configurable prompting strategies (e.g., CoT, Refine) using dspy modules.
    """
    def __init__(self, model:str, strategy: str, temperature=0.7, cache=True):
        if LLM_API_BASE is None or LLM_API_KEY is None:
            raise ValueError("LLM_API_BASE and LLM_API_KEY must be set in the environment variables")
        self.base_llm = dspy.LM(
            model,
            temperature=temperature,
            cache=cache,
            api_key=LLM_API_KEY,
            base_url=LLM_API_BASE,
        )
        self.strategy = strategy
        assert self.strategy in ["cot", "refine", "naive"], "Strategy must be either 'cot', 'refine', or 'naive'"

    def run(self, text: str) -> ResumeFields:
        """
        Run the extraction inside a dspy.context manager.
        Accepts resume text, returns ResumeFields.
        """
        if self.strategy == "cot":
            extractor = dspy.ChainOfThought(ResumeExtractionSignature)
        elif self.strategy == "refine":
            extractor = dspy.Refine(ResumeExtractionSignature)
        elif self.strategy == "naive":
            extractor = dspy.Predict(ResumeExtractionSignature)
        else:
            raise ValueError(f"Invalid strategy: {self.strategy}")
        with dspy.context(llm=self.base_llm):
            result = extractor(text=text).extracted_fields
        return ResumeFields(
            name=result.name or None,
            surname=result.surname or None,
            current_profession=result.current_profession or None,
            profile_category=result.profile_category or None,
            years_experience=float(result.years_experience) if result.years_experience else None,
        )

def extract_resume_fields(model, text: str, strategy: str = "naive", temperature: float = 0.7, cache: bool = True) -> ResumeFields:
    extractor = FieldExtractor(model=model, strategy=strategy, temperature=temperature, cache=cache)
    return extractor.run(text) 