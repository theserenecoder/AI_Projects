import os
from dotenv import load_dotenv

## Config Class

class Config:
    
    def __init__(self):
        load_dotenv()
        self.weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def get_api_keys(self) -> dict:
        '''
        Returns a dictionary of all configured API Key
        '''
        return {
            'weather_api_key': self.weather_api_key,
            'serper_api_key': self.serper_api_key,
            'tavily_api_key': self.tavily_api_key,
            'openai_api_key': self.openai_api_key
        }