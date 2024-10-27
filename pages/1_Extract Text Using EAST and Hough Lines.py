import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import cv2
import numpy as np
from scipy.ndimage import rotate

def correct_skew(image, delta=1, limit=12):
    def determine_score(arr, angle):
        data = rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding to create a binary image
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 15
    )

    # Evaluate scores for a range of angles
    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        _, score = determine_score(thresh, angle)
        scores.append(score)

    # Select the angle with the highest score
    best_angle = angles[scores.index(max(scores))]
    return best_angle

def deskew_image(image):
    # Convert the PIL image to a NumPy array
    image_array = np.array(image)

    # Find the best angle to deskew the image
    best_angle = correct_skew(image_array)
    
    # Rotate the image to correct the skew
    (h, w) = image_array.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    deskewed = cv2.warpAffine(image_array, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # Convert back to PIL format for pytesseract compatibility
    deskewed_image = Image.fromarray(cv2.cvtColor(deskewed, cv2.COLOR_BGR2RGB))
    return deskewed_image

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
    st.title("PDF to Markdown Converter with OCR and Deskewing")

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
