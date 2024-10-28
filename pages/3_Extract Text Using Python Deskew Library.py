import os
import math
import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
from typing import Tuple, Union
import cv2
import numpy as np
from deskew import determine_skew
from pathlib import Path


def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


def extract_text_from_images(image_paths):
    text = ""
    for image_path in image_paths:
        jpgfile = cv2.imread(image_path)
        grayscale = cv2.cvtColor(jpgfile, cv2.COLOR_BGR2GRAY)
        angle = determine_skew(grayscale)
        rotated = rotate(jpgfile, angle, (0, 0, 0))
        # Deskew the image
        # Perform OCR on the deskewed image
        text += pytesseract.image_to_string(rotated)
        os.remove(image_path)
    return text

def save_as_markdown(text, file_name="output.md"):
    with open(file_name, "w") as md_file:
        md_file.write(text)


def main():
    st.set_page_config(page_title="Extracting Text Using Python Deskew Library")
    st.title("Extracting Text from a PDF Using Python's Deskew Library - by Scott Isaacson")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Convert PDF to a list of images
        output_folder="./images3"
        images = convert_from_bytes(uploaded_file.read(), output_folder=output_folder, fmt="jpg")
        image_paths = [str(f) for f in sorted(Path(output_folder).iterdir()) if f.suffix == ".jpg"]


        # Perform OCR to extract text from the images with deskewing
        st.info("Performing OCR with deskewing, please wait...")
        st.write("Image Paths:", image_paths)
        text = extract_text_from_images(image_paths)

        # Display the extracted text in the app
        st.subheader("Extracted Text")
        st.text_area("Text content", text, height=300)

        # Save the extracted text as a markdown file
        st.download_button(
            label="Download as Markdown",
            data=text,
            file_name="output.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()
