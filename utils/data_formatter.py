"""
Data formatting utilities for dashboard display
Parses pre-processed CSV/Excel/JSON data with verification results
"""

import pandas as pd
import json
from datetime import datetime


def parse_json_data(json_data):
    """
    Parse JSON data with provider verification results.
    Maps your specific JSON structure to dashboard format.
    
    Args:
        json_data: List of dictionaries or single dictionary from JSON file
        
    Returns:
        tuple: (parsed_data_list, validation_errors)
    """
    validation_errors = []
    parsed_data = []
    
    # Ensure json_data is a list
    if isinstance(json_data, dict):
        json_data = [json_data]
    
    for idx, record in enumerate(json_data):
        try:
            # Map JSON fields to dashboard format
            npi = record.get('source_npi', '')
            provider_name = record.get('provider_name') or record.get('source_provider_name', '')
            
            # Address fields
            address = record.get('address', record.get('source_address', ''))
            city = record.get('city', record.get('source_city', ''))
            state = record.get('state', record.get('source_state', ''))
            zip_code = record.get('zipcode', '')
            
            # Source versions (for address display)
            source_city = record.get('source_city', city)
            source_state = record.get('source_state', state)
            source_zip = record.get('source_zipcode', record.get('source_zip', zip_code))
            
            # Contact info
            phone = record.get('phone', '')
            fax = record.get('fax', '')
            email = record.get('email', '')
            
            # Confidence score: Use address_confidence_score if available (numerical), otherwise map from confidence_measure
            if 'address_confidence_score' in record:
                try:
                    confidence_score = float(record.get('address_confidence_score', 0))
                    # Ensure it's in 0-100 range
                    if confidence_score > 1 and confidence_score <= 100:
                        confidence_score = int(confidence_score)
                    elif confidence_score <= 1:
                        confidence_score = int(confidence_score * 100)
                    else:
                        confidence_score = 0
                except:
                    confidence_score = 0
            else:
                # Fallback to confidence_measure mapping
                confidence_raw = record.get('confidence_measure', 'Medium')
                if confidence_raw == 'High':
                    confidence_score = 90
                elif confidence_raw == 'Medium':
                    confidence_score = 70
                elif confidence_raw == 'Low':
                    confidence_score = 40
                else:
                    confidence_score = 50
            
            # Status logic:
            # - Verified: phone AND address found, AND confidence >= 80%
            # - Failed: no address found
            # - Needs Review: confidence < 80% or other conditions
            has_address = bool(address and address.strip())
            has_phone = bool(phone and phone.strip())
            
            if not has_address:
                status = 'failed'
            elif has_phone and has_address and confidence_score >= 80:
                status = 'verified'
            else:
                status = 'needs_review'
            
            # Sources - extract from various source fields
            sources = []
            for i in range(1, 6):
                source = record.get(f'addr_source_{i}') or record.get(f'phone_source_{i}')
                if source and source not in ['NA', 'null', None]:
                    sources.append(source)
            
            # Remove duplicates and add primary sources
            if record.get('addr_source') and record.get('addr_source') not in ['NA', None]:
                sources.insert(0, record.get('addr_source'))
            
            sources = list(dict.fromkeys(sources))  # Remove duplicates while preserving order
            
            # Specialty/Facility
            specialty = record.get('facility_name', '')
            
            # Operating hours - extract from operational_status_value fields
            hours_info = ''
            for i in range(1, 6):
                value = record.get(f'operational_status_value_{i}', '')
                if value and value not in ['NA', 'null', None, '']:
                    # Check if this looks like hours information (contains time indicators)
                    if any(indicator in str(value).lower() for indicator in ['am', 'pm', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'closed', ':']):
                        hours_info = value
                        break
            
            # Discrepancies - check for mismatches
            discrepancies = []
            if record.get('error_message'):
                discrepancies.append(record.get('error_message'))
            if record.get('llm_parse_error'):
                discrepancies.append(f"Parse error: {record.get('llm_parse_error')}")
            
            # Address change detection
            source_addr = record.get('source_address', '')
            current_addr = record.get('address', '')
            address_changed = bool(source_addr and current_addr and source_addr != current_addr)
            
            # Build result record
            result = {
                'provider_name': provider_name,
                'npi': npi,
                'address': address,
                'original_address': source_addr if address_changed else address,
                'verified_address': current_addr if address_changed else address,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'source_city': source_city,
                'source_state': source_state,
                'source_zip': source_zip,
                'specialty': specialty,
                'phone': phone,
                'email': email,
                'fax': fax,
                'confidence_score': confidence_score,
                'status': status,
                'sources': sources,
                'address_changed': address_changed,
                'discrepancies': discrepancies,
                'operational_status': record.get('operational_status', ''),
                'rank': record.get('rank', ''),
                'operating_hours': hours_info
            }
            
            parsed_data.append(result)
            
        except Exception as e:
            validation_errors.append(f"Error parsing record {idx+1}: {str(e)}")
            continue
    
    return parsed_data, validation_errors


def parse_uploaded_data(df):
    """
    Parse uploaded CSV/Excel with pre-processed verification data.
    
    The CSV should already contain verification results including:
    - Provider information (name, NPI, address, etc.)
    - Verification status
    - Confidence scores
    - Data sources
    
    Args:
        df: Pandas DataFrame from uploaded file
        
    Returns:
        tuple: (parsed_data_list, validation_errors)
    """
    validation_errors = []
    
    # Define expected columns (flexible - will use what's available)
    # Common column name variations
    column_mappings = {
        'provider_name': ['provider name', 'provider_name', 'name', 'provider', 'physician name'],
        'npi': ['npi', 'npi number', 'national provider identifier'],
        'address': ['address', 'street address', 'street', 'addr'],
        'city': ['city', 'town'],
        'state': ['state', 'st'],
        'zip_code': ['zip', 'zip code', 'zipcode', 'postal code', 'zip_code'],
        'specialty': ['specialty', 'specialization', 'medical specialty', 'practice'],
        'phone': ['phone', 'phone number', 'telephone', 'tel'],
        'email': ['email', 'e-mail', 'email address'],
        'confidence_score': ['confidence', 'confidence score', 'confidence_score', 'score', 'confidence %', 'address_confidence_score', 'address confidence score'],
        'status': ['status', 'verification status', 'verification_status', 'result'],
        'sources': ['sources', 'data sources', 'data_sources', 'source', 'references'],
        'original_address': ['original address', 'original_address', 'old address'],
        'verified_address': ['verified address', 'verified_address', 'new address', 'corrected address'],
        'discrepancies': ['discrepancies', 'issues', 'notes', 'flags']
    }
    
    # Normalize column names (lowercase for matching)
    df_lower = df.copy()
    df_lower.columns = [str(col).strip().lower() for col in df.columns]
    
    # Map columns to standard names
    column_map = {}
    for standard_name, variants in column_mappings.items():
        for col in df_lower.columns:
            if col in variants:
                column_map[col] = standard_name
                break
    
    # Check for essential columns
    essential_fields = ['provider_name', 'npi']
    found_essential = [field for field in essential_fields if field in column_map.values()]
    
    if len(found_essential) < 1:  # At least provider name or NPI
        validation_errors.append("Missing essential column: Need at least 'Provider Name' or 'NPI'")
        return [], validation_errors
    
    # Parse each row
    parsed_data = []
    
    for idx, row in df_lower.iterrows():
        try:
            # Map row data to standard fields
            record = {}
            
            for orig_col, standard_col in column_map.items():
                value = row.get(orig_col, '')
                
                # Clean and convert value
                if pd.isna(value):
                    value = ''
                else:
                    value = str(value).strip()
                
                record[standard_col] = value
            
            # Set defaults for missing fields
            record.setdefault('provider_name', record.get('npi', f'Provider {idx+1}'))
            record.setdefault('npi', '')
            record.setdefault('address', '')
            record.setdefault('city', '')
            record.setdefault('state', '')
            record.setdefault('zip_code', '')
            record.setdefault('specialty', '')
            record.setdefault('phone', '')
            record.setdefault('email', '')
            
            # Parse confidence score
            conf_str = record.get('confidence_score', '0')
            try:
                # Handle percentage format (e.g., "95%" or "95")
                conf_str = conf_str.replace('%', '').strip()
                confidence_score = float(conf_str) if conf_str else 0
                # Ensure it's in 0-100 range
                if confidence_score > 1 and confidence_score <= 100:
                    record['confidence_score'] = int(confidence_score)
                elif confidence_score <= 1:
                    record['confidence_score'] = int(confidence_score * 100)
                else:
                    record['confidence_score'] = 0
            except:
                record['confidence_score'] = 0
            
            # Parse status using new logic:
            # - Verified: phone AND address found, AND confidence >= 80%
            # - Failed: no address found
            # - Needs Review: confidence < 80% or other conditions
            has_address = bool(record.get('address', '').strip())
            has_phone = bool(record.get('phone', '').strip())
            score = record['confidence_score']
            
            status = record.get('status', '').lower()
            # Check if explicit status is provided
            if status in ['verified', 'pass', 'success', 'approved', 'valid']:
                record['status'] = 'verified'
            elif status in ['needs_review', 'review', 'pending', 'check', 'warning']:
                record['status'] = 'needs_review'
            elif status in ['failed', 'fail', 'error', 'invalid', 'rejected']:
                record['status'] = 'failed'
            else:
                # Apply new status logic if status is missing or ambiguous
                if not has_address:
                    record['status'] = 'failed'
                elif has_phone and has_address and score >= 80:
                    record['status'] = 'verified'
                else:
                    record['status'] = 'needs_review'
            
            # Parse sources (comma-separated list)
            sources_str = record.get('sources', '')
            if sources_str:
                record['sources'] = [s.strip() for s in sources_str.split(',') if s.strip()]
            else:
                record['sources'] = []
            
            # Handle address verification
            record.setdefault('original_address', record.get('address', ''))
            record.setdefault('verified_address', record.get('address', ''))
            
            # Check if address changed
            record['address_changed'] = (
                record['original_address'] != record['verified_address'] and 
                record['verified_address'] != '' and
                record['verified_address'].lower() != record['original_address'].lower()
            )
            
            # Parse discrepancies
            discrepancies_str = record.get('discrepancies', '')
            if discrepancies_str:
                record['discrepancies'] = [d.strip() for d in discrepancies_str.split(',') if d.strip()]
            else:
                record['discrepancies'] = []
            
            # Add metadata
            record['row_number'] = idx + 1
            record['parsed_at'] = datetime.now().isoformat()
            
            parsed_data.append(record)
            
        except Exception as e:
            validation_errors.append(f"Error parsing row {idx+1}: {str(e)}")
    
    return parsed_data, validation_errors


def format_results_for_display(results):
    """
    Format parsed results for dashboard display.
    Ensures consistent structure for template rendering.
    
    Args:
        results: List of result dictionaries from parsed CSV
        
    Returns:
        list: Formatted results ready for display
    """
    # Results are already in correct format from parse_uploaded_data
    # Just ensure all fields exist with defaults
    formatted = []
    
    for result in results:
        formatted_result = {
            'provider_name': result.get('provider_name', 'Unknown'),
            'npi': result.get('npi', 'N/A'),
            'original_address': result.get('original_address', ''),
            'verified_address': result.get('verified_address', result.get('address', '')),
            'source_city': result.get('source_city', result.get('city', '')),  # Source city (or fallback to model city)
            'source_state': result.get('source_state', result.get('state', '')),  # Source state (or fallback to model state)
            'source_zip': result.get('source_zip', result.get('zip_code', '')),  # Source zip (or fallback to model zip)
            'city': result.get('city', ''),  # Model response city
            'state': result.get('state', ''),  # Model response state
            'zip_code': result.get('zip_code', ''),  # Model response zip
            'specialty': result.get('specialty', ''),
            'phone': result.get('phone', ''),
            'email': result.get('email', ''),
            'fax': result.get('fax', ''),
            'confidence_score': result.get('confidence_score', 0),
            'status': result.get('status', 'pending'),
            'sources': result.get('sources', []),
            'address_changed': result.get('address_changed', False),
            'discrepancies': result.get('discrepancies', []),
            'operational_status': result.get('operational_status', ''),
            'rank': result.get('rank', ''),
            'operating_hours': result.get('operating_hours', ''),
        }
        
        formatted.append(formatted_result)
    
    return formatted


def calculate_summary_stats(results):
    """
    Calculate summary statistics for dashboard metrics.
    
    Args:
        results: List of verification results
        
    Returns:
        dict: Summary statistics
    """
    total = len(results)
    
    if total == 0:
        return {
            'total': 0,
            'verified': 0,
            'review': 0,
            'failed': 0,
            'avg_confidence': 0,
            'sources_consulted': 0
        }
    
    verified = sum(1 for r in results if r.get('status') == 'verified')
    review = sum(1 for r in results if r.get('status') == 'needs_review')
    failed = sum(1 for r in results if r.get('status') == 'failed')
    
    avg_confidence = sum(r.get('confidence_score', 0) for r in results) / total
    
    all_sources = set()
    for r in results:
        all_sources.update(r.get('sources', []))
    
    return {
        'total': total,
        'verified': verified,
        'review': review,
        'failed': failed,
        'avg_confidence': round(avg_confidence, 1),
        'sources_consulted': len(all_sources),
        'verification_rate': round((verified / total) * 100, 1) if total > 0 else 0
    }
