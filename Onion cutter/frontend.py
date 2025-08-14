# frontend.py
import streamlit as st
import requests

Headline = st.title("Onion cutter!")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

if st.button("Upload"):
    if uploaded_file is None:
        st.warning("Please upload an image first.")
    else:
        files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

        try:
            resp = requests.post("http://localhost:8000/process", files=files)
            if resp.status_code == 200:
                data = resp.json()
                # Display results from backend
                st.title(data.get("result head", 'No result head'))
                st.image(uploaded_file, caption=data.get('caption', 'Uploaded image'), use_container_width=True)
                st.write(data.get('result body', 'No result body'))
                st.success("Response from backend:")
                st.json(data)
            else:
                st.error(f"Backend error: {resp.status_code}")
                st.write(resp.text)
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
