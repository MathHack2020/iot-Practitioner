import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError
# Function to initialize AWS TimeStream client
def get_timestream_client():
    return boto3.client('timestream-query', region_name='us-east-1')

# Function to query data from AWS TimeStream
def query_timestream_data():
    query_string = """
    SELECT * FROM "DTStreamData"."DtStreamTable"
    """
    try:
        timestream_client = get_timestream_client()
        response = timestream_client.query(QueryString=query_string)
        return response
    except ClientError as e:
        st.error(f"Failed to query TimeStream: {e.response['Error']['Message']}")
        return None

#  convert TimeStream query response to DataFrame
def timestream_response_to_dataframe(response):
    if response is None:
        return pd.DataFrame()
    
    columns = [column['Name'] for column in response['ColumnInfo']]
    rows = []
    for row in response['Rows']:
        data = [col.get('ScalarValue', None) for col in row['Data']]
        rows.append(data)
    
    df = pd.DataFrame(rows, columns=columns)
    
    # Transpose the data to put measure names as features
    if 'measure_name' in df.columns and 'measure_value::varchar' in df.columns:
        df = df.pivot(index='time', columns='measure_name', values='measure_value::varchar').reset_index()
    
    return df

response = query_timestream_data()
df = timestream_response_to_dataframe(response)
st.write(df)

