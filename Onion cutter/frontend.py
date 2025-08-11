# frontend.py
import streamlit as st
import requests

st.title("Streamlit ↔ FastAPI Connection Demo")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
note = st.text_input("Add a note", "Test note")

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

if st.button("Upload"):
    if uploaded_file is None:
        st.warning("Please upload an image first.")
    else:
        files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"note": note}

        try:
            resp = requests.post("http://localhost:8000/process", files=files, data=data)
            if resp.status_code == 200:
                st.success("Response from backend:")
                st.json(resp.json())
            else:
                st.error(f"Backend error: {resp.status_code}")
                st.write(resp.text)
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
