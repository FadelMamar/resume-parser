from pdf2image import convert_from_path,convert_from_bytes
from typing import List
from PIL import Image


def pdf_to_images(pdf_path: str|bytes, dpi: int = 300) -> List[Image.Image]:
    """
    Convert a PDF file to a list of PIL Images, one per page.
    Args:
        pdf_path (str): Path to the PDF file.
        dpi (int): Dots per inch for image quality.
    Returns:
        List[Image.Image]: List of images, one per PDF page.
    """
    if isinstance(pdf_path, str):
        images = convert_from_path(pdf_path, dpi=dpi)
    elif isinstance(pdf_path, bytes):
        images = convert_from_bytes(pdf_path, dpi=dpi)
    else:
        raise ValueError("pdf_path must be a string or bytes")
    return images
