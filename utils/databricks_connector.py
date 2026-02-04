"""
Databricks Connector for Provider Verification Dashboard
Handles connection to Databricks and table discovery
"""

import os
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class DatabricksConnector:
    """
    Connects to Databricks and provides methods to:
    - List available tables from specified catalogs/schemas
    - Load data from Delta tables
    - Cache results to reduce API calls
    """
    
    def __init__(self, host: str, token: str, http_path: str, 
                 catalogs: Optional[List[str]] = None,
                 schemas: Optional[List[str]] = None,
                 table_pattern: Optional[str] = None,
                 cache_duration: int = 5):
        """
        Initialize Databricks connector.
        
        Args:
            host: Databricks workspace URL (e.g., https://adb-xxx.azuredatabricks.net)
            token: Personal access token
            http_path: SQL Warehouse or cluster HTTP path
            catalogs: List of catalogs to scan (None = all accessible)
            schemas: List of schemas to include (None = all)
            table_pattern: Regex pattern to filter table names (None = all)
            cache_duration: Cache duration in minutes
        """
        self.host = host.replace('https://', '')
        self.token = token
        self.http_path = http_path
        self.catalogs = catalogs or []
        self.schemas = schemas or []
        self.table_pattern = table_pattern
        self.cache_duration = cache_duration
        
        # Cache for table list
        self._table_cache = None
        self._cache_timestamp = None
        
        # Import here to fail gracefully if not installed
        try:
            from databricks import sql
            self.sql = sql
        except ImportError:
            raise ImportError(
                "databricks-sql-connector not installed. "
                "Install with: pip install databricks-sql-connector"
            )
    
    def _get_connection(self):
        """Create a new Databricks SQL connection."""
        return self.sql.connect(
            server_hostname=self.host,
            http_path=self.http_path,
            access_token=self.token
        )
    
    def _is_cache_valid(self) -> bool:
        """Check if cached table list is still valid."""
        if self._table_cache is None or self._cache_timestamp is None:
            return False
        
        elapsed = datetime.now() - self._cache_timestamp
        return elapsed < timedelta(minutes=self.cache_duration)
    
    def list_available_tables(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List all available tables from configured catalogs and schemas.
        
        Args:
            force_refresh: Force refresh cache
            
        Returns:
            List of table info dicts with keys:
                - full_name: catalog.schema.table
                - catalog: catalog name
                - schema: schema name
                - table_name: table name
                - table_type: TABLE, VIEW, etc.
                - row_count: estimated row count (if available)
        """
        # Return cached results if valid
        if not force_refresh and self._is_cache_valid():
            return self._table_cache
        
        tables = []
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Build query to list tables
            catalog_filter = ""
            if self.catalogs:
                catalog_list = "', '".join(self.catalogs)
                catalog_filter = f"AND table_catalog IN ('{catalog_list}')"
            
            schema_filter = ""
            if self.schemas:
                schema_list = "', '".join(self.schemas)
                schema_filter = f"AND table_schema IN ('{schema_list}')"
            
            query = f"""
                SELECT 
                    table_catalog,
                    table_schema,
                    table_name,
                    table_type
                FROM system.information_schema.tables
                WHERE 1=1
                  {catalog_filter}
                  {schema_filter}
                  AND table_schema != 'information_schema'
                ORDER BY table_catalog, table_schema, table_name
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                catalog, schema, table_name, table_type = row
                full_name = f"{catalog}.{schema}.{table_name}"
                
                # Apply table name pattern filter
                if self.table_pattern:
                    patterns = [p.strip() for p in self.table_pattern.split(',')]
                    if not any(re.search(pattern, table_name, re.IGNORECASE) for pattern in patterns):
                        continue
                
                # Try to get row count (may fail for some tables)
                row_count = None
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
                    count_result = cursor.fetchone()
                    if count_result:
                        row_count = count_result[0]
                except:
                    pass  # Row count not critical
                
                tables.append({
                    'full_name': full_name,
                    'catalog': catalog,
                    'schema': schema,
                    'table_name': table_name,
                    'table_type': table_type,
                    'row_count': row_count
                })
            
            cursor.close()
            connection.close()
            
            # Update cache
            self._table_cache = tables
            self._cache_timestamp = datetime.now()
            
        except Exception as e:
            print(f"Error listing tables: {str(e)}")
            # Return empty list on error
            tables = []
        
        return tables
    
    def load_table_data(self, table_name: str, limit: Optional[int] = None, csv_file_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load data from a Databricks table.
        
        Args:
            table_name: Full table name (catalog.schema.table)
            limit: Optional row limit
            csv_file_id: Optional filter by csv_file_id column
            
        Returns:
            List of row dictionaries
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Build query
            query = f"SELECT * FROM {table_name}"
            
            # Add WHERE clause if csv_file_id is provided
            if csv_file_id:
                query += f" WHERE csv_file_id = '{csv_file_id}'"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert to JSON-serializable types
                    if value is None:
                        row_dict[col] = None
                    elif isinstance(value, (str, int, float, bool)):
                        row_dict[col] = value
                    else:
                        row_dict[col] = str(value)
                data.append(row_dict)
            
            cursor.close()
            connection.close()
            
            return data
            
        except Exception as e:
            raise Exception(f"Error loading table data: {str(e)}")
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test the Databricks connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            connection.close()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
