import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from timeStream_Query import query_timestream_data, timestream_response_to_dataframe
from bedrock_insights import generate_insights_with_bedrock

#  display AWS TimeStream data and interact with LLM
def timestream_app():
    st.title("AWS TimeStream Data Viewer")

    # Query data from AWS TimeStream
    response = query_timestream_data()
    df = timestream_response_to_dataframe(response)
    # df['time'] = pd.to_datetime(df['time'])
    # df = df.pivot(index='time', columns=[['sensor_type', "location"]], values='value')

# Reset the index to turn device_id into a column
    # df.reset_index(inplace=True)


    if df.empty:
        st.warning("No data found in TimeStream table.")
    else:
        # Text box for user to interact with data using LLM
        st.subheader("Ask Questions about the Data")
        user_query = st.text_area("Enter your query about the data:")
        
        if st.button("Get LLM Response") and user_query:
            # Generate insights using AWS Bedrock based on user input
            st.subheader("LLM Response to User Query")
            llm_prompt = f"Based on the following data, answer the user's query: {user_query}. Data: {df.to_string(index=False)}"
            llm_response = generate_insights_with_bedrock(user_query, df)
            
            if llm_response:
                st.markdown(f"**{llm_response}**")
                # st.write(llm_response)
            else:
                st.warning("No response could be generated.")
        
        # Generate initial insights using AWS Bedrock
        # st.subheader("Generated Insights from Bedrock")
        # insights = generate_insights_with_bedrock(df)
        # if insights:
        #     st.markdown(f"**{insights}**")
        # else:
        #     st.warning("No insights could be generated.")
        
        # Configure AgGrid to display the data
        st.subheader("TimeStream Data Table")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False, groupable=True)
        gb.configure_selection('single', use_checkbox=True)
        grid_options = gb.build()

        AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            fit_columns_on_grid_load=True,
            height=400,
            width='100%'
        )

if __name__ == "__main__":
    timestream_app()

