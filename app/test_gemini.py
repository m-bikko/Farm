import os
from dotenv import load_dotenv
from services.gemini_service import gemini_service

# Load environment variables
load_dotenv()

def test_gemini_service():
    """Test the Gemini service to verify it can communicate with the API."""
    
    print("Testing Gemini service...")
    
    # Make sure API key is set
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY or GOOGLE_GENERATIVE_AI_API_KEY environment variable not set.")
        return
    
    print(f"API Key: {api_key[:5]}...{api_key[-3:]} (length: {len(api_key)})")
    
    # Test a simple content generation
    prompt = "Generate a JSON object with information about a cow named Bessie. Include age, weight, and breed."
    
    print("\nSending prompt to Gemini API...")
    response = gemini_service.generate_content(prompt)
    
    print("\nResponse from Gemini API:")
    print(response)
    
    # Test the JSON extraction
    print("\nAttempting to extract JSON from response...")
    result = gemini_service._extract_json_from_response(response)
    
    print("\nExtracted JSON result:")
    print(result)
    
    print("\nGemini service test complete.")

if __name__ == "__main__":
    test_gemini_service()