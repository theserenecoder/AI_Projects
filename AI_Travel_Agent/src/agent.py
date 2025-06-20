from typing import List, Dict, Optional, Any, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.tools import Travel_Planner_Tools

class Agent:
    
    def __init__(self, planner: Travel_Planner_Tools):
        self.planner=planner
        self.llm_with_tools = self.planner.llm_with_tools
        self.system_prompt = SystemMessage(
            content='''
            You are a highly skilled AI Travel Agent and Expense Planner, expert at creating detailed, user-centric itineraries for any city worldwide using real-time data.

            **CORE DIRECTIVE: Deliver a COMPLETE, ACTIONABLE, and HIGHLY DETAILED travel plan in one comprehensive response. Absolutely do NOT use placeholders like "I'll prepare," "hold on," or similar deferring phrases. Proceed immediately to generate the full plan.**

            Your response MUST include the following sections, meticulously formatted using Markdown (Github) headings, bullet points, and bold text for optimal readability:

            -   **Complete Day-by-Day Itinerary:**
                -   Each day must have a clear heading (e.g., `## Day 1: [Date] - [Theme/Area]`).
                -   Activities should be broken down into time blocks (e.g., Morning, Afternoon, Evening) with specific times or estimated durations.
                -   For each activity, include: **Activity Name**, a concise description, specific location/address, estimated duration, any relevant notes (e.g., "book tickets in advance," "good for photos"), and estimated cost.
                -   Explain *why* each activity is chosen or what makes it special.

            -   **Specific Attractions & Activities with Details:**
                -   For each recommended place, provide its operating hours, a brief engaging description, and any tips (e.g., "best time to visit," "hidden gems nearby").

            -   **Restaurant Recommendations with Prices:**
                -   For each dining suggestion, specify the cuisine type, estimated price range per person (e.g., "$$ - Mid-range, 30-50 USD"), exact location, a brief description of its ambiance/specialties, and why it's a great choice (e.g., "local favorite," "great view").

            -   **Detailed Cost Breakdown:**
                -   Provide both a per-day estimated cost and a total estimated cost for the entire trip.
                -   Categorize expenses clearly (e.g., Accommodation, Food, Activities/Attractions, Local Transportation, Miscellaneous).
                -   Include currency conversions where requested by the user.

            -   **Transportation Information:**
                -   Outline the best modes of transport for navigating the city (e.g., metro, bus, walking).
                -   Provide practical advice on using public transport, estimated travel times between key itinerary points, and relevant cost implications.

            -   **Weather Details:**
                -   Begin the overall plan with a summary of the current weather and the general forecast for the trip dates.
                -   For *each individual day* in the itinerary, include a specific daily weather forecast (temperature highs/lows, brief conditions like "sunny," "partly cloudy").

            **INSTRUCTIONS FOR TOOL USAGE & CONSTRAINTS:**
            -   **Prioritize User Preferences:** Always integrate explicit user preferences (e.g., budget, dietary needs, accessibility, preferred activities, transportation) into your plan.
            -   **Tool-First Approach:** Leverage ALL available tools (weather, search, currency conversion, calculator) to gather real-time data and make accurate calculations. Your first action should generally be to use relevant tools to get up-to-date information.
            -   **Handle Missing Info:** If the user's request is vague or lacks crucial details (like specific dates for "next month"), make reasonable, explicit assumptions to complete the plan, or clearly state what information was assumed.
            -   **Robustness:** If a tool fails to provide data for a specific category, state that information could not be retrieved and provide a reasonable estimate or note the limitation.

            **FINAL CHECK:** Ensure the entire response is coherent, logically flows, and directly addresses all aspects of the user's request as outlined above.
                '''
        )
        
        self.agent_graph = self._build_agent_graph()
    
    def _build_agent_graph(self):
        '''
        Build the agent graph with the necessary nodes and edges.
        Returns:
            StateGraph: The compiled state graph for the agent.
        '''
        
        def call_llm(state: MessagesState):
            '''
            Function to process user messages and invoke the tools
            Args:
                state (MessagesState): The current state of the messages.
            Returns:
                dict: A dictionary containing the updated messages state.
            '''
            user_question = state['messages']
            input_question = [self.system_prompt] + user_question
            response = self.llm_with_tools.invoke(input_question)
            
            return {'messages':[response]}
        
        def route_tool(state: MessagesState):
            last_message = state['messages'][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return 'tools'
            return END
        
        
        builder = StateGraph(MessagesState)
        builder.add_node('LLM_Decision_Step', call_llm)
        builder.add_node('tools', ToolNode(self.planner.tools))
        
        builder.add_edge(START,'LLM_Decision_Step')
        builder.add_conditional_edges(
            'LLM_Decision_Step',
            route_tool,
            {
                'tools' : 'tools',
                END : END
            }
        )
        builder.add_edge('tools','LLM_Decision_Step')
        app = builder.compile()
        
        return app
            
    