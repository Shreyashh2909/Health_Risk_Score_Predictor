import streamlit as st
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Health Risk Predictor", layout="centered")

st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to right, #d9a7c7, #fffcdc);
            font-family: 'Segoe UI', sans-serif;
        }
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background-color: #fefefe;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        h1, h3, h4 {
            text-align: center;
            color: #222;
        }
        button[kind="primary"] {
            background-color: #10B981 !important;
            color: white !important;
            border-radius: 10px;
            padding: 10px 16px;
            font-weight: bold;
        }
        .markdown-text-container ul {
            padding-left: 1.5rem;
        }
        .markdown-text-container li {
            margin-bottom: 0.5rem;
        }
        .element-container:has(.stPyplot) {
            margin-top: 30px;
        }
        .risk-card {
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .low-risk {
            background-color: #A8E6CF;
        }
        .medium-risk {
            background-color: #FFD3B6;
        }
        .high-risk {
            background-color: #FFAAA5;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 Health Risk Score Predictor")
st.markdown("### Please fill in your details:")

name = st.text_input("Full Name")
phone = st.text_input("Phone Number")

age = st.number_input("Age", 1, 120, 20)
gender = st.selectbox("Gender", ["Male", "Female"])
bmi = st.number_input("BMI", 10.0, 50.0, 19.0)
smoking = st.selectbox("Do you smoke?", ["No", "Yes"])
diabetes = st.selectbox("Do you have diabetes?", ["No", "Yes"])
alcohol = st.selectbox("Do you consume alcohol?", ["No", "Yes"])

chol_input = st.radio("Do you know your cholesterol level?", ("Yes", "No"))
if chol_input == "Yes":
    cholesterol = st.number_input("Cholesterol", value=170)
else:
    cholesterol = -1

activity = st.slider("Activity Level (0 = Low, 3 = High)", 0, 3, 3)

if st.button("Predict Risk"):
    if name.strip() == "" or phone.strip() == "":
        st.error("Please enter your name and phone number.")
    else:
        payload = {
            'name': name,
            'phone': phone,
            'age': age,
            'gender': 0 if gender == "Male" else 1,
            'bmi': bmi,
            'diabetes': 1 if diabetes == "Yes" else 0,
            'alcohol': 1 if alcohol == "Yes" else 0,
            'cholesterol': cholesterol,
            'activity': activity
        }
        
        try:
            # Make the API request to Flask backend
            response = requests.post('http://localhost:5000/predict', json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("Analysis complete!")
                
                # Determine risk class for styling
                risk_class = result['category'].lower().replace(" ", "-") + "-risk"
                
                st.markdown(f"""
                <div class="risk-card {risk_class}">
                    <h2>Your Health Risk Assessment</h2>
                    <h1 style="font-size: 3.5rem; margin: 10px 0;">{result['risk_score']}</h1>
                    <h3>{result['category']} Risk</h3>
                    <p>Based on your health profile</p>
                </div>
                """, unsafe_allow_html=True)
                
                if cholesterol == -1:
                    st.info(f"Estimated cholesterol level: {result.get('estimated_chol', 'N/A')} mg/dL")
                
                st.subheader("Recommendations")
                for i, rec in enumerate(result['recommendations'], 1):
                    st.markdown(f"{i}. {rec}")
                
                # Visual representation
                fig, ax = plt.subplots(figsize=(8, 2))
                ax.barh([0], [result['risk_score']], color='#10B981', height=0.5)
                ax.set_xlim(0, 100)
                ax.set_xticks([0, 25, 50, 75, 100])
                ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
                ax.set_yticks([])
                ax.set_title('Your Health Risk Score')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                
                st.pyplot(fig)
                
            else:
                st.error(f"Prediction failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the prediction service: {str(e)}")
            st.info("Please make sure the Flask backend is running on port 5000")