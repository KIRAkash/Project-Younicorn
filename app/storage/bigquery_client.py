# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""BigQuery client for Project Minerva data storage."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from ..config import config

logger = logging.getLogger(__name__)


class BigQueryClient:
    """BigQuery client for managing Project Minerva data."""
    
    def __init__(self):
        """Initialize BigQuery client."""
        self.client = bigquery.Client()
        self.dataset_id = config.bigquery_dataset
        self.project_id = self.client.project
        self.dataset_ref = self.client.dataset(self.dataset_id)
        
        # Ensure dataset exists
        self._ensure_dataset_exists()
        
        # Table schemas
        self.table_schemas = {
            "startups": self._get_startup_schema(),
            "analyses": self._get_analysis_schema(),
            "users": self._get_user_schema(),
            "teams": self._get_team_schema(),
            "comments": self._get_comment_schema(),
            "agent_traces": self._get_agent_trace_schema(),
            "sources": self._get_source_schema(),
        }
        
        # Ensure all tables exist
        self._ensure_tables_exist()
    
    def _ensure_dataset_exists(self) -> None:
        """Ensure the dataset exists, create if not."""
        try:
            self.client.get_dataset(self.dataset_ref)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = config.bigquery_location
            dataset.description = "Project Minerva - AI-Powered Startup Due Diligence Platform"
            
            dataset = self.client.create_dataset(dataset, timeout=30)
            logger.info(f"Created dataset {self.dataset_id}")
    
    def _ensure_tables_exist(self) -> None:
        """Ensure all required tables exist."""
        for table_name, schema in self.table_schemas.items():
            self._ensure_table_exists(table_name, schema)
    
    def _ensure_table_exists(self, table_name: str, schema: List[bigquery.SchemaField]) -> None:
        """Ensure a specific table exists."""
        table_ref = self.dataset_ref.table(table_name)
        
        try:
            self.client.get_table(table_ref)
            logger.info(f"Table {table_name} already exists")
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"Created table {table_name}")
    
    def _get_startup_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for startups table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("industry", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("funding_stage", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("website_url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("founded_date", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("employee_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("revenue_run_rate", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("funding_raised", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("funding_seeking", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("founders", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("documents", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("submitted_by", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("submission_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_updated", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        ]
    
    def _get_analysis_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for analyses table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("request_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("overall_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("team_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("market_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("product_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("competition_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("investment_recommendation", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("confidence_level", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("executive_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("investment_memo", "STRING", mode="NULLABLE"),
            # Individual agent analysis columns
            bigquery.SchemaField("team_analysis", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("market_analysis", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("product_analysis", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("competition_analysis", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("synthesis_analysis", "JSON", mode="NULLABLE"),
            # Legacy field for backward compatibility
            bigquery.SchemaField("agent_analyses", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("risks_opportunities", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("key_insights", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("started_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("completed_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("total_duration_seconds", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("version", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("last_updated", "TIMESTAMP", mode="REQUIRED"),
        ]
    
    def _get_user_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for users table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("full_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("bio", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("avatar_url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("hashed_password", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("is_verified", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("email_notifications", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("timezone", "STRING", mode="REQUIRED"),
        ]
    
    def _get_team_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for teams table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("max_members", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("subscription_tier", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("members", "JSON", mode="NULLABLE"),
        ]
    
    def _get_comment_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for comments table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("parent_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("comment_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("section", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("agent_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("is_resolved", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("resolved_by", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resolved_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("likes", "INTEGER", mode="REQUIRED"),
        ]
    
    def _get_agent_trace_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for agent traces table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("agent_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("step_number", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("action", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("reasoning", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tool_used", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("input_data", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("output_data", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("duration_seconds", "FLOAT", mode="NULLABLE"),
        ]
    
    def _get_source_schema(self) -> List[bigquery.SchemaField]:
        """Get schema for sources table."""
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("citation_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("domain", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("document_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("page_number", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("excerpt", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("confidence_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("supported_claims", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into a table.
        
        Args:
            table_name (str): Name of the table
            rows (List[Dict[str, Any]]): Rows to insert
        """
        table_ref = self.dataset_ref.table(table_name)
        table = self.client.get_table(table_ref)
        
        # Convert datetime objects to strings for JSON serialization
        processed_rows = []
        for row in rows:
            processed_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    processed_row[key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    processed_row[key] = json.dumps(value) if value else None
                else:
                    processed_row[key] = value
            processed_rows.append(processed_row)
        
        errors = self.client.insert_rows_json(table, processed_rows)
        if errors:
            logger.error(f"Error inserting rows into {table_name}: {errors}")
            raise Exception(f"Failed to insert rows: {errors}")
        
        logger.info(f"Inserted {len(rows)} rows into {table_name}")
    
    def query(self, sql: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results.
        
        Args:
            sql (str): SQL query to execute
            parameters (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        job_config = bigquery.QueryJobConfig()
        if parameters:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(key, "STRING", value)
                for key, value in parameters.items()
            ]
        
        query_job = self.client.query(sql, job_config=job_config)
        results = query_job.result()
        
        return [dict(row) for row in results]
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Dict[str, Any]: Table information
        """
        table_ref = self.dataset_ref.table(table_name)
        table = self.client.get_table(table_ref)
        
        return {
            "table_id": table.table_id,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "created": table.created.isoformat() if table.created else None,
            "modified": table.modified.isoformat() if table.modified else None,
            "schema": [{"name": field.name, "type": field.field_type, "mode": field.mode} 
                      for field in table.schema],
        }
