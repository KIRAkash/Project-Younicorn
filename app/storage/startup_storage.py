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

"""Startup data storage operations."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from .bigquery_client import BigQueryClient
from ..models.startup import StartupSubmission

logger = logging.getLogger(__name__)


class StartupStorage:
    """Storage operations for startup submissions."""
    
    def __init__(self, bigquery_client: BigQueryClient):
        """Initialize startup storage.
        
        Args:
            bigquery_client (BigQueryClient): BigQuery client instance
        """
        self.bq_client = bigquery_client
        self._ensure_tables_exist()

    def _ensure_tables_exist(self) -> None:
        """Ensure required tables exist in BigQuery."""
        # Create status_updates table if it doesn't exist
        status_updates_schema = """
        CREATE TABLE IF NOT EXISTS `{project}.{dataset}.startup_status_updates` (
            startup_id STRING,
            status STRING,
            updated_by STRING,
            updated_at TIMESTAMP,
            update_id STRING
        )
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id
        )

        try:
            self.bq_client.query(status_updates_schema)
            logger.info("Ensured startup_status_updates table exists")
        except Exception as e:
            logger.error(f"Failed to create status_updates table: {e}")

    def create_startup(self, startup: StartupSubmission) -> str:
        """Create a new startup submission.
        
        Args:
            startup (StartupSubmission): Startup submission data
            
        Returns:
            str: Created startup ID
        """
        # Create main startup record
        row = {
            "id": str(startup.id),
            "company_name": startup.company_info.name,
            "description": startup.company_info.description,
            "industry": startup.company_info.industry.value,
            "funding_stage": startup.company_info.funding_stage.value,
            "location": startup.company_info.location,
            "website_url": str(startup.company_info.website_url) if startup.company_info.website_url else None,
            "founded_date": startup.company_info.founded_date,
            "employee_count": startup.company_info.employee_count,
            "revenue_run_rate": startup.company_info.revenue_run_rate,
            "funding_raised": startup.company_info.funding_raised,
            "funding_seeking": startup.company_info.funding_seeking,
            "founders": [founder.dict() for founder in startup.founders],
            "documents": [doc.dict() for doc in startup.documents],
            "metadata": startup.metadata.dict(),
            "submitted_by": str(startup.submitted_by),
            "submission_timestamp": startup.submission_timestamp,
            "last_updated": startup.last_updated,
            "initial_status": startup.status,  # Store initial status in main record
        }

        # Insert main record
        self.bq_client.insert_rows("startups", [row])

        # Create initial status update record
        status_row = {
            "startup_id": str(startup.id),
            "status": startup.status,
            "updated_by": str(startup.submitted_by),
            "updated_at": startup.submission_timestamp,
            "update_id": str(uuid4())
        }
        
        # Insert status update
        self.bq_client.insert_rows("startup_status_updates", [status_row])

        logger.info(f"Created startup submission: {startup.id}")
        return str(startup.id)
    
    def get_startup(self, startup_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a startup submission by ID.
        
        Args:
            startup_id (UUID): Startup ID
            
        Returns:
            Optional[Dict[str, Any]]: Startup data or None if not found
        """
        sql = """
        WITH latest_status AS (
            SELECT startup_id, status, updated_at
            FROM `{project}.{dataset}.startup_status_updates`
            WHERE startup_id = @startup_id
            ORDER BY updated_at DESC
            LIMIT 1
        )
        SELECT 
            s.*,
            COALESCE(ls.status, s.initial_status) as status,
            ls.updated_at as status_last_updated
        FROM `{project}.{dataset}.startups` s
        LEFT JOIN latest_status ls
        ON s.id = ls.startup_id
        WHERE s.id = @startup_id
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id
        )
        
        results = self.bq_client.query(sql, {"startup_id": str(startup_id)})
        return results[0] if results else None

    def update_startup_status(self, startup_id: UUID, status: str, updated_by: UUID) -> None:
        """Update startup status by creating a new status update record.

        Args:
            startup_id (UUID): Startup ID
            status (str): New status
            updated_by (UUID): User making the update
        """
        # Insert new status update record
        status_row = {
            "startup_id": str(startup_id),
            "status": status,
            "updated_by": str(updated_by),
            "updated_at": datetime.utcnow(),
            "update_id": str(uuid4())
        }

        self.bq_client.insert_rows("startup_status_updates", [status_row])
        logger.info(f"Updated startup {startup_id} status to {status}")

    def list_startups(
        self, 
        submitted_by: Optional[UUID] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        funding_stage: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List startup submissions with optional filters.
        
        Args:
            submitted_by (Optional[UUID]): Filter by submitter
            status (Optional[str]): Filter by status
            industry (Optional[str]): Filter by industry
            funding_stage (Optional[str]): Filter by funding stage
            limit (int): Maximum number of results
            offset (int): Offset for pagination
            
        Returns:
            List[Dict[str, Any]]: List of startup submissions
        """
        where_clauses = []
        parameters = {}
        
        # Build the subquery to get latest status for each startup
        sql = """
        WITH latest_status AS (
            SELECT startup_id, status, updated_at
            FROM (
                SELECT startup_id, status, updated_at,
                    ROW_NUMBER() OVER (PARTITION BY startup_id ORDER BY updated_at DESC) as rn
                FROM `{project}.{dataset}.startup_status_updates`
            )
            WHERE rn = 1
        )
        SELECT 
            s.*,
            COALESCE(ls.status, s.initial_status) as current_status,
            ls.updated_at as status_last_updated
        FROM `{project}.{dataset}.startups` s
        LEFT JOIN latest_status ls
        ON s.id = ls.startup_id
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id
        )

        if submitted_by:
            where_clauses.append("s.submitted_by = @submitted_by")
            parameters["submitted_by"] = str(submitted_by)
        
        if status:
            where_clauses.append("COALESCE(ls.status, s.initial_status) = @status")
            parameters["status"] = status
        
        if industry:
            where_clauses.append("s.industry = @industry")
            parameters["industry"] = industry
        
        if funding_stage:
            where_clauses.append("s.funding_stage = @funding_stage")
            parameters["funding_stage"] = funding_stage
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += """
        ORDER BY s.submission_timestamp DESC
        LIMIT {limit}
        OFFSET {offset}
        """.format(limit=limit, offset=offset)

        return self.bq_client.query(sql, parameters)
    
    def search_startups(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search startups by company name or description.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        sql = """
        SELECT *
        FROM `{project}.{dataset}.startups`
        WHERE LOWER(company_name) LIKE LOWER(@query)
           OR LOWER(description) LIKE LOWER(@query)
        ORDER BY submission_timestamp DESC
        LIMIT {limit}
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id,
            limit=limit
        )
        
        search_query = f"%{query}%"
        return self.bq_client.query(sql, {"query": search_query})
    
    def get_startup_statistics(self) -> Dict[str, Any]:
        """Get startup submission statistics.
        
        Returns:
            Dict[str, Any]: Statistics about startup submissions
        """
        sql = """
        SELECT 
            COUNT(*) as total_startups,
            COUNT(DISTINCT industry) as unique_industries,
            COUNT(DISTINCT funding_stage) as unique_funding_stages,
            AVG(employee_count) as avg_employee_count,
            AVG(funding_raised) as avg_funding_raised,
            AVG(funding_seeking) as avg_funding_seeking,
            COUNT(CASE WHEN status = 'submitted' THEN 1 END) as pending_analysis,
            COUNT(CASE WHEN status = 'analyzing' THEN 1 END) as in_analysis,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_analysis
        FROM `{project}.{dataset}.startups`
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id
        )
        
        results = self.bq_client.query(sql)
        return results[0] if results else {}
    
    def get_startups_by_industry(self) -> List[Dict[str, Any]]:
        """Get startup count by industry.
        
        Returns:
            List[Dict[str, Any]]: Industry breakdown
        """
        sql = """
        SELECT 
            industry,
            COUNT(*) as count,
            AVG(funding_raised) as avg_funding_raised,
            AVG(employee_count) as avg_employee_count
        FROM `{project}.{dataset}.startups`
        WHERE industry IS NOT NULL
        GROUP BY industry
        ORDER BY count DESC
        """.format(
            project=self.bq_client.project_id,
            dataset=self.bq_client.dataset_id
        )
        
        return self.bq_client.query(sql)
