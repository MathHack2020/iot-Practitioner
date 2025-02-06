import boto3
import streamlit as st
from langchain_aws import BedrockLLM

#  initialize AWS Bedrock client
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

#  generate insights using AWS Bedrock
def generate_insights_with_bedrock(user_query, data):
    try:
        bedrock_client = get_bedrock_client()
        bedrock_llm = BedrockLLM(model_id="amazon.titan-text-premier-v1:0", client=bedrock_client)
        
        #  generate insights based on the queried data
        resp="You are a data expert responsible for providing precise and concise answers to user questions based solely on the data provided. When a user asks a question, respond only with the direct answer extracted from the data. Do not give any instructions, explanations, or code. Your goal is to deliver the exact information requested in a clear and straightforward manner. "
        prompt = f"{resp}{user_query} : {data.to_string(index=False)}"
        response = bedrock_llm.invoke(prompt)
        return response
    except Exception as e:
        st.error(f"Failed to generate insights using Bedrock: {str(e)}")
        return None