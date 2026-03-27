import pickle
import pandas as pd 
import joblib 

def predict_fertilizer(weights_path , input_dict):
    # Load the bundle inside or use the already trained 'pipeline'
    # For a standalone script, we load it to ensure the file works
    with open(weights_path, "rb") as f:
        loaded_bundle = pickle.load(f)
        model = loaded_bundle["pipeline"]
        features = loaded_bundle["features"]
    
    df_input = pd.DataFrame([input_dict])
    df_input.columns = df_input.columns.str.replace('Temparature', 'Temperature')
    
    # Ensure column order matches the training features
    df_input = df_input.reindex(columns=features)
    
    return model.predict(df_input)[0]




# ==========================================
# 5. INFERENCE FUNCTION (How to use it)
# ==========================================
def predict_yield_simple(weights_path , crop_name, rain, pesticide, temp):
    """
    Takes raw inputs and returns a yield prediction using the single pipeline file.
    """
    # Load the single pipeline object
    model = joblib.load(weights_path)
    
    # Create a blank row with all 0s based on the features the model learned
    input_df = pd.DataFrame(0, index=[0], columns=model.feature_names)
    
    # Fill in numerical data
    input_df['average_rain_fall_mm_per_year'] = rain
    input_df['pesticides_tonnes'] = pesticide
    input_df['avg_temp'] = temp
    
    # Set the specific crop to 1 (One-Hot Encoding)
    crop_col = f'Crop_{crop_name}'
    if crop_col in input_df.columns:
        input_df[crop_col] = 1
    else:
        return f"Error: Crop '{crop_name}' was not found in the training data."

    # Predict (Scaling happens automatically inside the pipeline!)
    prediction = model.predict(input_df)[0]
    return prediction



def predict_crop(model_weights , n, p, k, temp, hum, ph, rain):
    # 1. Load the saved pipeline
    model = joblib.load(model_weights)
    
    # 2. Format input as a DataFrame (must match training column names)
    input_data = pd.DataFrame([[n, p, k, temp, hum, ph, rain]], 
                              columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    # 3. Predict
    prediction = model.predict(input_data)
    
    # 4. (Optional) Get probabilities to see how "sure" the model is
    # probabilities = model.predict_proba(input_data)
    # confidence = max(probabilities[0])
    
    return prediction[0]




# Example Test
if __name__ == "__main__":
    sample_input = {
        'Temperature': 30.0,
        'Humidity': 60.0,
        'Moisture': 42.0,
        'Soil Type': 'Sandy',
        'Crop Type': 'Maize',
        'Nitrogen': 22,
        'Potassium': 0,
        'Phosphorous': 21
    }
    
    result = predict_fertilizer(sample_input)
    print(f"\nPredicted Fertilizer: {result}")
    
        
        # --- Example Usage ---
    example_crop = 'Rice, paddy'
    predicted_val = predict_yield_simple(example_crop, 1100, 45000, 26.0)
    print(f"\nExample Prediction for {example_crop}: {predicted_val:,.2f} hg/ha")

