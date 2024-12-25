PRESCRIPTION_PROMPT= """Generate a detailed medical prescription following Indian medical standards. Include:

1. Chief complaints with duration and severity
2. Vital signs (Temperature, BP, Pulse, SpO2 if relevant)
3. Detailed diagnosis with specific findings
4. 3-5 medications with:
    - Generic name (common in India)
    - Brand name (common Indian brands)
    - Strength (mg/ml)
    - Precise dosage with timing
    - Duration with specific dates
    - Route of administration
    - Special instructions
5. Detailed patient instructions including:
    - Medication schedule
    - Dietary restrictions
    - Lifestyle modifications
    - Warning signs to watch for
    - Follow-up timeline
6. Investigation/Lab tests to be done (if any)
7. Referrals to specialists (if needed)

Return as JSON:
{
    "chief_complaints": ["complaint with duration"],
    "vital_signs": {
        "temperature": "value",
        "blood_pressure": "value",
        "pulse": "value",
        "spo2": "value if measured"
    },
    "diagnosis": "detailed diagnosis",
    "medications": [
        {
            "generic_name": "name",
            "brand_name": "Indian brand name",
            "strength": "strength",
            "dosage": "detailed dosage",
            "duration": "duration",
            "route": "route",
            "special_instructions": "any special instructions"
        }
    ],
    "instructions": ["detailed instructions"],
    "investigations": ["test1", "test2"],
    "follow_up": "follow up details",
    "referrals": ["specialist referral if any"],
    "lifestyle_modifications": ["modification1", "modification2"]
}""" 

LAB_REPORT_PROMPT = """Generate a detailed medical laboratory report following Indian standards. Include:

1. Patient vitals and basic information
2. Sample collection details
3. 5-8 relevant laboratory tests with:
- Test name (common tests in India)
- Result value with units
- Normal reference range
- Interpretation (High/Low/Normal)
- Any specific notes
4. Include some from these categories:
- Hematology
- Biochemistry
- Lipid Profile
- Thyroid Profile
- Liver Function
- Kidney Function
- Blood Sugar Tests

Return as JSON:
{
    "sample_details": {
        "collection_date": "date",
        "collection_time": "time",
        "fasting_status": "fasting/non-fasting",
        "sample_type": "blood/urine/etc"
    },
    "test_results": [
        {
            "category": "test category",
            "test_name": "name",
            "result": "value with units",
            "reference_range": "range with units",
            "interpretation": "High/Low/Normal",
            "notes": "any specific notes"
        }
    ],
    "summary": "Overall interpretation",
    "recommendations": ["recommendation1", "recommendation2"],
    "additional_notes": "any special notes or warnings"
}"""

DISCHARGE_SUMMARY_PROMPT = """Generate a detailed hospital discharge summary following Indian standards. Include:

1. Admission Details:
    - Date of admission
    - Date of discharge
    - Duration of stay
    - Admission type (Emergency/Planned)
    - Primary department
2. Clinical Information:
    - Chief complaints with duration
    - Relevant past medical history
    - Physical examination findings
    - Vital signs during admission
3. Hospital Course:
    - Primary diagnosis
    - Secondary diagnoses
    - Procedures performed
    - Treatment given
    - Course in hospital
    - Complications if any
4. Discharge Details:
    - Condition at discharge
    - Activity restrictions
    - Diet restrictions
    - Medications on discharge
    - Follow-up plan
    - Warning signs to watch for

Return as JSON:
{
    "admission_details": {
        "admission_date": "date",
        "discharge_date": "date",
        "duration": "days",
        "admission_type": "Emergency/Planned",
        "department": "department name"
    },
    "clinical_info": {
        "chief_complaints": ["complaint1", "complaint2"],
        "past_history": ["relevant history"],
        "examination_findings": ["finding1", "finding2"],
        "vital_signs": {
            "temperature": "value",
            "blood_pressure": "value",
            "pulse": "value",
            "spo2": "value"
        }
    },
    "hospital_course": {
        "primary_diagnosis": "diagnosis",
        "secondary_diagnoses": ["diagnosis1", "diagnosis2"],
        "procedures": ["procedure1", "procedure2"],
        "treatment_given": ["treatment1", "treatment2"],
        "complications": ["complication if any"]
    },
    "discharge_details": {
        "condition": "condition at discharge",
        "activity_restrictions": ["restriction1", "restriction2"],
        "diet_restrictions": ["diet1", "diet2"],
        "medications": [
            {
                "name": "medicine name",
                "dosage": "dosage",
                "duration": "duration"
            }
        ],
        "follow_up": {
            "date": "follow up date",
            "department": "department",
            "special_instructions": "instructions"
        },
        "warning_signs": ["sign1", "sign2"]
    }
}"""

INDIAN_HOSPITALS = [
    {"name": "Apollo Hospitals", "locations": ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Mumbai"]},
    {"name": "Fortis Healthcare", "locations": ["Gurgaon", "Noida", "Bangalore", "Mumbai", "Kolkata"]},
    {"name": "Max Healthcare", "locations": ["Saket", "Patparganj", "Vaishali", "Shalimar Bagh"]},
    {"name": "Manipal Hospitals", "locations": ["Bangalore", "Mangalore", "Goa", "Jaipur"]},
    {"name": "Medanta", "locations": ["Gurgaon", "Lucknow", "Indore", "Ranchi"]},
    {"name": "Narayana Health", "locations": ["Bangalore", "Kolkata", "Ahmedabad", "Jamshedpur"]},
    {"name": "AIIMS", "locations": ["New Delhi", "Bhopal", "Jodhpur", "Patna", "Raipur"]},
    {"name": "Kokilaben Hospital", "locations": ["Mumbai", "Andheri West"]},
    {"name": "Tata Memorial", "locations": ["Mumbai", "Kolkata", "Varanasi"]},
    {"name": "Lilavati Hospital", "locations": ["Mumbai", "Bandra"]}
]

