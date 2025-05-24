import os
import time
import json
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiService:
    """
    Service class for interacting with Google's Gemini API.
    """
    
    def __init__(self):
        """
        Initialize the Gemini service with API key and model configuration.
        """
        self.api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_GENERATIVE_AI_API_KEY environment variable is not set. AI features will not work.")
            self.is_configured = False
            return
            
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Set the preferred models in order of preference
        preferred_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
        
        # Try to list available models
        try:
            available_models = genai.list_models()
            print("Available models:")
            available_model_names = []
            for model_info in available_models:
                model_name = model_info.name
                if isinstance(model_name, str) and '/' in model_name:
                    model_name = model_name.split('/')[-1]  # Extract just the model name
                print(f" - {model_name}")
                available_model_names.append(model_name)
            
            # Try the preferred models in order
            self.model_name = None
            for preferred in preferred_models:
                for available in available_model_names:
                    if preferred in available:
                        self.model_name = available
                        break
                if self.model_name:
                    break
                    
            # If none of the preferred models are available, use the first available
            if not self.model_name and available_model_names:
                self.model_name = available_model_names[0]
                
            if self.model_name:
                print(f"Using model: {self.model_name}")
                self.model = genai.GenerativeModel(self.model_name)
                self.is_configured = True
                print(f"Successfully configured Gemini service with model: {self.model_name}")
            else:
                print("No models available with the provided API key.")
                self.is_configured = False
                
        except Exception as e:
            print(f"Error listing or configuring models: {e}")
            
            # Try the preferred models directly
            for model_name in preferred_models:
                try:
                    print(f"Trying model directly: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    self.is_configured = True
                    print(f"Successfully configured Gemini service with model: {model_name}")
                    return
                except Exception as model_error:
                    print(f"Error with model {model_name}: {model_error}")
                    
            # If we got here, none of the models worked
            print("Failed to configure any Gemini model.")
            self.is_configured = False
    
    def generate_content(self, prompt_text, generation_config=None, retries=2):
        """
        Generate content using the Gemini API with retry logic.
        
        Args:
            prompt_text (str): The prompt to send to the API
            generation_config (dict, optional): Configuration for generation
            retries (int, optional): Number of retries on failure
            
        Returns:
            str: Generated text or error message
        """
        if not self.is_configured:
            return "Error: Gemini API not properly configured."
        
        # Default generation config
        if generation_config is None:
            generation_config = {
                "temperature": 0.2,  # Lower temperature for more deterministic output
                "max_output_tokens": 2048,
            }
        
        # Add JSON formatting instructions if needed
        if "JSON" in prompt_text and not "DO NOT add comments" in prompt_text:
            json_instruction = "\n\nIMPORTANT: Your response must be valid JSON with no text or comments outside the JSON object. DO NOT add comments inside the JSON (no // or /* */ comments). The JSON must be parseable by standard JSON parsers."
            prompt_text += json_instruction
        
        # Try to generate content with retries
        retry_count = 0
        while retry_count <= retries:
            try:
                response = self.model.generate_content(
                    prompt_text,
                    generation_config=generation_config
                )
                
                # Log the response for debugging
                print(f"Raw Gemini Response: {response.text[:200]}...")
                
                return response.text
                
            except Exception as e:
                retry_count += 1
                if retry_count <= retries:
                    # Exponential backoff
                    wait_time = 2 ** retry_count
                    print(f"Gemini API error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to generate content after {retries} retries: {e}")
                    return f"Error generating AI response: {str(e)}"
    
    def generate_feeding_plan(self, animal_tag_id, species, breed, age, weight_kg, feeding_history, available_feed_types):
        """
        Generate a feeding plan for a specific animal.
        
        Args:
            animal_tag_id (str): The animal's unique identifier
            species (str): The animal's species
            breed (str): The animal's breed
            age (str): The animal's age
            weight_kg (str/float): The animal's weight in kg
            feeding_history (list): Recent feeding logs
            available_feed_types (list): Available feed types
            
        Returns:
            dict: A structured feeding plan
        """
        # Create the prompt
        prompt = f"""You are an AI Farm Assistant specializing in livestock nutrition.
For a {species} (breed: {breed or 'Unknown'}) that is {age} old, currently weighs {weight_kg} kg, and has the following feeding history for the past 7 days:
{chr(10).join(feeding_history) if feeding_history else "No recent feeding history available."}

Available feed types include: {', '.join(available_feed_types) if available_feed_types else "Generic Feed, Hay, Grain"}

Generate a suggested daily feeding plan for the next 7 days, optimizing for healthy growth/maintenance. Provide quantities in kg for each feed type per day. Consider general nutritional needs for this type of animal.

Output the plan in a structured JSON format like:
{{
  "animal_tag_id": "{animal_tag_id}",
  "plan_start_date": "{time.strftime('%Y-%m-%d')}",
  "daily_schedule": [
    {{ "day": 1, "date": "YYYY-MM-DD", "feedings": [{{"feed_type": "Type A", "quantity_kg": Z}}, {{"feed_type": "Type B", "quantity_kg": W}}]}},
    ... (for 7 days)
  ],
  "notes": "General recommendations..."
}}

IMPORTANT: Your response must be valid JSON with no text or comments outside the JSON object.
"""
        
        # Generate and process the response
        response_text = self.generate_content(prompt)
        return self._extract_json_from_response(response_text)
    
    def detect_anomalies(self, animal_tag_id, species, breed, age, feeding_history, health_history):
        """
        Detect health anomalies for a specific animal.
        
        Args:
            animal_tag_id (str): The animal's unique identifier
            species (str): The animal's species
            breed (str): The animal's breed
            age (str): The animal's age
            feeding_history (list): Recent feeding logs
            health_history (list): Recent health records
            
        Returns:
            dict: Detected anomalies and assessment
        """
        # Create the prompt
        prompt = f"""You are an AI Farm Assistant specializing in animal health monitoring.
For a {species} (breed: {breed or 'Unknown'}) with animal ID {animal_tag_id}, age {age}, consider the following data from the last 14 days:

Feeding Logs:
{chr(10).join(feeding_history) if feeding_history else "No recent feeding logs available."}

Health Records:
{chr(10).join(health_history) if health_history else "No recent health records available."}

Analyze this data for any unusual patterns or potential health concerns. Look for things like:
- Significant unexplained decrease/increase in food consumption.
- Weight loss despite adequate feeding.
- Consistently high/low temperature.
- Reported lethargy or unusual behavior changes.
- Deviations from expected norms for this animal type.

If anomalies are found, describe each anomaly, its potential cause, and suggest a severity level (Low, Medium, High).
Output in JSON format:
{{
  "animal_tag_id": "{animal_tag_id}",
  "anomalies_detected": [
    {{
      "description": "Sudden 20% decrease in feed intake over the last 3 days.",
      "potential_cause": "Possible illness, dental issue, or stress.",
      "severity": "Medium",
      "data_points_of_concern": ["Date X: Behavior noted", "Date Y: Weight drop"]
    }}
  ],
  "overall_assessment": "Some concerns noted, further observation recommended."
}}

If no significant anomalies, return an empty anomalies_detected list and a positive assessment.

IMPORTANT: Your response must be valid JSON with no text or comments outside the JSON object.
"""

        # Generate and process the response
        response_text = self.generate_content(prompt)
        return self._extract_json_from_response(response_text)
    
    def generate_health_summary(self, animal_tag_id, species, breed, age, feeding_history, health_history, summary_period_start, summary_period_end):
        """
        Generate a health summary for a specific animal.
        
        Args:
            animal_tag_id (str): The animal's unique identifier
            species (str): The animal's species
            breed (str): The animal's breed
            age (str): The animal's age
            feeding_history (list): All feeding logs
            health_history (list): All health records
            summary_period_start (str): Start date of summary period
            summary_period_end (str): End date of summary period
            
        Returns:
            dict: A structured health summary
        """
        # Create the prompt
        prompt = f"""You are an AI Farm Assistant.
For animal ID {animal_tag_id}, a {species} (breed: {breed or 'Unknown'}) aged {age}, provide a concise health and feeding summary based on the following data:

All Feeding Logs:
{chr(10).join(feeding_history) if feeding_history else "No feeding logs available."}

All Health Records:
{chr(10).join(health_history) if health_history else "No health records available."}

Summarize key trends in feeding, weight, temperature, and behavior. Highlight any periods of concern or improvement. Provide an overall health status indication.
Output in JSON format:
{{
  "animal_tag_id": "{animal_tag_id}",
  "summary_period_start": "{summary_period_start}",
  "summary_period_end": "{summary_period_end}",
  "feeding_summary": "Average daily intake X kg. Consistent feed types. [Any notable changes].",
  "weight_trend": "Weight has [increased/decreased/stayed stable] from X kg to Y kg. [Comment on trend].",
  "temperature_trend": "Temperatures generally stable around X C. [Any notable spikes/dips].",
  "behavior_summary": "Behavior mostly [e.g., active]. [Any reported issues and their resolution/status].",
  "overall_status": "Good / Fair / Needs Monitoring / Concern",
  "recommendations": ["Continue current feeding plan.", "Monitor X more closely."]
}}

IMPORTANT: Your response must be valid JSON with no text or comments outside the JSON object.
"""

        # Generate and process the response
        response_text = self.generate_content(prompt)
        return self._extract_json_from_response(response_text)
    
    def _extract_json_from_response(self, response_text):
        """
        Extract JSON from the response text, handling various formats.
        
        Args:
            response_text (str): The raw response text from Gemini
            
        Returns:
            dict: Parsed JSON object or error dictionary
        """
        if response_text.startswith("Error"):
            return {"error": response_text}
            
        try:
            # Process the response text to extract JSON
            json_content = response_text
            
            # Handle markdown code blocks
            if "```json" in json_content:
                json_content = json_content.split("```json")[1].split("```")[0].strip()
            elif "```" in json_content:
                json_content = json_content.split("```")[1].split("```")[0].strip()
                
            # Extract JSON from text that may have content before/after
            if json_content.strip().startswith("{"):
                start_idx = json_content.find("{")
                end_idx = json_content.rfind("}")
                if start_idx >= 0 and end_idx >= 0:
                    json_content = json_content[start_idx:end_idx+1]
            
            # Remove JSON comments (both // and /* */ style)
            import re
            # First, remove // style comments
            json_content = re.sub(r'//.*?$', '', json_content, flags=re.MULTILINE)
            # Then remove /* */ style comments
            json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
                    
            # Parse the JSON content
            print(f"Processed JSON content: {json_content[:200]}...")
            return json.loads(json_content)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            try:
                # Try a more flexible JSON parser (demjson if available)
                import json5
                return json5.loads(json_content)
            except (ImportError, Exception) as flex_error:
                print(f"Flexible JSON parsing failed: {flex_error}")
                # One last attempt with manual comment removal
                try:
                    # Remove lines with comments and try again
                    clean_lines = []
                    for line in json_content.split('\n'):
                        if '//' not in line and '/*' not in line and '*/' not in line:
                            clean_lines.append(line)
                    clean_json = '\n'.join(clean_lines)
                    return json.loads(clean_json)
                except Exception:
                    # Give up and return the error
                    return {
                        "error": "Failed to parse AI response",
                        "raw_response": response_text
                    }

# Create a singleton instance
gemini_service = GeminiService()