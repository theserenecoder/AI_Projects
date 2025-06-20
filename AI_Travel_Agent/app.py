import os
import streamlit as st
from datetime import date,datetime
from langchain_core.messages import HumanMessage

from src.config import Config
from src.tools import Travel_Planner_Tools
from src.agent import Agent


## Streamlit App

st.set_page_config(page_title="AI Travel & Expense Planner", layout="wide")

st.title("🌍 AI Travel & Expense Planner")
st.markdown("Your smart assistant for planning comprehensive trips worldwide!")

st.markdown("---")
st.subheader("Plan Your Next Adventure!")
st.info("API keys are loaded from your `.env` file (for local development) or Streamlit secrets (for deployment). Please ensure they are set up correctly.")

user_query = st.text_area(
    "Tell me about your trip (e.g., destination, dates, budget, interests, travelers):", 
    height=150,
    value=f"Hey there! I'm planning a 7-day trip to Rome for next May. My hotel budget is around $100 per night. I’d like to know what the weather will be like, what places I can visit, and how much the whole trip might cost. I’ll be paying in Japanese Yen, but my native currency is CAD. Also, I prefer local food and public transportation. Can you plan it all for me?."
)

if st.button("Generate Trip Plan"):
    # Load API keys using the Config class
    config_instance = Config()
    api_keys = config_instance.get_api_keys()

    # Basic check for essential API keys (from config)
    #if not api_keys.get('openai_api_key') or not api_keys.get('weather_api_key'):
       # st.warning("Essential API keys (OpenAI, OpenWeatherMap) are not set. Please ensure they are configured in your `.env` file or Streamlit secrets.")
   # else:
   
    st.info("Generating your personalized trip plan. This might take a moment as I gather real-time data...")
    # Use a spinner for better UX during long operations
    with st.spinner("Thinking and gathering data... This can take a minute for complex plans."):
        try:
            # Initialize Travel_Planner_Tools and Agent
            planner = Travel_Planner_Tools(config=api_keys)
            
            if planner.llm_with_tools is None:
                st.error("Error: The AI model could not be initialized. Please check your OpenAI API key and ensure it's valid.")
            else:
                agent_instance = Agent(planner=planner)
                
                # Invoke the LangGraph agent
                # Initial input for LangGraph is a HumanMessage
                response_state = agent_instance.agent_graph.invoke({'messages': [HumanMessage(content=user_query)]})
                
                # The final output is the content of the last message in the state
                final_output_message = response_state['messages'][-1].content
                
                st.subheader("Your Complete Trip Plan:")
                st.markdown(final_output_message) # Render markdown output
                st.success("Trip plan generated successfully!")

        except Exception as e:
            st.error(f"An unexpected error occurred during trip planning: {e}")
            st.info("Please review your API keys and the details of your request.")

st.markdown("---")
st.caption("Powered by LangChain, LangGraph, OpenAI, OpenWeatherMap, Google Serper, and Tavily.")

