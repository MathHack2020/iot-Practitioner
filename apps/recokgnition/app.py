import streamlit as st
import boto3
import pandas as pd

 


def analyze_image_with_rekognition(image_bytes):
    """Analyzes an image using AWS Rekognition to detect labels."""
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'Bytes': image_bytes.getvalue()},
        MaxLabels=10,
        MinConfidence=75
    )
    return response['Labels']

def display_labels(labels):
    """Displays labels in a DataFrame."""
    if labels:
        data = [{'Name': label['Name'], 'Confidence': f"{label['Confidence']:.2f}%"} for label in labels]
        df = pd.DataFrame(data)
        st.write(df)
    else:
        st.write("No labels detected.")

def main():
    st.title('AWS Rekognition Image Analysis')
    st.write('Upload an image to analyze using AWS Rekognition.')

    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        labels = analyze_image_with_rekognition(uploaded_file)
        st.image(uploaded_file, caption='Uploaded Image', use_container_width=True)
        display_labels(labels)

if __name__ == '__main__':
    main()