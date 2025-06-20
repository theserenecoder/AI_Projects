# 🌍✈️ AI Travel & Expense Planner

An intelligent AI agent built with **LangChain** and **LangGraph**, designed to provide comprehensive, real-time travel itineraries and expense breakdowns. This project showcases a modular architecture for building robust and scalable AI applications.

---

## ✨ Features

- **Complete Day-by-Day Itineraries**: Generates detailed plans with specific activities and timings.
- **Real-time Weather Integration**: Fetches current weather and multi-day forecasts for the destination.
- **Smart Search Capabilities**: Recommends attractions, restaurants, activities, hotels, and transportation options using external search tools (Google Serper, Tavily, DuckDuckGo).
- **Detailed Cost Management**: Calculates estimated costs (accommodation, food, activities, transport) and provides currency conversion to the user's native currency.
- **User-Centric Planning**: Prioritizes and integrates user preferences (e.g., budget, interests, dietary needs, travel companions, transportation preferences).
- **Modular Architecture**: Designed for maintainability and scalability, separating concerns into distinct Python modules.
- **Interactive Streamlit UI**: A user-friendly web interface for easy interaction.

---

## 🧠 Architecture Overview

The AI Travel & Expense Planner leverages a **modular design**, orchestrating specialized components to process complex queries and generate detailed travel plans.



travel_planner_app/
├── .env                 # Environment variables (API Keys)
├── requirements.txt     # Python dependencies
├── app.py               # Main Streamlit application
└── src/                 # Core Python modules
    ├── __init__.py      # Marks src as a Python package
    ├── config.py        # API Key management
    ├── tools.py         # Definitions of all custom tools (Weather, Currency, Search, Calculator)
    └── agent.py         # LangGraph Agent orchestration logic


---

## ⚙️ How It Works

### `app.py` (Streamlit Interface)
The user interacts with the Streamlit frontend, providing their travel request.

---

### `src/config.py`
Securely loads API keys from either a local `.env` file or Streamlit Cloud's `st.secrets`, ensuring sensitive information remains private.

---

### `src/agent.py` (LangGraph Orchestrator)
The core of the intelligence, powered by LangGraph, which creates a stateful agent.

- Uses a `SystemPrompt` to guide the LLM through a multi-step reasoning process.
- Intelligently routes the query, deciding which tools to invoke based on the current state and the goal (creating a full itinerary).
- Manages the flow to ensure all necessary information is collected before generating the final plan.

---

### `src/tools.py` (Intelligent Tools Hub)
Houses custom Python functions wrapped as LangChain tools, including:

- **Weather Tools**: Fetch real-time current and forecast data.
- **Web Search Tools**: Search for attractions, restaurants, hotels, transportation options.
- **Currency Tools**: Perform currency conversions and budgeting calculations.

The LLM invokes these tools, processes their outputs, and refines its understanding and recommendations iteratively.

---

## ✅ Validation & Output
The agent cycles through LLM reasoning and tool execution until a comprehensive plan is formed. The final output is formatted in Markdown and displayed in the Streamlit app.

---

## 🚀 Getting Started

### 🔧 Prerequisites
- Python 3.11+
- API Keys for:
  - OpenAI (e.g., `gpt-3.5-turbo`)
  - OpenWeatherMap
  - Google Serper *(Optional but recommended)*
  - Tavily *(Optional but recommended)*

---

### 🛠️ Installation

#### Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME  # Replace with your actual repo name
    '''

#### Install dependencies:
    '''bash
    pip install -r requirements.txt
    '''

## 🔐 API Key Configuration
Create a .env file in the root directory of your project and add:
    '''
    OPENAI_API_KEY="your_openai_api_key_here"
    OPENWEATHERMAP_API_KEY="your_openweathermap_api_key_here"
    SERPER_API_KEY="your_google_serper_api_key_here"
    TAVILY_API_KEY="your_tavily_api_key_here"
    '''

## ▶️ Running the Application
From the project root, run:
    '''bash
        streamlit run app.py
    '''
This will launch the app in your default browser.


## 💡 Usage
1. **Launch the App**: Run streamlit run app.py.

2. **Enter Your Query**: Provide details like:
    - Destination
    - Dates (e.g., "next month", "July 10–15")
    - Budget (e.g., "$100/night")
    - Travelers (e.g., "me and two kids")
    - Interests (e.g., "museums", "local food")
    - Preferred currency
    - Transport preferences

3. **Generate Plan**: Click "Generate Trip Plan".

4. **Review**: A complete itinerary is shown with weather, costs, and activities.


## 📈 Example Query
    '''Hey there! I'm planning a 7-day trip to Rome for next May. My hotel budget is around $100 per night. I’d like to know what the weather will be like, what places I can visit, and how much the whole trip might cost. I’ll be paying in Japanese Yen, but my native currency is CAD. Also, I prefer local food and public transportation. Can you plan it all for me?
    '''


## ✉️ Contact
[Ashutosh Sharma : www.linkedin.com/in/ashutoshsharma25]