import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import cv2
import numpy as np

def deskew_image(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Invert colors for better detection
    gray = cv2.bitwise_not(gray)

    # Use thresholding to create a binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find coordinates of all non-zero pixels
    coords = np.column_stack(np.where(binary > 0))

    # Compute the angle of the minimum area rectangle containing the text
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotate the image to correct the skew
    (h, w) = gray.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(np.array(image), M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Convert back to PIL format for pytesseract compatibility
    return deskewed

def extract_text_from_images(images):
    text = ""
    for image in images:
        # Deskew the image
        deskewed_image = deskew_image(image)
        # Perform OCR on the deskewed image
        text += pytesseract.image_to_string(deskewed_image)
    return text

def save_as_markdown(text, file_name="output.md"):
    with open(file_name, "w") as md_file:
        md_file.write(text)

def main():
    st.set_page_config(page_title="Extracting Text Using OpenCV Minimum Area Rectangle")
    st.title("Extracting Text from a PDF Using OpenCV Minimum Area Rectangle - by Scott Isaacson")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Convert PDF to a list of images
        images = convert_from_bytes(uploaded_file.read(), output_folder="./images", fmt="png")


        # Perform OCR to extract text from the images with deskewing
        st.info("Performing OCR with deskewing, please wait...")
        text = extract_text_from_images(images)

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

