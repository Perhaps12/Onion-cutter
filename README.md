Upload an image and the app generates a fake news article that goes along with it

Small project as an introduction to app development in python  to learn about frontend/backend interactions & different types of AI models  
Libraries used: streamlit, fastapi, transformers  
  
**Process:**
- Uses streamlit as a frontend user interface which allows uploading an image
- Image is uploaded to the backend using FastAPI
- Uses AI model "nlpconnect" to generate a caption from the user inputted image
- Uses AI model "google flan t5" to generate body text/headline from the caption
- Displays the results back on the frontend to the user

Both models were chosen because they were free & convenient choices
