
import reverse_geocode as rg

def get_location_offline(lat, lon):
    # 'search' accepts a tuple or a list of tuples for batch processing
    coordinates = (lat, lon)
    results = rg.get(coordinates) # Returns a list of dictionaries
    return results.get("state","orissa")

if __name__ == "__main__":
    # Example: Near Dehradun, Uttarakhand
    print(get_location_offline(30.3165, 78.0322))
    # Output: Dehra Dun, Uttarakhand, IN

