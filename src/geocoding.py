from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class LocationGeocoder:
    def __init__(self):
        # Use Nominatim for free geocoding
        self.geolocator = Nominatim(user_agent="power_grid_analysis_system")
        
        # Predefined Delhi locations with precise coordinates
        self.delhi_locations = {
            'Connaught Place': (28.6304, 77.2177),
            'Nehru Place': (28.5479, 77.2628),
            'India Gate': (28.6129, 77.2294),
            'Chandni Chowk': (28.6562, 77.2295),
            'Saket': (28.5166, 77.2209),
            'Dwarka': (28.5784, 77.0650),
            'Noida': (28.5355, 77.3910),
            'Gurgaon': (28.4595, 77.0266)
        }
    
    def geocode_location(self, location, city='Delhi, India'):
        """
        Geocode a location with enhanced precision
        
        Args:
            location (str): Specific location within the city
            city (str): City name to provide context
        
        Returns:
            dict: Containing latitude, longitude, and full address
        """
        # First, check predefined locations
        for predefined_loc, coords in self.delhi_locations.items():
            if predefined_loc.lower() in location.lower():
                return {
                    'latitude': coords[0],
                    'longitude': coords[1],
                    'address': f'{predefined_loc}, {city}',
                    'source': 'predefined'
                }
        
        try:
            # Combine location with city for more precise geocoding
            full_location = f"{location}, {city}"
            
            # Attempt to geocode
            location_data = self.geolocator.geocode(full_location)
            
            if location_data:
                return {
                    'latitude': location_data.latitude,
                    'longitude': location_data.longitude,
                    'address': location_data.address,
                    'source': 'geocoded'
                }
            else:
                # Fallback to city center if specific location not found
                city_location = self.geolocator.geocode(city)
                return {
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'address': 'Delhi, India',
                    'note': 'City center used as fallback',
                    'source': 'city_center'
                }
        
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            # Fallback to Delhi city center coordinates
            return {
                'latitude': 28.6139,
                'longitude': 77.2090,
                'address': 'Delhi, India',
                'error': str(e),
                'source': 'error_fallback'
            }
        except Exception as e:
            # Generic error handling
            return {
                'latitude': 28.6139,
                'longitude': 77.2090,
                'address': 'Delhi, India',
                'error': f'Unexpected geocoding error: {str(e)}',
                'source': 'generic_fallback'
            }

# Create a singleton instance
location_geocoder = LocationGeocoder()
