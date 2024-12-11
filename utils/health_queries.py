from typing import Dict, Any
from datetime import datetime, timedelta
from database import execute_sql_query
from utils.custom_types import DBCredentials

def get_nutrition_summary(user_id: str, db_credentials: DBCredentials, days: int = 30) -> Dict[str, Any]:
    """Get nutrition summary for the last N days"""
    query = """
    SELECT 
        dn.date,
        dn.total_calories,
        SUM(cf.protein) as total_protein,
        SUM(cf.carbs) as total_carbs,
        SUM(cf.fat) as total_fat
    FROM daily_nutrition dn
    LEFT JOIN consumed_foods cf ON cf.daily_nutrition_id = dn.id
    WHERE dn.user_id = :user_id 
    AND dn.date >= CURRENT_DATE - INTERVAL :days_interval
    GROUP BY dn.date, dn.total_calories
    ORDER BY dn.date DESC
    """
    
    params = {"user_id": user_id, "days_interval": f"{days} days"}
    return execute_sql_query(query, db_credentials, params)

def get_sensor_stats(user_id: str, db_credentials: DBCredentials, days: int = 30) -> Dict[str, Any]:
    """Get average sensor readings for the last N days"""
    query = """
    SELECT 
        AVG(beat_avg) as avg_heart_rate,
        AVG(temperature_c) as avg_temperature,
        AVG(humidity) as avg_humidity,
        MIN(beat_avg) as min_heart_rate,
        MAX(beat_avg) as max_heart_rate,
        MIN(temperature_c) as min_temperature,
        MAX(temperature_c) as max_temperature
    FROM sensor_data
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL :days_interval
    """
    
    params = {"days_interval": f"{days} days"}
    return execute_sql_query(query, db_credentials, params)

def get_food_consumption(user_id: str, db_credentials: DBCredentials, days: int = 30, limit: int = 10) -> Dict[str, Any]:
    """Get top consumed foods for the last N days"""
    query = """
    SELECT 
        cf.food_name,
        COUNT(*) as consumption_count,
        AVG(cf.calories) as avg_calories,
        AVG(cf.protein) as avg_protein,
        AVG(cf.carbs) as avg_carbs,
        AVG(cf.fat) as avg_fat
    FROM consumed_foods cf
    JOIN daily_nutrition dn ON cf.daily_nutrition_id = dn.id
    WHERE dn.user_id = :user_id 
    AND cf.consumed_at >= CURRENT_TIMESTAMP - INTERVAL :days_interval
    GROUP BY cf.food_name
    ORDER BY consumption_count DESC
    LIMIT :limit
    """
    
    params = {"user_id": user_id, "days_interval": f"{days} days", "limit": limit}
    return execute_sql_query(query, db_credentials, params)

def get_nutrition_trends(user_id: str, db_credentials: DBCredentials, days: int = 30) -> Dict[str, Any]:
    """Get daily nutrition trends including averages and totals"""
    query = """
    WITH daily_macros AS (
        SELECT 
            dn.date,
            dn.total_calories,
            SUM(cf.protein) as total_protein,
            SUM(cf.carbs) as total_carbs,
            SUM(cf.fat) as total_fat
        FROM daily_nutrition dn
        LEFT JOIN consumed_foods cf ON cf.daily_nutrition_id = dn.id
        WHERE dn.user_id = :user_id 
        AND dn.date >= CURRENT_DATE - INTERVAL :days_interval
        GROUP BY dn.date, dn.total_calories
    )
    SELECT 
        AVG(total_calories) as avg_daily_calories,
        AVG(total_protein) as avg_daily_protein,
        AVG(total_carbs) as avg_daily_carbs,
        AVG(total_fat) as avg_daily_fat,
        MAX(total_calories) as max_daily_calories,
        MIN(total_calories) as min_daily_calories,
        COUNT(*) as days_tracked
    FROM daily_macros
    """
    
    params = {"user_id": user_id, "days_interval": f"{days} days"}
    return execute_sql_query(query, db_credentials, params) 