"""
Test script to verify Databricks POC catalog connection and configuration.

This script tests:
1. Connection to Databricks workspace
2. Access to POC catalog
3. Schemas within POC catalog
4. Tables in POC.default schema
5. Data preview from first table

Run: python test_poc_catalog.py
"""

import os
from dotenv import load_dotenv

# Try to import databricks-sql-connector
try:
    from databricks import sql
except ImportError:
    print("❌ Error: databricks-sql-connector not installed")
    print("\nInstall it with:")
    print("  pip install databricks-sql-connector")
    exit(1)

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 Testing Databricks POC Catalog Connection")
print("=" * 60)

# Check required environment variables
print("\n📋 Checking Configuration...")
required_vars = {
    'DATABRICKS_HOST': os.getenv('DATABRICKS_HOST'),
    'DATABRICKS_TOKEN': os.getenv('DATABRICKS_TOKEN'),
    'DATABRICKS_HTTP_PATH': os.getenv('DATABRICKS_HTTP_PATH'),
    'DATABRICKS_CATALOGS': os.getenv('DATABRICKS_CATALOGS'),
    'DATABRICKS_SCHEMAS': os.getenv('DATABRICKS_SCHEMAS')
}

all_set = True
for key, value in required_vars.items():
    if value:
        if 'TOKEN' in key:
            display_value = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
        else:
            display_value = value
        print(f"  ✅ {key}: {display_value}")
    else:
        print(f"  ❌ {key}: Not set")
        all_set = False

if not all_set:
    print("\n❌ Missing required configuration in .env file")
    print("Please check your .env file and try again.")
    exit(1)

print("\n✅ All required configuration variables are set")

# Connect to Databricks
print("\n🔌 Connecting to Databricks...")
try:
    connection = sql.connect(
        server_hostname=os.getenv('DATABRICKS_HOST').replace('https://', ''),
        http_path=os.getenv('DATABRICKS_HTTP_PATH'),
        access_token=os.getenv('DATABRICKS_TOKEN')
    )
    cursor = connection.cursor()
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify DATABRICKS_HOST is correct")
    print("2. Check if DATABRICKS_TOKEN is valid (not expired)")
    print("3. Verify DATABRICKS_HTTP_PATH points to a running SQL Warehouse")
    print("4. Make sure your network allows access to Databricks")
    exit(1)

# Test 1: List all catalogs
print("\n" + "=" * 60)
print("📦 TEST 1: Checking Available Catalogs")
print("=" * 60)

# Get target catalog from config
target_catalog = os.getenv('DATABRICKS_CATALOGS', '').split(',')[0].strip()

try:
    cursor.execute("SHOW CATALOGS")
    catalogs = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(catalogs)} catalog(s):")
    for cat in catalogs:
        if cat.upper() == target_catalog.upper():
            print(f"  ✅ {cat} (Target catalog)")
        else:
            print(f"  - {cat}")
    
    # Check if target catalog exists (case-insensitive)
    poc_exists = any(cat.upper() == target_catalog.upper() for cat in catalogs)
    if poc_exists:
        print(f"\n✅ '{target_catalog}' catalog found!")
    else:
        print(f"\n⚠️  '{target_catalog}' catalog NOT found!")
        print("Available catalogs:", ', '.join(catalogs))
        print("\nUpdate DATABRICKS_CATALOGS in .env to one of the available catalogs")
except Exception as e:
    print(f"❌ Error listing catalogs: {str(e)}")
    poc_exists = False

# Test 2: List schemas in catalog
print("\n" + "=" * 60)
print(f"📂 TEST 2: Checking Schemas in {target_catalog} Catalog")
print("=" * 60)

default_exists = False
schemas = []

try:
    cursor.execute(f"SHOW SCHEMAS IN {target_catalog}")
    schemas = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(schemas)} schema(s) in {target_catalog}:")
    for schema in schemas:
        if schema == 'information_schema':
            print(f"  ℹ️  {schema} (System schema - auto-generated)")
        elif schema == 'default':
            print(f"  ✅ {schema} (Target schema)")
        else:
            print(f"  - {schema}")
    
    # Check if default exists
    default_exists = 'default' in schemas
    if default_exists:
        print("\n✅ 'default' schema found!")
    else:
        print("\n⚠️  'default' schema NOT found!")
        print("Available schemas:", ', '.join([s for s in schemas if s != 'information_schema']))
except Exception as e:
    print(f"❌ Error listing schemas: {str(e)}")
    print(f"This might mean the {target_catalog} catalog doesn't exist or you don't have access")

# Test 3: List tables in target catalog.default
print("\n" + "=" * 60)
print(f"📊 TEST 3: Checking Tables in {target_catalog}.default")
print("=" * 60)
try:
    cursor.execute(f"""
        SELECT table_name, table_type
        FROM system.information_schema.tables
        WHERE table_catalog = '{target_catalog}'
          AND table_schema = 'default'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"Found {len(tables)} table(s) in {target_catalog}.default:")
        for table in tables:
            print(f"  📄 {table[0]} ({table[1]})")
        print("\n✅ Tables found! Your dashboard will display these tables.")
    else:
        print(f"⚠️  No tables found in {target_catalog}.default schema")
        print("\nPossible reasons:")
        print("1. No tables have been created in this schema yet")
        print("2. Tables exist but you don't have SELECT permission")
        print("3. Tables are in a different schema")
        print("\nCreate a test table:")
        print(f"  CREATE TABLE {target_catalog}.default.test_table (id INT, name STRING);")
        tables = []  # Set to empty for next test
except Exception as e:
    print(f"❌ Error listing tables: {str(e)}")
    tables = []

# Test 4: Preview data from first table
if tables:
    print("\n" + "=" * 60)
    print("📄 TEST 4: Previewing Data from First Table")
    print("=" * 60)
    first_table = tables[0][0]
    print(f"Table: {target_catalog}.default.{first_table}")
    try:
        cursor.execute(f"SELECT * FROM {target_catalog}.default.{first_table} LIMIT 5")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        print(f"\n✅ Successfully queried table!")
        print(f"  Columns: {len(columns)}")
        print(f"  Sample columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
        print(f"  Rows returned: {len(rows)}")
        
        if rows:
            print("\nFirst row preview:")
            for i, col in enumerate(columns[:5]):
                value = rows[0][i] if i < len(rows[0]) else 'N/A'
                print(f"  - {col}: {value}")
            if len(columns) > 5:
                print(f"  ... and {len(columns) - 5} more columns")
        else:
            print("\n⚠️  Table exists but has no data")
    except Exception as e:
        print(f"❌ Error previewing data: {str(e)}")
        print("You may not have SELECT permission on this table")

# Test 5: Verify configuration matches reality
print("\n" + "=" * 60)
print("🎯 TEST 5: Configuration Validation")
print("=" * 60)
config_catalogs = os.getenv('DATABRICKS_CATALOGS', '').split(',')
config_schemas = os.getenv('DATABRICKS_SCHEMAS', '').split(',')

print(f"\nYour .env configuration:")
print(f"  DATABRICKS_CATALOGS={os.getenv('DATABRICKS_CATALOGS')}")
print(f"  DATABRICKS_SCHEMAS={os.getenv('DATABRICKS_SCHEMAS')}")

if tables:
    print(f"\n✅ Configuration is correct!")
    print(f"   Your dashboard will show {len(tables)} table(s) from {target_catalog}.default")
elif poc_exists and default_exists:
    print(f"\n⚠️  Configuration is correct, but no tables found")
    print(f"   Create some tables in {target_catalog}.default to see them in the dashboard")
else:
    print(f"\n❌ Configuration needs adjustment")
    if not poc_exists:
        print(f"   Update DATABRICKS_CATALOGS to one of: {', '.join(catalogs)}")
    if not default_exists:
        print(f"   Update DATABRICKS_SCHEMAS to one of: {', '.join([s for s in schemas if s != 'information_schema'])}")

# Close connection
cursor.close()
connection.close()

# Final summary
print("\n" + "=" * 60)
print("📋 SUMMARY")
print("=" * 60)
print(f"✅ Connection: Successful")
print(f"{'✅' if poc_exists else '❌'} {target_catalog} Catalog: {'Found' if poc_exists else 'Not found'}")
print(f"{'✅' if default_exists else '❌'} default Schema: {'Found' if default_exists else 'Not found'}")
print(f"{'✅' if tables else '⚠️ '} Tables: {len(tables) if tables else 'None found'}")

if tables:
    print("\n🎉 All tests passed! Your Databricks integration is ready.")
    print("\nNext steps:")
    print("  1. Start your Flask app: python app.py")
    print("  2. Go to http://localhost:8080")
    print("  3. Click '📊 Databricks Tables' tab")
    print("  4. Select a table and load the data")
else:
    print("\n⚠️  Setup incomplete. Review the test results above.")

print("\n" + "=" * 60)
