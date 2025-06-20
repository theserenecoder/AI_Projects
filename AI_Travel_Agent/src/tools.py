import requests
import streamlit as st
from typing import  List,Optional, Any, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import  DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import date, datetime

## Weather Class
class Check_Weather:
    def __init__(self,api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.openweathermap.org/data/2.5/'
        
    def get_weather(self, city: str) -> Dict[str, Any]:
        ''' Get the current weather for a given city.'''
        try:
            self.url = f'{self.base_url}weather?q={city}&units=metric&appid={self.api_key}'
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f'Error: {str(e)}')
            return {'Error': str(e)}
        
    def get_forecast(self, city: str, days:int) -> Dict[str, Any]:
        ''' Get the weather forecast for a given city.'''
        try:
            num_intervals = days * 8  # OpenWeatherMap API returns 8 forecasts per day
            self.url = f'{self.base_url}/forecast?q={city}&cnt={num_intervals}&units=metric&appid={self.api_key}'
            
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f'Error: {str(e)}')
            return {'Error': str(e)}
    
    

## Currency Converter Class
class Currency_Converter:
    
    def __init__(self):
        self.base_url = 'https://api.frankfurter.dev/v1/latest'
        
    def convert_currency(self,amount:float, from_currency: str, to_currency: str ) -> float:
        ''' Convert currency from one to another.'''
        try:
            url = f'{self.base_url}?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            return result['rates'][to_currency]
        except Exception as e:
            st.error(f'Error: {str(e)}')
            return None


## Calculator Class
class Calculator:
    
    def add(self,*costs: float) -> float:
        '''
        Sum all the given costs.
        
        Args:
            *costs: List of costs to add

        Returns:
            float: Sum all costs.
        '''
        return sum(costs)
    
    def multiply(self, *costs:float) -> float:
        '''
        Multiply given costs.
        
        Args:
            *costs: List of costs to multiply
        
        Returns:
            float: Product of all costs.
        '''
        result = 1
        for cost in costs:
            result *=cost
        return result
    
    
    def calculate_daily_budget(self,total_cost: float, days: int) -> float:
        '''
        Calculate the daily budget based on total cost and number of days.
        Args:
            total_cost (float): Total cost of the trip.
            days (int): Number of days for the trip.
        Returns:
            float: Daily budget for the trip.
        '''
        if days==0:
            return 0.0
        return total_cost / days

class Travel_Planner_Tools:
    
    def __init__(self, config: dict):
        self.config = config
        self.weather_service = Check_Weather(api_key=self.config.get('weather_api_key'))
        self.currency_converter  = Currency_Converter()
        self.calculator = Calculator()
        
        ## Initializing search tools
        self.duckduck_search = DuckDuckGoSearchRun()
        
        try:
            self.serp_search = GoogleSerperAPIWrapper(serper_api_key=self.config.get('serper_api_key'))
        except Exception as e:
            st.error(f'Error initializing GoogleSerperAPIWrapper: {str(e)}')
            self.serp_search = None
        
        try:
            self.tavily_search = TavilySearchResults(max_results=5, tavily_api_key=self.config.get('tavily_api_key'))
        except Exception as e:
            st.error(f'Error initializing TavilySearchResults: {str(e)}')
            self.tavily_search = None
            
        ## Initializing llm
        try:
            self.llm = ChatOpenAI(model = 'o3-mini', openai_api_key = self.config.get('openai_api_key'))
        except Exception as e:
            st.error(f'Error initializing ChatOpenAI: {str(e)}')
            self.llm = None
        
        
        if self.llm:
            self.tools = self._travel_planning_tools()
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.tools=[]
            self.llm_with_tools = None
        

        
        ## Initializing tools
    def _travel_planning_tools(self) -> List:
        '''
        Initialize and return the list of tools for travel planning.
        Returns:
            List: List of tools for travel planning.
        '''
        ## Defining Pydantic model or structured input to get_day_plan tool
        class DayPlanItem(BaseModel):
            time: str = Field(...,description='Estimated time of the activity (e.g.,9:00 AM - 11:00 AM).')
            activity: str = Field(..., description = 'Description of the activity (e.g., Visit Eiffel Tower, Lunch at Le Comptoir).')
            location: Optional[str] = Field(None, description= 'Specific location or address of the activity.')
            notes: Optional[str] = Field(None, description='Any sepcific notes or recommendations for the activity (e.g., Book tickets in advance, Try the local cuisine).')
            estimated_cost: Optional[str] = Field(None, description='Estimated cost of the activity (e.g., 20 USD, 50 EUR).')
            
        class DayPlanInput(BaseModel):
            date: str = Field(..., description="The date for which the plan is being generated (YYYY-MM-DD).")
            day_number: int = Field(..., description="The number of the day in the itinerary (e.g., 1 for Day 1).")
            plan_items: List[DayPlanItem] = Field(..., description="A list of planned activities for the day, in chronological order, following the DayPlanItem schema.")
            summary: Optional[str] = Field(None, description="A brief summary of the day's plan.")
            weather_forcast: Optional[str] = Field(None, description="Weather forecast for the day, if available.")
        
        ## Defining the main input model for the full itinerary input
        class FullItinearyInput(BaseModel):
            destination: str=Field(...,description='Main destination city for the trip')
            start_date: str =Field(...,description='Start date of the trip in YYYY-MM-DD format')
            end_date: str=Field(...,description='End date of the trip in YYYY-MM-DD format')
            total_days: str=Field(...,description='Total number of days for the trip')
            daily_plans: List[str]=Field(...,description='A list of formatted strings where each string represents a daily plan generated by the get_day_pan tool.')
            overall_summary: Optional[str] = Field(None,description='An optional overall summary of the trip')
            budget_information: Optional[str] = Field(None,description='An optional budget information for the trip (e.g., Mid-range, Estimated total : XX)')
            overall_weather_summary: Optional[str] =Field(None,description='Optional overall current weather and forcast information of the destination')
        
        @tool
        def search_attraction(city: str) -> str:
            ''' Search for top tourist attractions in a city.
            Args:
                city (str): Name of the city to search for attractions.
            Returns:
                str: Search results for top tourist attractions in the city.
            '''
            query = f'Top tourist attractions in {city}'
            
            ## Primary Tool: GoogleSerperAPIWrapper
            ## Secondary Tool: TavilySearchResults
            try:
                if self.serp_search:
                    results = self.serp_search.run(query)
                    if results:
                        return f'Top attraction in {city} : {results}'
            except Exception as e:
                st.error(f'Error in Serper Search (attraction): {str(e)}')
            
            try:
                if self.tavily_search:
                    results = self.tavily_search.invoke(query)
                    if results:
                        formatted_result = "\n".join([f'Source: {r['url']}\nContent: {r['content']}' for r in results])
                        if formatted_result:
                            return f'Top attraction in {city} : {formatted_result}'
            except Exception as e:
                st.error(f'Error in Tavily Search: {str(e)}')
                
            return f'Top attraction in {city} not found'

        
        @tool
        def search_restaurant(city: str) -> str:
            ''' Search for top restaurants in a city.
            Args:
                city (str): Name of the city to search for restaurants.
            Returns:
                str: Search results for top restaurants in the city.
            '''
            query = f'Top restaurants in {city}'
            
            ## Primary Tool: GoogleSerperAPIWrapper
            ## Secondary Tool: TavilySearchResults
            try:
                if self.serp_search:
                    results = self.serp_search.run(query)
                    if results:
                        return f'Top restaurant in {city} : {results}'
            except Exception as e:
                st.error(f'Error in Serper Search (restaurant): {str(e)}')
            
            try:
                if self.tavily_search:
                    results = self.tavily_search.invoke(query)
                    if results:
                        formatted_result = "\n".join([f'Source: {r['url']}\nContent: {r['content']}' for r in results])
                        if formatted_result:
                            return f'Top restaurant in {city} : {formatted_result}'
            except Exception as e:
                st.error(f'Error in Tavily Search: {str(e)}')
                
            return f'Top restaurant in {city} not found'
                
        @tool
        def search_activity(city: str) -> str:
            ''' Search for top activities in a city.
            Args:
                city (str): Name of the city to search for activities.
            Returns:
                str: Search results for top activities in the city.
            '''
            query = f'Top activities in {city}'
            ## Primary Tool: GoogleSerperAPIWrapper
            ## Secondary Tool: TavilySearchResults
            try:
                if self.serp_search:
                    results = self.serp_search.run(query)
                    if results:
                        return f'Top activities in {city} : {results}'
            except Exception as e:
                st.error(f'Error in Serper Search (activity): {str(e)}')
            
            try:
                if self.tavily_search:
                    results = self.tavily_search.invoke(query)
                    if results:
                        formatted_result = "\n".join([f'Source: {r['url']}\nContent: {r['content']}' for r in results])
                        if formatted_result:
                            return f'Top activities in {city} : {formatted_result}'
            except Exception as e:
                st.error(f'Error in Tavily Search: {str(e)}')
                
            return f'Top activities in {city} not found'
        
        @tool
        def search_transport(city: str) -> str:
            ''' Search for means of transportation in a city.
            Args:
                city (str): Name of the city to search for transportation options.
            Returns:
                str: Search results for means of transportation in the city.
            '''
            query = f'Means of transport in {city}'
            ## Primary Tool: GoogleSerperAPIWrapper
            ## Secondary Tool: DuckDuckGoSearchRun
            try:
                if self.serp_search:
                    results = self.serp_search.run(query)
                    if results:
                        return f'Means of transport in {city} : {results}'
            except Exception as e:
                st.error(f'Error in Serper Search (transport): {str(e)}')
            try:
                if self.duckduck_search:
                    results = self.duckduck_search.invoke(query)
                    if results:
                        return f'Means of transport in {city} : {results}'
            except Exception as e:
                st.error(f'Error in DuckDuckGo Search: {str(e)}')
            return f'Means of transport in {city} not found'
        
        @tool
        def get_current_weather(city:str) -> str:
            ''' Get the current weather afor a city.
            Args:
                city (str): Name of the city to get weather information.
            Returns:
                str: Current weather for the city.
            '''
            try:
                current_weather = self.weather_service.get_weather(city)
                if current_weather and 'main' in current_weather and 'weather' in current_weather:                                 
                    current_description=current_weather['weather'][0]['description']
                    current_temp  = current_weather['main']['temp']
                    return f'Current weather in {city} : {current_temp}°C, {current_description}'
                return f'Current weather in {city} not found'
            except Exception as e:
                st.error(f'Error getting current weather: {str(e)}')
                return f'Current weather in {city} not found due to error'
                
                
        @tool
        def get_weather_forcast(city:str, days: int = 5) -> Dict[str, Any]:
            ''' Get the weather forecast for a city.
            Args:
                city (str): Name of the city to get weather information.
                days (int): Number of days for the forecast
            Returns:
                Dict[str, Any]: Raw Json weather forecast data.
            '''
            try:
                weather_forecast = self.weather_service.get_forecast(city, days)  
                if weather_forecast and 'list' in weather_forecast:
                      return weather_forecast
                return {"error": f'Weather forecast for {city} not found'}
                '''
                summary = []
                for i in weather_forecast['list']:
                    date = i['dt_txt']
                    temperature = i['main']['temp']
                    description = i['weather'][0]['description']
                    summary.append(f'{date} :  {temperature}°C,{description}')
                return f'Weather forecast for {city}:\n' + '\n'.join(summary)'''
                
            except Exception as e:
                st.error(f'Error getting weather forecast: {str(e)}')
                return f'Weather forecast for {city} not found due to error'
        
        @tool
        def search_hotels(city: str, check_in_date: Optional[str]=None, check_out_date: Optional[str]=None) -> str:
            ''' Search for top hotels in a city.
            Args:
                city (str): Name of the city to search for hotels.
                check_in_date (str, optional): Check-in date in YYYY-MM-DD format.
                check_out_date (str, optional): Check-out date in YYYY-MM-DD format.
            Returns:
                str: Search results for hotels in the city, including price and booking availability if found.
            '''
            query = f'Mid range hotels in {city}'
            if check_in_date and check_out_date:
                query += f' from {check_in_date} to {check_out_date}'
            query += '. Name of hotel and current price per night booking availability'            
            ## Primary Tool: GoogleSerperAPIWrapper
            ## Secondary Tool: DuckDuckGoSearchRun
            try:
                if self.serp_search:
                    results = self.serp_search.run(query)
                    if results:
                        return f'Hotels in {city} : {results}'
            except Exception as e:
                st.error(f"Error in Serper Search: {str(e)}")
            try:
                if self.duckduck_search:
                    results = self.duckduck_search.invoke(query)
                    if results:
                        return f'Hotels in {city} : {results}'
            except Exception as e:
                st.error(f'Error in DuckDuckGo Search: {str(e)}')
            return f'Hotels in {city} not found'
        
        @tool
        def hotel_cost(price_per_night: float, days:int) -> float:
            ''' Calculate the total cost of hotel stay.
            Args:
                price_per_night (float): Price per night for the hotel.
                days (int): Number of days for the hotel stay.
            Returns:
                float: Total cost of the hotel stay.
            '''
            return self.calculator.multiply(price_per_night, days)
        
        @tool
        def add_costs(*costs: float) -> float:
            '''
            Add multiple costs together
            
            Args:
                *costs (float): List of costs to be sumed up
                
            Returns:
                float: Total cost
            '''
            return self.calculator.add(*costs)
        
        @tool
        def multiply_costs(*costs: float) -> float:
            '''
            Multiply multiple costs together
            
            Args:
                *costs (float): List of costs to be multiplies together
                
            Returns:
                float: Total cost
            '''
            return self.calculator.multiply(*costs)
        
        
        @tool
        def calculate_daily_budget(total_cost: float, days:int) -> float:
            '''
            Calculate the daily budget based on total cost and no of days.
            
            Args:
                total_cost (float): Total cost of the budget
                days (int) : Number of days
                
            Returns:
                float: Daily budget amount
            '''
            return self.calculator.calculate_daily_budget(total_cost,days)
        
        
        @tool
        def convert_currency(amount: float,from_currency: str, to_currency: str ) -> float:
            ''' Convert currency from one to another.
            Args:
                amount (float): Amount to convert.
                from_currency (str): Currency to convert from.
                to_currency (str): Currency to convert to.                
            Returns:
                float: Converted amount in the target currency.
            '''
            return self.currency_converter.convert_currency(amount,from_currency, to_currency )
        
        @tool(args_schema= DayPlanInput)
        def get_day_plan(date: str, day_number: int, plan_items: List[DayPlanItem], summary: Optional[str] = None,weather_forecast: Optional[str] = None) -> str:
            '''
            Creates a structured daily itinerary plan based on list of activities.
            Args:
                date ( str): Specific date for the day's plan (YYYY-MM-DD)
                day_number (int): Day number in the itinerary (e.g., 1 for Day 1).
                plan_items (List[DayPlanItem]): A list of dictionaries, where each dictionary
                                                represents an activity with 'time', 'activity',
                                                'location', 'notes', and 'estimated_cost' keys.
                                                Each item should conform to the DayPlanItem schema.
                summary (Optional[str]): A brief summary of the day's plan.
                weather_forecast (Optional[str]): The weather forecast for this specific day.
            Returns:
                str: A formatted string representing the daily itinerary plan.
            '''
            plan_output = [f"---Day {day_number} ({date})---"]
            if summary:
                plan_output.append(f"Summary: {summary}")
            if weather_forecast:
                plan_output.append(f'Weather for the Day {day_number}: {weather_forecast}')
            plan_output.append("\n")
            
            for item in plan_items:
                plan_output.append(f"  {item.get('time', 'Time N/A')}: {item.get('activity','Activity N/A')}")
                if item.get('location'):
                    plan_output.append(f"   Location: {item['location']}")
                if item.get('estimated_costs'):
                    plan_output.append(f"   Estimated Cost: {item['estimated_costs']}")
                if item.get('notes'):
                    plan_output.append(f"   Notes: {item['notes']}")
                plan_output.append("")
            plan_output.append("---------------------------------\n")
            return "\n".join(plan_output)
        
        
        @tool(args_schema=FullItinearyInput)
        def create_full_itinerary(destination: str, start_date: str, end_date: str, total_days: int, daily_plans: List[str], 
                               overall_summary: Optional[str] = None, budget_information: Optional[str] = None, 
                               overall_weather_summary: Optional[str] = None) -> str:
            '''
            Generates a full itinerary for the trip based on the information provided.
            Args:
                destination (str): Main destination city for the trip.
                start_date (Str): Start date of the trip in YYYY-MM-DD format.
                end_Date (str): End date of the trip in YYYY-MM-DD format.
                total_days (int): Total number of days of the trip.
                daily_plans (List[str]): A list of formatted strings where each string represents a daily plan generated by the get_day_plan tool.
                overall_summary (Optional[str]): An optional overall summary of the trip.
                budget_information (Optional[str]): An optional budget information for the trip (e.g., Mid-range, Estimated total : XX).
                overall_weather_summary (Optional[str]): Optional overall current weather and forecast information of the destination.
            Returns:
                str: A formatted string representing the full itinerary for the trip.
            '''
            full_itinerary_output= []
            full_itinerary_output.append(f'***** Your Trip to {destination} *****')
            full_itinerary_output.append(f"Dates: {start_date} to {end_date} ({total_days} days)")
            if overall_summary:
                full_itinerary_output.append(f"Overview: {overall_summary}")
            if budget_information:
                full_itinerary_output.append(f"Budget : {budget_information}")
            if overall_weather_summary:
                full_itinerary_output.append(f"Overall Weather Outlook: {overall_weather_summary}")
            full_itinerary_output.append("\n"+"="*50+"\n")
            
            for plans in daily_plans:
                full_itinerary_output.append(plans)
                
            full_itinerary_output.append("\n"+"="*50+"\n")
            full_itinerary_output.append("**This itinerary is generated by AI. Please verify the information before making any bookings.**\n")
            full_itinerary_output.append("***** End of Trip Plan *****")
            
            return "\n".join(full_itinerary_output)    
            

        return [
            search_attraction,
            search_restaurant,
            search_activity,
            search_transport,
            get_current_weather,
            get_weather_forcast,
            search_hotels,
            hotel_cost,
            add_costs,
            multiply_costs,
            calculate_daily_budget,
            convert_currency,
            get_day_plan,
            create_full_itinerary
        ]
                  