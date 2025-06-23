from transformers import pipeline
import streamlit as st

@st.cache_resource
def get_sentiment_model():
    return pipeline("sentiment-analysis")

def get_sentiment_score(text):
    model = get_sentiment_model()
    result = model(text)[0]
    return result["label"], round(result["score"], 2)
