import os
import json
import pandas as pd
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables from parent folder
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
print(f"[DEBUG] Looking for .env at: {env_path}")
load_dotenv(env_path)

class AQIAgenticBot:
    """
    Advanced Agentic AI using a ReAct (Reasoning + Action) flow powered by Gemini 2.5 Flash.
    The agent has access to the full project dataset and metrics for factual grounding.
    """
    
    def __init__(self, get_current_aqi_fn):
        self.get_current_aqi = get_current_aqi_fn
        self.last_call_time = 0
        self.min_interval = 15.0  # 4 calls per minute = 15s interval
        
        # Configure Gemini
        raw_key = os.getenv("GOOGLE_API_KEY")
        api_key = raw_key.strip() if raw_key else None
        
        if not api_key:
            print("[DEBUG] CRITICAL: GOOGLE_API_KEY is EMPTY or NOT FOUND!")
        else:
            # We strip spaces/newlines just in case they are in the .env file
            print(f"[DEBUG] API Key Loaded. Length: {len(api_key)} chars. Starts with: {api_key[:8]}...")
            
        # Configure Gemini using the new SDK
        self.client = genai.Client(api_key=api_key)
        
        # DEBUG: List all models to see what is available in your region/account
        print("\n[DEBUG] --- AVAILABLE MODELS FOR YOUR KEY ---")
        try:
            for m in self.client.models.list():
                print(f" - {m.name}")
        except Exception as e:
            print(f" [DEBUG] Could not list models: {e}")
        print("[DEBUG] ------------------------------------\n")

        # Using Gemini 2.5 Flash
        self.model_id = 'gemini-2.5-flash'
        
        # Project Metadata for grounding
        self.project_context = {
            "title": "Agentic AQI Forecasting & Analytics System",
            "persona": "Technical Research Assistant",
            "academic_context": "Predictive Analytics (PA) Lab Project 2026",
            "syllabus_mapping": {
                "Unit I": "Classification: Implemented HGB, Random Forest, and SVM-SGD with balanced class weights for robust AQI categorization.",
                "Unit II": "Unsupervised Clustering: PCA-reduced feature space (12D to 2D) followed by K-Means (k=3) to identify spatial pollution regimes (Industrial, Coastal, Residential).",
                "Unit III": "Neural Networks: Designed Multi-Layer Perceptrons (ANN/DNN) using Back-Propagation for non-linear pollutant interaction modeling.",
                "Unit IV": "NLP & Agentic AI: This ReAct-based chatbot serves as the natural language interface for data exploration and model interpretation.",
                "Unit V": "Deep Learning: Built Sequential pipelines using LSTM and Bi-Directional LSTM with Attention to capture long-term temporal dependencies and pollution spikes.",
                "Unit VI": "Generative AI: Utilized Variational Autoencoders (VAE) and GANs for synthetic data generation, specifically augmenting minority 'Severe' classes to improve recall."
            },
            "dataset_info": {
                "total_rows": 842160,
                "granularity": "Hourly",
                "features": ["PM2.5", "PM10", "NO2", "CO", "SO2", "O3", "Temp", "Humidity", "Wind", "Festivals", "Crop Burning"],
                "preprocessing": "Linear Interpolation for gaps, Median Imputation for city-wide missingness, Cyclical encoding (Sine/Cosine) for temporal features.",
                "geography": "Comprehensive India dataset (Delhi, Mumbai, Bengaluru, etc.)",
            },
            "model_architectures": {
                "LSTM": "128 units -> Dropout (0.2) -> 64 units -> Softmax Output.",
                "HGB": "Histogram-based Gradient Boosting, optimized for large datasets and native missing value handling.",
                "VAE": "Encoder (64-32-8) -> Latent Space (8D) -> Decoder (32-64-8) with KL Divergence regularization."
            },
            "vae_augmentation_impact": {
                "total_synthetic_samples_added": 2746,
                "target_classes": ["Hazardous", "Very_Unhealthy", "Unhealthy"],
                "recall_improvement_hazardous": "From 0.0% to ~23.5% (significant gain in minority class detection).",
                "purpose": "Addressing class imbalance to ensure public health safety during extreme pollution events."
            },
            "forecasting_results": {
                "top_performing_model": "Bi-Directional LSTM with Attention",
                "avg_accuracy_1h": "99.3%",
                "avg_accuracy_24h": "92.4%",
                "metrics": ["Macro F1", "Severe Class Recall", "Balanced Accuracy"]
            },
            "inference_pipeline": {
                "step_1": "Feature Collection: Pollutant and weather data ingestion.",
                "step_2": "Preprocessing: Standard Scaling using pre-trained UI Scaler.",
                "step_3": "Prediction: Ensemble consensus or specific sequential model execution.",
                "step_4": "Validation: Comparison with CPCB deterministic AQI calculation."
            }
        }

    def process_query(self, query):
        print(f"\n[AGENT] Processing User Query: {query}")
        
        # 1. Rate Limiting Check (Internal)
        now = time.time()
        if now - self.last_call_time < self.min_interval:
            return {
                "thought_trace": ["Rate limit detected.", "Throttling request to protect API quota.", "Wait 2 seconds."],
                "response": "I am currently processing requests at maximum capacity. Please allow a brief interval before your next technical query."
            }
        self.last_call_time = now

        try:
            # 2. Pre-flight check: Current status for grounding
            current_status = self.get_current_aqi(query)
            
            prompt = f"""
            You are the "AQI Project Technical Assistant", an academic AI agent specialized in the AQI Prediction & Analytics project.
            Your persona is professional, objective, and highly technical.

            INTERNAL KNOWLEDGE BASE:
            {json.dumps(self.project_context, indent=2)}

            LIVE SYSTEM STATE:
            Target City: {current_status.get('city', 'Unknown')}
            Current CPCB AQI: {current_status.get('aqi', 'Unknown')}
            CPCB Category: {current_status.get('category', 'Unknown')}
            ML Forecast Prediction: {current_status.get('ml_predicted_category', 'Unknown')}
            Data Mode: {"Live (External API)" if current_status.get('is_live') else "Static (Dataset)"}

            USER QUERY: {query}

            RESPONSE PROTOCOL (ReAct):
            1. Thought: Analyze the query. Does it require dataset stats, architecture details, workflow explanation, or a safety suggestion?
            2. Action: Retrieve exact metrics from the Knowledge Base or Live State.
            3. Response: Provide a structured, professional answer.

            STRICT GUIDELINES:
            - **Domain Restriction**: ONLY answer questions related to the project dataset, workflow, models, architecture, inference, or AQI analysis.
            - **Non-Project Queries**: If asked about anything else (general health, jokes, politics, etc.), respond: "I am a specialized AQI Project Assistant. My knowledge is limited to the dataset, architectures, and workflow of this specific predictive analytics project."
            - **Safety Suggestions**: If asked if it is "ok to go out", provide the AQI class and index from the ML Forecast. Suggest an answer (e.g., "It is not recommended") and provide a REASON based on the predicted category and pollutant levels.
            - **Inference Explanation**: If asked how inference works, describe the pipeline (Scaling -> Prediction -> Mapping) as detailed in the Knowledge Base.
            - **VAE Augmentation**: If asked about data changes after VAE, explain how 2,746 synthetic samples were added to boost minority class recall (especially for Hazardous cases).
            - **Tone**: Maintain a formal, academic tone. Avoid informal language.
            - **Identity**: Never mention "Gemini", "Google", or being an "LLM". You are the custom AQI Project Technical Assistant.
            - **Format**: ALWAYS return a JSON object with "thought_trace" (list of strings) and "response" (single string).
            """

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            
            # Robust JSON extraction using regex
            try:
                import re
                raw_text = response.text
                
                # Use regex to find the JSON block in case the LLM added preamble/postscript
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if match:
                    cleaned_text = match.group(0)
                else:
                    cleaned_text = raw_text.replace('```json', '').replace('```', '').strip()
                
                # Parse the JSON response
                result = json.loads(cleaned_text)
                
                # CRASH FIX: Ensure 'response' is a string. If it's an object, format it naturally.
                if isinstance(result.get('response'), (dict, list)):
                    if isinstance(result['response'], dict):
                        # Extract the values into a readable paragraph
                        result['response'] = "\n\n".join(str(v) for v in result['response'].values())
                    else:
                        result['response'] = str(result['response'])

                # PROACTIVE CITY GUIDANCE:
                # If the user asks a general question like "Should I go out?", 
                # and doesn't mention a city, or if we want to be helpful:
                cities = self.project_context["dataset_info"].get("available_cities", [])
                if "city" not in query.lower() and len(cities) > 0:
                    hint = f"\n\nNote: I have specific data for {len(cities)} cities including {', '.join(cities[:5])}. Which one would you like to check?"
                    result['response'] += hint

                return result
            except (json.JSONDecodeError, AttributeError):
                # Fallback if Gemini doesn't return clean JSON
                return {
                    "thought_trace": ["LLM returned non-standard format.", "Extracting natural language content.", "Formatting for UI."],
                    "response": response.text if hasattr(response, 'text') else "I processed your request, but the reasoning engine returned an unexpected format. Please try rephrasing."
                }
                
        except Exception as e:
            print(f" [AGENT ERROR/FALLBACK] {e}")
            
            # ---------------------------------------------------------
            # LOCAL RULE-BASED ENGINE (OFFLINE FALLBACK)
            # Ensures the bot can answer viva questions even without Gemini
            # ---------------------------------------------------------
            q = query.lower()
            current_status = self.get_current_aqi()
            resp = ""
            
            if "model" in q or "accuracy" in q or "best" in q:
                resp = "Based on our project metrics, the BiLSTM (Bidirectional LSTM) with Attention is the top-performing model, achieving 99.3% accuracy for 1-hour forecasts and 92.4% for 24-hour forecasts."
            elif "row" in q or "size" in q or "dataset" in q:
                resp = "Our dataset contains exactly 842,160 rows of hourly, multi-city AQI data."
            elif "city" in q or "cities" in q:
                cities = self.project_context['dataset_info'].get('available_cities', [])
                resp = f"We analyze data for {len(cities)} specific cities. Our internal knowledge base covers locations across India."
            elif "delhi" in q:
                resp = "Delhi historically experiences 'Poor' to 'Very Poor' AQI (250-400+). Our BiLSTM model accurately captures these extreme temporal patterns."
            elif "mumbai" in q:
                resp = "Mumbai typically sees 'Moderate' AQI (100-200) due to coastal winds, though it can peak higher during winter inversions."
            elif "outside" in q or "health" in q or "advice" in q:
                resp = f"The current baseline AQI reading is {current_status['aqi']} ({current_status['category']}). Please consult local CPCB advisories before engaging in heavy outdoor exertion."
            elif "syllabus" in q or "unit" in q:
                resp = "This project fully aligns with the syllabus: Unit I (Classification: Naive Bayes, KNN, SVM), Unit II (Clustering: K-Means, Hierarchical), Unit III (ANN), Unit IV (NLP & LLM: This Chatbot), Unit V (Deep Learning: CNN, RNN, LSTM), and Unit VI (GANs: Data Augmentation)."
            else:
                resp = "My cloud reasoning engine is currently rate-limited, but as your local AQI Project Data Agent, I am still online! I can instantly answer questions about our models, dataset size, or specific cities based on my offline knowledge base."

            return {
                "thought_trace": ["Cloud API unavailable or rate-limited.", "Activating Offline Rule-Based Engine.", "Parsing query against internal project context."],
                "response": resp
            }

    def _get_health_advice(self, category):
        # Kept for backward compatibility but usually handled by Gemini now
        advice_map = {
            "Good": "The air is fresh!",
            "Moderate": "Air quality is acceptable.",
            "Poor": "Wear a mask outdoors.",
            "Severe": "Stay indoors."
        }
        return advice_map.get(category, "Please check local advisories.")
