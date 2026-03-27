import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# 1. Load and Clean
df = pd.read_csv("./data/Crop_recommendation.csv")
# Dropping rows with any missing values
df = df.dropna(axis=0, how='any')

# 2. Features and Target
X = df.drop('label', axis=1)
y = df['label']

# 3. Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Pipeline Setup
# The pipeline ensures that the StandardScaler is fitted ONLY on training data
# and then applied to test/inference data using those same parameters.
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(
        n_estimators=100, 
        max_depth=9,
        min_samples_leaf=12,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42
    ))
])

# 5. Train
pipeline.fit(X_train, y_train)

# 6. Comprehensive Evaluation
y_pred = pipeline.predict(X_test)
print(f"Overall Accuracy: {accuracy_score(y_test, y_pred):.2%}")
print("\nDetailed Report:\n", classification_report(y_test, y_pred))

# 7. Save
joblib.dump(pipeline, 'crop_prediction_model.pkl')
print("Model saved successfully.")


import joblib
import pandas as pd

def suggest_crop(n, p, k, temp, hum, ph, rain):
    # 1. Load the saved pipeline
    model = joblib.load('crop_prediction_model.pkl')
    
    # 2. Format input as a DataFrame (must match training column names)
    input_data = pd.DataFrame([[n, p, k, temp, hum, ph, rain]], 
                              columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    # 3. Predict
    prediction = model.predict(input_data)
    
    # 4. (Optional) Get probabilities to see how "sure" the model is
    probabilities = model.predict_proba(input_data)
    confidence = max(probabilities[0])
    
    return prediction[0], confidence

# Example Usage:
crop, score = suggest_crop(90, 42, 43, 20.8, 82.0, 6.5, 202.9)
print(f"Recommended: {crop} ({score:.2%} confidence)")


# import joblib
# import pandas as pd

# # Load the saved pipeline
# model = joblib.load('crop_prediction_model.pkl')

# # New data point (N, P, K, temp, hum, ph, rain)
# new_data = pd.DataFrame([[80, 40, 40, 25.0, 80.0, 6.5, 200.0]], 
#                         columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

# # Predict!
# prediction = model.predict(new_data)
# print(f"Suggested Crop: {prediction[0]}")