import logging
import json
from typing import Dict, Any
from datetime import datetime
import random
from faker import Faker
from openai import OpenAI
import traceback
from config import OPENAI_MODEL, OPENAI_API_KEY
from utils.medical_document_gen_prompts import INDIAN_HOSPITALS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_indian_name():
    """Generate a random Indian name"""
    first_names = [
        "Aarav", "Arjun", "Advait", "Kabir", "Krishna", "Vihaan",
        "Aanya", "Diya", "Zara", "Myra", "Prisha", "Aadhya"
    ]
    last_names = [
        "Patel", "Kumar", "Singh", "Sharma", "Verma", "Gupta",
        "Shah", "Mehta", "Reddy", "Kapoor", "Malhotra", "Joshi"
    ]
    return f"Dr. {random.choice(first_names)} {random.choice(last_names)}"

async def generate_indian_details() -> Dict[str, Any]:
    """Generate realistic Indian medical facility and patient details using OpenAI"""
    try:
        # Select a random hospital
        hospital = random.choice(INDIAN_HOSPITALS)
        location = random.choice(hospital["locations"])
        
        prompt = f"""Generate realistic Indian medical facility and patient details. Use {hospital["name"]} in {location} as the hospital.
        Return in this exact JSON format without any additional text:
        {{
            "hospital_name": "{hospital["name"]}, {location}",
            "address": "Detailed address with area landmarks and pincode",
            "phone": "Valid format Indian phone number",
            "doctor": {{
                "name": "Full Indian name",
                "qualification": "Medical qualifications (include specialization)",
                "registration": "State Medical Council registration number",
                "specialization": "Medical specialization",
                "experience": "Years of experience"
            }},
            "patient": {{
                "name": "Full Indian name",
                "age": "age in years",
                "gender": "M/F",
                "contact": "Valid format Indian phone number",
                "blood_group": "Blood group",
                "allergies": ["allergy1", "allergy2"] or [],
                "occupation": "Patient occupation",
                "address": "Patient residential address"
            }}
        }}"""

        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in Indian healthcare administration. Return ONLY valid JSON without any explanation or additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        response_content = response.choices[0].message.content.strip()
        
        try:
            details = json.loads(response_content)
            logger.info("Successfully parsed Indian details JSON")
            return details
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response content: {response_content}")
            raise

    except Exception as e:
        logger.error(f"Error generating Indian details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Fall back to faker
        fake = Faker('en_IN')
        return {
            "hospital_name": f"{random.choice(['Apollo', 'Fortis', 'Max', 'Medanta'])} Hospital",
            "address": fake.address(),
            "phone": fake.phone_number(),
            "doctor": {
                "name": generate_indian_name(),
                "qualification": "MBBS, MD",
                "registration": f"IMC-{fake.random_number(digits=6)}"
            },
            "patient": {
                "name": f"{fake.first_name()} {fake.last_name()}",
                "age": str(random.randint(18, 75)),
                "gender": random.choice(["M", "F"]),
                "contact": fake.phone_number()
            }
        } 

async def generate_medical_content(doc_type: str, llm_choice: str = "openai") -> Dict[str, Any]:
    """Generate sample medical content based on document type using OpenAI"""
    try:
        indian_details = await generate_indian_details()
        common_data = {
            "hospital_name": indian_details["hospital_name"],
            "address": indian_details["address"],
            "phone": indian_details["phone"],
            "doctor_name": f"Dr. {indian_details['doctor']['name']}",
            "doctor_qualifications": indian_details['doctor']['qualification'],
            "doctor_registration": indian_details['doctor']['registration'],
            "patient_name": indian_details['patient']['name'],
            "patient_age": indian_details['patient']['age'],
            "patient_gender": indian_details['patient']['gender'],
            "patient_contact": indian_details['patient']['contact'],
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        from utils.medical_document_gen_prompts import PRESCRIPTION_PROMPT, LAB_REPORT_PROMPT, DISCHARGE_SUMMARY_PROMPT
        
        prompt = {
            "prescription": PRESCRIPTION_PROMPT,
            "lab_report": LAB_REPORT_PROMPT,
            "discharge_summary": DISCHARGE_SUMMARY_PROMPT
        }.get(doc_type)

        if not prompt:
            raise ValueError(f"Invalid document type: {doc_type}")

        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": """You are an experienced Indian medical professional. 
                Generate realistic medical content following Indian healthcare standards and terminology.
                Include detailed, medically accurate information while maintaining patient safety.
                Return ONLY valid JSON without any additional text."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        response_content = response.choices[0].message.content.strip()
        
        try:
            llm_content = json.loads(response_content)
            logger.info("Successfully parsed medical content JSON")
            return {**common_data, **llm_content}
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {str(je)}")
            logger.error(f"Raw response content: {response_content}")
            raise

    except Exception as e:
        logger.error(f"Error in generate_medical_content: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 