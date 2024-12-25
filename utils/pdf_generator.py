import logging
from typing import Dict, Any, List
import pdfkit
import traceback

logger = logging.getLogger(__name__)

def generate_investigations_section(investigations: List[str]) -> str:
    if not investigations:
        return ""
    return f"""
    <div class="section-title">Investigations</div>
    <ul>
        {''.join(f'<li>{investigation}</li>' for investigation in investigations)}
    </ul>
    """

def generate_referrals_section(referrals: List[str]) -> str:
    if not referrals:
        return ""
    return f"""
    <div class="referrals">
        <div class="section-title">Referrals</div>
        <ul>
            {''.join(f'<li>{referral}</li>' for referral in referrals)}
        </ul>
    </div>
    """

def generate_lifestyle_items(modifications: List[str]) -> str:
    if not modifications:
        return "<li>No specific modifications recommended</li>"
    return ''.join(f'<li>{modification}</li>' for modification in modifications)

async def generate_pdf(content: Dict[str, Any], doc_type: str) -> bytes:
    """Generate PDF document from HTML template"""
    try:
        if doc_type == "prescription":
            # Format medication rows
            medication_rows = ""
            logger.debug(f"Medications data: {content['medications']}")
            
            for med in content['medications']:
                if isinstance(med, (list, tuple)):
                    generic_name = med[0]
                    strength = med[1]
                    dosage = med[2]
                    duration = med[3]
                    route = med[4] if len(med) > 4 else "Oral"
                elif isinstance(med, dict):
                    brand_name = f" ({med.get('brand_name', '')})" if med.get('brand_name') else ""
                    generic_name = f"{med.get('generic_name', '')}{brand_name}"
                    strength = med.get('strength', '')
                    dosage = med.get('dosage', '')
                    duration = med.get('duration', '')
                    route = med.get('route', 'Oral')
                else:
                    logger.error(f"Unexpected medication format: {med}")
                    continue

                medication_rows += f"""
                <tr>
                    <td>{generic_name}</td>
                    <td>{strength}</td>
                    <td>{dosage}</td>
                    <td>{duration}</td>
                    <td>{route}</td>
                </tr>"""

            # Format instructions
            instruction_items = ""
            instructions = content.get('instructions', [])
            if isinstance(instructions, list):
                instruction_items = ''.join(f"<li>{instruction}</li>" for instruction in instructions)
            else:
                instruction_items = f"<li>{instructions}</li>"

            # Remove Dr. prefix if already present
            doctor_name = content['doctor_name']
            if doctor_name.startswith("Dr. Dr."):
                doctor_name = doctor_name.replace("Dr. Dr.", "Dr.")

            # Fill template
            from templates.medical_templates import PRESCRIPTION_TEMPLATE
            html_content = PRESCRIPTION_TEMPLATE.format(
                hospital_name=content['hospital_name'],
                address=content['address'],
                phone=content['phone'],
                doctor_name=doctor_name,
                doctor_qualifications=content['doctor_qualifications'],
                doctor_registration=content['doctor_registration'],
                patient_name=content['patient_name'],
                patient_age=content['patient_age'],
                patient_gender=content['patient_gender'],
                patient_contact=content['patient_contact'],
                date=content['date'],
                blood_group=content.get('blood_group', 'Not Available'),
                allergies=', '.join(content.get('allergies', ['None'])),
                diagnosis=content['diagnosis'],
                temperature=content.get('vital_signs', {}).get('temperature', 'N/A'),
                blood_pressure=content.get('vital_signs', {}).get('blood_pressure', 'N/A'),
                pulse=content.get('vital_signs', {}).get('pulse', 'N/A'),
                spo2=content.get('vital_signs', {}).get('spo2', 'N/A'),
                medication_rows=medication_rows,
                instruction_items=instruction_items,
                investigations_section=generate_investigations_section(content.get('investigations', [])),
                referrals_section=generate_referrals_section(content.get('referrals', [])),
                lifestyle_items=generate_lifestyle_items(content.get('lifestyle_modifications', []))
            )

            # Convert to PDF
            options = {
                'encoding': 'UTF-8',
                'enable-local-file-access': None
            }
            pdf_content = pdfkit.from_string(html_content, False, options=options)
            return pdf_content

    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        logger.error(f"Content data: {content}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 