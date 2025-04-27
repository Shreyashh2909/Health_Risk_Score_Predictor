from flask import Flask, request, jsonify
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from flask_cors import CORS  # Important for frontend-backend communication

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Training data (Age, Gender, BMI, Diabetes, Alcohol, Cholesterol, Activity)
train_data = np.array([
    [25, 0, 22.0, 0, 0, 180, 3],
    [45, 1, 30.0, 1, 1, 200, 1],
    [60, 1, 34.5, 1, 1, 250, 0],
    [35, 0, 28.0, 0, 0, 190, 2],
    [50, 1, 32.0, 1, 0, 230, 1],
    [20, 0, 19.0, 0, 0, 170, 3]
])
labels = [0, 1, 2, 1, 2, 0]  # 0=Low, 1=Medium, 2=High

# Train the model
model = DecisionTreeClassifier()
model.fit(train_data, labels)

def estimate_cholesterol(age, bmi, activity):
    """Estimate cholesterol if not provided by user"""
    return round(160 + (age * 0.5) + (bmi * 0.8) - (activity * 5), 2)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()  # Use get_json() instead of .json
        
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Extract data with defaults
        name = data.get('name', 'Unknown')
        phone = data.get('phone', 'N/A')
        age = data.get('age', 30)
        gender = data.get('gender', 0)
        bmi = data.get('bmi', 22.0)
        diabetes = data.get('diabetes', 0)
        alcohol = data.get('alcohol', 0)
        cholesterol = data.get('cholesterol', -1)
        activity = data.get('activity', 2)

        # Estimate cholesterol if not provided
        estimated_chol = None
        if cholesterol == -1:
            estimated_chol = estimate_cholesterol(age, bmi, activity)
            cholesterol = estimated_chol

        # Prepare input data for prediction
        input_data = [
            age,
            gender,
            bmi,
            diabetes,
            alcohol,
            cholesterol,
            activity
        ]

        # Make prediction
        pred = model.predict([input_data])[0]
        category = ["Low", "Medium", "High"][pred]

        # Generate risk score
        if pred == 0:
            risk_score = np.random.uniform(5, 30)
        elif pred == 1:
            risk_score = np.random.uniform(35, 65)
        else:
            risk_score = np.random.uniform(70, 95)

        # Recommendations
        rec_map = {
            0: ["Stay active", "Eat fruits & veggies", "Maintain regular sleep"],
            1: ["Reduce sugar/salt", "Walk 30 mins daily", "Schedule a health checkup"],
            2: ["Consult a physician", "Follow a strict diet", "Get routine lab tests"]
        }

        print(f"🔔 Prediction for {name} ({phone}): {category} risk")

        # Return response with additional info
        return jsonify({
            'name': name,
            'phone': phone,
            'risk_score': round(risk_score, 2),
            'category': category,
            'recommendations': rec_map[pred],
            'estimated_chol': estimated_chol if estimated_chol else None,
            'input_data': input_data  # For debugging
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Health Risk Predictor API is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)