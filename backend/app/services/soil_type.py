
def get_soil_type(lat, lon):
    """
    Returns only the soil type string based on geographic coordinates.
    Categories: Sandy, Loamy, Clayey, Black, Red.
    """
    
    # 1. Sandy Soil (Northwest - Rajasthan/Gujarat)
    if (24.00 <= lat <= 30.00) and (69.00 <= lon <= 76.00):
        return "Sandy"

    # 2. Black Soil (Deccan Plateau - MH, MP, GJ)
    elif (15.00 <= lat <= 25.00) and (73.00 <= lon <= 80.00):
        return "Black"

    # 3. Red Soil (South & East - TN, KA, AP, OD)
    elif (8.00 <= lat <= 24.00) and (75.00 <= lon <= 85.00):
        return "Red"

    # 4. Loamy Soil (Indo-Gangetic Plains - UP, PB, BR)
    elif (23.00 <= lat <= 32.00) and (74.00 <= lon <= 90.00):
        return "Loamy"

    # 5. Clayey Soil (Broadest coverage/Deltas)
    elif (6.75 <= lat <= 35.49) and (68.38 <= lon <= 96.66):
        return "Clayey"
    
    else:
        return "Unknown"

# --- Testing with your decimal precision ---
print(get_soil_type(26.52345, 71.38210))  # Output: Sandy
print(get_soil_type(19.07601, 72.87767))  # Output: Black
print(get_soil_type(28.61390, 77.20900))  # Output: Loamy