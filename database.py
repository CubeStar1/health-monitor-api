from sqlalchemy import create_engine, text
import pandas as pd
from utils.custom_types import DBCredentials
from typing import Dict, Any, Optional

def get_db_structure(db_credentials: DBCredentials):
    db_url = f"postgresql://{db_credentials.db_user}:{db_credentials.db_password}@{db_credentials.db_host}:{db_credentials.db_port}/{db_credentials.db_name}"
    engine = create_engine(db_url)

    ddl_query = """
    SELECT 
        'CREATE TABLE ' || tablename || ' (' ||
        array_to_string(
            array_agg(
                column_name || ' ' || type || 
                CASE WHEN character_maximum_length IS NOT NULL 
                     THEN '(' || character_maximum_length || ')' 
                     ELSE '' 
                END ||
                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END
            ), 
            ', '
        ) || ');'
    FROM (
        SELECT 
            c.table_name AS tablename, 
            c.column_name, 
            c.is_nullable,
            c.character_maximum_length,
            CASE WHEN c.domain_name IS NOT NULL THEN c.domain_name
                 ELSE c.udt_name
            END AS type,
            c.ordinal_position
        FROM 
            information_schema.columns c
        WHERE 
            table_schema = 'public'
        ORDER BY 
            c.table_name, 
            c.ordinal_position
    ) AS t
    GROUP BY tablename;
    """

    with engine.connect() as connection:
        result = connection.execute(text(ddl_query))
        ddl_statements = [row[0] for row in result]

    return "\n\n".join(ddl_statements)

def execute_sql_query(query: str, db_credentials: DBCredentials, params: Optional[Dict[str, Any]] = None):
    db_url = f"postgresql://{db_credentials.db_user}:{db_credentials.db_password}@{db_credentials.db_host}:{db_credentials.db_port}/{db_credentials.db_name}"
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text(query), params if params else {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df.to_dict(orient="records")