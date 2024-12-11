from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, UUID4
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
from supabase import create_client, Client

from database import execute_sql_query, get_db_structure
from utils.custom_types import ChatRequest, DBCredentials
from utils.database_utils import get_db_credentials
from llm import open_ai, gemini
from config import OPENAI_MODEL, GEMINI_MODEL, SUPABASE_URL, SUPABASE_KEY
from utils.health_queries import (
    get_nutrition_summary,
    get_sensor_stats,
    get_food_consumption,
    get_nutrition_trends
)

# Configure logging and Supabase
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

class HealthReportRequest(BaseModel):
    user_id: UUID4
    llm_choice: str = "openai"

class HealthReportResponse(BaseModel):
    report_id: UUID4
    message: str

class HealthReportStatus(BaseModel):
    id: UUID4
    status: str
    report_content: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

async def get_table_data(query: str, user_id: str, llm_choice: str) -> Dict[str, Any]:
    """Get data using the chat endpoint's query generation"""
    logger.info(f"Generating SQL for query: {query}")
    
    db_credentials = get_db_credentials()
    db_structure = get_db_structure(db_credentials)
    
    system_message = f"""You are a helpful AI assistant that can query a PostgreSQL database. 
    When generating SQL queries, do not include ``` or 'sql' tags. Only return the raw SQL query.
    Here's the database schema: {db_structure}
    
    Important: Always include user_id = '{user_id}' in WHERE clauses for security.
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]

    # Generate SQL query using specified LLM
    try:
        if llm_choice == "openai":
            logger.debug(f"Using OpenAI to generate SQL for: {query}")
            response = open_ai.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0,
            )
            sql_query = response.choices[0].message.content.strip()
        elif llm_choice == "gemini":
            logger.debug(f"Using Gemini to generate SQL for: {query}")
            model = gemini.genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content([m['content'] for m in messages])
            sql_query = response.text.strip()
        else:
            raise HTTPException(status_code=400, detail="Invalid LLM choice")
        
        logger.info(f"Generated SQL query: {sql_query}")

    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

    # Execute the generated query
    try:
        logger.debug(f"Executing SQL query for user {user_id}")
        results = execute_sql_query(sql_query, db_credentials)
        logger.info(f"Query returned {len(results)} results")
        return {
            "query": sql_query,
            "results": results
        }
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

async def fetch_rag_data(query: str, user_id: str, llm_choice: str) -> str:
    """Fetch data using RAG query endpoint"""
    logger.info(f"Fetching RAG data for query: {query}")
    
    try:
        from routers.rag_query_v2 import RAGQueryRequest, rag_query
        
        request = RAGQueryRequest(
            query=query,
            match_count=5,
            llm_choice=llm_choice,
            user_id=user_id
        )
        
        response = await rag_query(request)
        logger.debug(f"RAG response received for query: {query}")
        return response["response"]
    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

async def get_health_data(user_id: str, db_credentials: DBCredentials) -> Dict[str, Any]:
    """Fetch all health-related data"""
    try:
        nutrition_summary = get_nutrition_summary(user_id, db_credentials)
        sensor_stats = get_sensor_stats(user_id, db_credentials)
        food_consumption = get_food_consumption(user_id, db_credentials)
        nutrition_trends = get_nutrition_trends(user_id, db_credentials)
        
        return {
            "nutrition_summary": nutrition_summary,
            "sensor_stats": sensor_stats,
            "food_consumption": food_consumption,
            "nutrition_trends": nutrition_trends
        }
    except Exception as e:
        logger.error(f"Error fetching health data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch health data: {str(e)}")

async def update_report_status(report_id: UUID4, status: str, error_message: Optional[str] = None):
    """Update the status of a report"""
    try:
        data = {
            "status": status,
            "error_message": error_message,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("health_reports").update(data).eq("id", str(report_id)).execute()
    except Exception as e:
        logger.error(f"Failed to update report status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update report status: {str(e)}")

async def update_report_content(report_id: UUID4, content: str):
    """Update the report content"""
    try:
        data = {
            "status": "completed",
            "report_content": content,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("health_reports").update(data).eq("id", str(report_id)).execute()
    except Exception as e:
        logger.error(f"Failed to update report content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update report content: {str(e)}")

async def create_report_record(user_id: UUID4, llm_choice: str) -> UUID4:
    """Create initial report record"""
    try:
        data = {
            "user_id": str(user_id),
            "status": "pending",
            "llm_choice": llm_choice,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("health_reports").insert(data).execute()
        return result.data[0]['id']
    except Exception as e:
        logger.error(f"Failed to create report record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create report record: {str(e)}")

async def generate_report_background(report_id: UUID4, request: HealthReportRequest):
    """Background task to generate report"""
    try:
        # Update status to generating
        await update_report_status(report_id, 'generating')
        
        # Fetch RAG data
        logger.info("Fetching RAG data...")
        rag_queries = [
            "List all my current medications, prescriptions, and their dosages. Include any recent changes.",
            "Summarize my physical activity and exercise routine. Include any fitness goals, achievements, and regular activities.",
            "What are my chronic conditions or ongoing health issues? Include any allergies or medical conditions.",
            "List my recent medical appointments, diagnoses, and test results. Include any doctor's recommendations."
        ]
        
        rag_data = await asyncio.gather(*[
            fetch_rag_data(query, str(request.user_id), request.llm_choice)
            for query in rag_queries
        ])
        
        # Fetch table data using deterministic queries
        logger.info("Fetching health data...")
        db_credentials = get_db_credentials()
        health_data = await get_health_data(str(request.user_id), db_credentials)
        
        # Construct the report prompt
        report_prompt = f"""
        Create a comprehensive health report in markdown format. Use the following data sources carefully to avoid redundancy:

        Medical Information:
        - Current Medications and Prescriptions: {rag_data[0]}
        - Chronic Conditions and Health Issues: {rag_data[2]}
        - Recent Medical History: {rag_data[3]}
        
        Sensor Data Statistics (Last 30 Days):
        {health_data['sensor_stats']}

        Nutrition and Diet:
        - Daily Nutrition Summary: {health_data['nutrition_summary']}
        - Food Consumption Patterns: {health_data['food_consumption']}
        - Overall Nutrition Trends: {health_data['nutrition_trends']}

        Physical Activity and Fitness:
        {rag_data[1]}

        Format the report with these sections:

        1. Executive Summary
           - Brief overview of overall health status
           - Key metrics and important findings
           - Any immediate concerns or improvements

        2. Medical Overview
           - Current Medications and Treatments
           - Recent Medical History
           - Important Health Records
           - Ongoing Medical Conditions (if any)

        3. Vital Signs Analysis
           - Heart Rate Trends (min, max, average)
           - Temperature Patterns
           - Other Sensor Measurements
           - Comparison with Normal Ranges

        4. Nutrition and Diet Assessment
           - Caloric Intake Analysis
           - Macronutrient Distribution (proteins, carbs, fats)
           - Most Frequent Food Choices
           - Dietary Patterns and Trends
           - Areas for Nutritional Improvement

        5. Physical Activity and Fitness
           - Activity Level Assessment
           - Exercise Patterns
           - Progress and Trends
           - Movement and Activity Recommendations

        6. Recommendations and Action Items
           - Medical Follow-ups (if needed)
           - Dietary Adjustments
           - Fitness Goals
           - Lifestyle Modifications
           - Preventive Health Measures

        Guidelines:
        1. Make it professional but easy to understand
        2. Use markdown formatting (headers, lists, bold for important points)
        3. Include specific numbers and trends where relevant
        4. Highlight any concerning patterns or notable improvements
        5. Provide actionable recommendations based on the data
        6. Use tables or bullet points for better readability
        7. Add context to numbers (e.g., "heart rate of 75 bpm is within normal range")

        Focus on creating a cohesive narrative that connects all health aspects while maintaining clear section separation.
        """

        # Generate the report using the specified LLM
        try:
            if request.llm_choice == "openai":
                logger.debug("Using OpenAI for final report generation")
                response = open_ai.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": report_prompt}],
                    temperature=0.7,
                )
                report_content = response.choices[0].message.content
            elif request.llm_choice == "gemini":
                logger.debug("Using Gemini for final report generation")
                model = gemini.genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content(report_prompt)
                report_content = response.text
            else:
                raise HTTPException(status_code=400, detail="Invalid LLM choice")

            # Update report with content
            await update_report_content(report_id, report_content)
            logger.info(f"Report generation completed for report_id: {report_id}")

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            await update_report_status(report_id, 'failed', str(e))
            
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        await update_report_status(report_id, 'failed', str(e))

@router.post("/health-report", response_model=HealthReportResponse)
async def create_health_report(request: HealthReportRequest) -> HealthReportResponse:
    """Start report generation process"""
    try:
        # Create initial report record
        report_id = await create_report_record(request.user_id, request.llm_choice)
        
        # Start background task
        asyncio.create_task(generate_report_background(report_id, request))
        
        return HealthReportResponse(
            report_id=report_id,
            message="Report generation started"
        )
    except Exception as e:
        logger.error(f"Failed to start report generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-report/{report_id}", response_model=HealthReportStatus)
async def get_report_status(report_id: UUID4) -> HealthReportStatus:
    """Get the status of a report"""
    query = """
    SELECT id, status, report_content, error_message, created_at, updated_at
    FROM health_reports
    WHERE id = :report_id
    """
    params = {"report_id": str(report_id)}
    result = await execute_sql_query(query, get_db_credentials(), params)
    
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return HealthReportStatus(**result[0])