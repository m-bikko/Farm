import os
from dotenv import load_dotenv
from services.gemini_service import gemini_service

# Load environment variables
load_dotenv()

def test_feeding_plan():
    """Test the complete feeding plan generation functionality."""
    
    print("Testing feeding plan generation...")
    
    # Sample data for a cow
    animal_tag_id = "COW-TEST-001"
    species = "Cow"
    breed = "Holstein"
    age = "3.5 years (1277 days)"
    weight_kg = 600
    
    # Sample feeding history
    feeding_history = [
        "- 2024-05-15: Hay, 8.5 kg, Notes: None",
        "- 2024-05-16: Grain Mix, 4.2 kg, Notes: None",
        "- 2024-05-17: Hay, 8.5 kg, Notes: None",
        "- 2024-05-18: Grain Mix, 4.2 kg, Notes: None",
        "- 2024-05-19: Hay, 8.5 kg, Notes: None",
        "- 2024-05-20: Grain Mix, 4.2 kg, Notes: None",
        "- 2024-05-21: Hay, 8.5 kg, Notes: None",
    ]
    
    # Available feed types
    available_feed_types = ["Hay", "Grain Mix", "Silage", "Pasture"]
    
    # Generate feeding plan
    result = gemini_service.generate_feeding_plan(
        animal_tag_id=animal_tag_id,
        species=species,
        breed=breed,
        age=age,
        weight_kg=weight_kg,
        feeding_history=feeding_history,
        available_feed_types=available_feed_types
    )
    
    # Print the result
    print("\nFeeding Plan Result:")
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "raw_response" in result:
            print(f"Raw response: {result.get('raw_response')}")
    else:
        print(f"Animal: {result.get('animal_tag_id')}")
        print(f"Plan Start Date: {result.get('plan_start_date')}")
        print(f"Notes: {result.get('notes')}")
        print("\nDaily Schedule:")
        for day in result.get('daily_schedule', []):
            print(f"Day {day.get('day')} - {day.get('date')}:")
            for feeding in day.get('feedings', []):
                print(f"  - {feeding.get('feed_type')}: {feeding.get('quantity_kg')} kg")
    
    print("\nTest complete.")

if __name__ == "__main__":
    test_feeding_plan()