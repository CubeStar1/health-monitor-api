PRESCRIPTION_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .hospital-name {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .hospital-details {{
            font-size: 14px;
            color: #666;
        }}
        .doctor-info {{
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .patient-info {{
            margin: 15px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .vital-signs {{
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
            border-bottom: 2px solid #2c3e50;
        }}
        .medication-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .medication-table th {{
            background-color: #2c3e50;
            color: white;
            padding: 8px;
        }}
        .medication-table td {{
            padding: 8px;
            border: 1px solid #dee2e6;
        }}
        .instructions {{
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: right;
            font-style: italic;
        }}
        .signature {{
            margin-top: 50px;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="hospital-name">{hospital_name}</div>
        <div class="hospital-details">
            {address}<br>
            Phone: {phone}
        </div>
    </div>

    <div class="doctor-info">
        <strong>{doctor_name}</strong><br>
        {doctor_qualifications}<br>
        Reg. No: {doctor_registration}
    </div>

    <div class="patient-info">
        <div class="section-title">Patient Details</div>
        Name: {patient_name}<br>
        Age: {patient_age} | Gender: {patient_gender}<br>
        Contact: {patient_contact}<br>
        Blood Group: {blood_group}<br>
        Allergies: {allergies}
    </div>

    <div class="vital-signs">
        <div class="section-title">Vital Signs</div>
        Temperature: {temperature} | BP: {blood_pressure}<br>
        Pulse: {pulse} | SpO2: {spo2}
    </div>

    <div class="section-title">Diagnosis</div>
    <p>{diagnosis}</p>

    <div class="section-title">Medications</div>
    <table class="medication-table">
        <tr>
            <th>Medicine</th>
            <th>Strength</th>
            <th>Dosage</th>
            <th>Duration</th>
            <th>Route</th>
        </tr>
        {medication_rows}
    </table>

    <div class="instructions">
        <div class="section-title">Instructions</div>
        <ul>
            {instruction_items}
        </ul>
    </div>

    {investigations_section}
    {referrals_section}

    <div class="instructions">
        <div class="section-title">Lifestyle Modifications</div>
        <ul>
            {lifestyle_items}
        </ul>
    </div>

    <div class="signature">
        <div class="doctor-signature">
            {doctor_name}<br>
            {doctor_qualifications}
        </div>
    </div>

    <div class="footer">
        Date: {date}
    </div>
</body>
</html>'''

LAB_REPORT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <style>
        /* Include all existing styles from prescription template */
        .test-category {
            font-weight: bold;
            color: #2c3e50;
            margin-top: 20px;
            border-bottom: 2px solid #2c3e50;
        }
        .test-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .test-table th {
            background-color: #f8f9fa;
            padding: 8px;
            border: 1px solid #dee2e6;
        }
        .test-table td {
            padding: 8px;
            border: 1px solid #dee2e6;
        }
        .abnormal {
            color: #dc3545;
            font-weight: bold;
        }
        .sample-info {
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="hospital-name">{hospital_name}</div>
        <div class="hospital-details">
            {address}<br>
            Phone: {phone}
        </div>
    </div>

    <div class="patient-info">
        <div class="section-title">Patient Details</div>
        Name: {patient_name}<br>
        Age: {patient_age} | Gender: {patient_gender}<br>
        Contact: {patient_contact}
    </div>

    <div class="sample-info">
        <div class="section-title">Sample Details</div>
        Collection Date: {sample_collection_date}<br>
        Collection Time: {sample_collection_time}<br>
        Sample Type: {sample_type}<br>
        Fasting Status: {fasting_status}
    </div>

    <div class="section-title">Test Results</div>
    <table class="test-table">
        <tr>
            <th>Category</th>
            <th>Test Name</th>
            <th>Result</th>
            <th>Reference Range</th>
            <th>Interpretation</th>
            <th>Notes</th>
        </tr>
        {test_rows}
    </table>

    <div class="section-title">Summary</div>
    <p>{summary}</p>

    <div class="instructions">
        <div class="section-title">Recommendations</div>
        <ul>
            {recommendation_items}
        </ul>
    </div>

    <div class="notes">
        <div class="section-title">Additional Notes</div>
        <p>{additional_notes}</p>
    </div>

    <div class="signature">
        <div class="doctor-signature">
            {doctor_name}<br>
            {doctor_qualifications}<br>
            Reg. No: {doctor_registration}
        </div>
    </div>

    <div class="footer">
        Report Date: {date}
    </div>
</body>
</html>'''

DISCHARGE_SUMMARY_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <style>
        /* Include all existing styles from prescription template */
        .summary-section {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .summary-title {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            border-bottom: 2px solid #2c3e50;
        }
        .warning-signs {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 10px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .medication-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .medication-table th {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
        }
        .medication-table td {
            padding: 8px;
            border: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="hospital-name">{hospital_name}</div>
        <div class="hospital-details">
            {address}<br>
            Phone: {phone}
        </div>
    </div>

    <div class="patient-info">
        <div class="section-title">Patient Details</div>
        Name: {patient_name}<br>
        Age: {patient_age} | Gender: {patient_gender}<br>
        Contact: {patient_contact}
    </div>

    <div class="summary-section">
        <div class="summary-title">Admission Details</div>
        Admission Date: {admission_date}<br>
        Discharge Date: {discharge_date}<br>
        Department: {department}<br>
        Type of Admission: {admission_type}
    </div>

    <div class="summary-section">
        <div class="summary-title">Clinical Information</div>
        <strong>Chief Complaints:</strong>
        <ul>{complaint_items}</ul>
        
        <strong>Past History:</strong>
        <ul>{history_items}</ul>
        
        <strong>Examination Findings:</strong>
        <ul>{finding_items}</ul>
        
        <strong>Vital Signs:</strong><br>
        {vital_signs}
    </div>

    <div class="summary-section">
        <div class="summary-title">Hospital Course</div>
        <strong>Primary Diagnosis:</strong> {primary_diagnosis}<br>
        <strong>Secondary Diagnoses:</strong> {secondary_diagnoses}<br>
        
        <strong>Procedures Performed:</strong>
        <ul>{procedure_items}</ul>
        
        <strong>Treatment Given:</strong>
        <ul>{treatment_items}</ul>
        
        <strong>Complications:</strong>
        <ul>{complication_items}</ul>
    </div>

    <div class="summary-section">
        <div class="summary-title">Discharge Details</div>
        <strong>Condition at Discharge:</strong> {condition_at_discharge}<br>
        
        <strong>Medications:</strong>
        <table class="medication-table">
            <tr>
                <th>Medicine</th>
                <th>Dosage</th>
                <th>Duration</th>
            </tr>
            {medication_rows}
        </table>
        
        <strong>Activity Restrictions:</strong>
        <ul>{activity_items}</ul>
        
        <strong>Diet Restrictions:</strong>
        <ul>{diet_items}</ul>
    </div>

    <div class="summary-section">
        <div class="summary-title">Follow-up Plan</div>
        Date: {follow_up_date}<br>
        Department: {follow_up_department}<br>
        Special Instructions: {follow_up_instructions}
    </div>

    <div class="warning-signs">
        <div class="summary-title">Warning Signs</div>
        <strong>Return to Emergency Department if:</strong>
        <ul>{warning_items}</ul>
    </div>

    <div class="signature">
        <div class="doctor-signature">
            {doctor_name}<br>
            {doctor_qualifications}<br>
            Reg. No: {doctor_registration}
        </div>
    </div>

    <div class="footer">
        Generated on: {date}
    </div>
</body>
</html>''' 