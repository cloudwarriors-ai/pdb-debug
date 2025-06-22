#!/usr/bin/env python3
"""
Breakpoint Simulation Application - Data Processing Pipeline
This application simulates a multi-stage data processing pipeline
with function calls passing parameters for PDB Gateway testing.
"""

import time
import json
from typing import List, Dict, Any


def load_raw_data(source_name: str, record_count: int = 10) -> List[Dict[str, Any]]:
    """
    Load raw data from a simulated source.
    
    Args:
        source_name: Name of the data source
        record_count: Number of records to generate
    
    Returns:
        List of raw data records
    """
    print(f"📥 Loading raw data from source: {source_name}")
    
    # Simulate data loading with various data types
    raw_data = []
    for i in range(record_count):
        record = {
            "id": i + 1,
            "name": f"Record_{i+1}",
            "value": (i + 1) * 10.5,
            "category": "A" if i % 2 == 0 else "B",
            "metadata": {
                "created_at": f"2024-01-{(i % 30) + 1:02d}",
                "priority": i % 3 + 1,
                "tags": [f"tag_{j}" for j in range(i % 3 + 1)]
            },
            "active": i % 4 != 0,
            "nested_data": {
                "level_1": {
                    "level_2": {
                        "deep_value": f"deep_{i}"
                    }
                }
            }
        }
        raw_data.append(record)
    
    print(f"✅ Loaded {len(raw_data)} records from {source_name}")
    return raw_data


def validate_data(raw_data: List[Dict[str, Any]], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate raw data against business rules.
    
    Args:
        raw_data: List of raw data records
        validation_rules: Dictionary of validation criteria
    
    Returns:
        Validation results with valid/invalid records
    """
    print(f"🔍 Validating {len(raw_data)} records against rules...")
    
    valid_records = []
    invalid_records = []
    validation_errors = []
    
    for record in raw_data:
        is_valid = True
        record_errors = []
        
        # Check required fields
        for required_field in validation_rules.get("required_fields", []):
            if required_field not in record or record[required_field] is None:
                is_valid = False
                record_errors.append(f"Missing required field: {required_field}")
        
        # Check value ranges
        if "value_min" in validation_rules and record.get("value", 0) < validation_rules["value_min"]:
            is_valid = False
            record_errors.append(f"Value {record.get('value')} below minimum {validation_rules['value_min']}")
        
        if "value_max" in validation_rules and record.get("value", 0) > validation_rules["value_max"]:
            is_valid = False
            record_errors.append(f"Value {record.get('value')} above maximum {validation_rules['value_max']}")
        
        # Check category values
        if "valid_categories" in validation_rules:
            if record.get("category") not in validation_rules["valid_categories"]:
                is_valid = False
                record_errors.append(f"Invalid category: {record.get('category')}")
        
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append(record)
            validation_errors.extend(record_errors)
    
    validation_result = {
        "total_records": len(raw_data),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "errors": validation_errors,
        "validation_rules": validation_rules
    }
    
    print(f"✅ Validation complete: {len(valid_records)} valid, {len(invalid_records)} invalid")
    return validation_result


def transform_data(validation_result: Dict[str, Any], transformation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform valid data according to transformation rules.
    
    Args:
        validation_result: Result from data validation
        transformation_config: Transformation configuration
    
    Returns:
        List of transformed records
    """
    print(f"🔄 Transforming {validation_result['valid_count']} valid records...")
    
    valid_records = validation_result["valid_records"]
    transformed_records = []
    
    for record in valid_records:
        transformed_record = {}
        
        # Apply field mappings
        field_mappings = transformation_config.get("field_mappings", {})
        for source_field, target_field in field_mappings.items():
            if source_field in record:
                transformed_record[target_field] = record[source_field]
        
        # Apply value transformations
        if "value_multiplier" in transformation_config:
            if "value" in record:
                transformed_record["transformed_value"] = record["value"] * transformation_config["value_multiplier"]
        
        # Create computed fields
        if transformation_config.get("add_computed_fields", False):
            transformed_record["computed_score"] = (
                record.get("value", 0) * record.get("metadata", {}).get("priority", 1)
            )
            transformed_record["record_hash"] = hash(json.dumps(record, sort_keys=True))
            transformed_record["category_numeric"] = 1 if record.get("category") == "A" else 2
        
        # Extract nested data
        if transformation_config.get("flatten_nested", False):
            if "nested_data" in record:
                deep_value = record["nested_data"]["level_1"]["level_2"]["deep_value"]
                transformed_record["flattened_deep_value"] = deep_value
        
        # Add transformation metadata
        transformed_record["transformation_timestamp"] = time.time()
        transformed_record["original_id"] = record.get("id")
        
        transformed_records.append(transformed_record)
    
    print(f"✅ Transformation complete: {len(transformed_records)} records transformed")
    return transformed_records


def aggregate_data(transformed_records: List[Dict[str, Any]], aggregation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate transformed data for reporting.
    
    Args:
        transformed_records: List of transformed records
        aggregation_config: Aggregation configuration
    
    Returns:
        Aggregated data summary
    """
    print(f"📊 Aggregating {len(transformed_records)} transformed records...")
    
    # Initialize aggregation results
    aggregation_result = {
        "total_records": len(transformed_records),
        "aggregations": {},
        "config": aggregation_config
    }
    
    # Sum aggregations
    if "sum_fields" in aggregation_config:
        for field in aggregation_config["sum_fields"]:
            total = sum(record.get(field, 0) for record in transformed_records)
            aggregation_result["aggregations"][f"{field}_total"] = total
    
    # Average aggregations
    if "avg_fields" in aggregation_config:
        for field in aggregation_config["avg_fields"]:
            values = [record.get(field, 0) for record in transformed_records if field in record]
            average = sum(values) / len(values) if values else 0
            aggregation_result["aggregations"][f"{field}_average"] = average
    
    # Count aggregations
    if "count_by_field" in aggregation_config:
        for field in aggregation_config["count_by_field"]:
            counts = {}
            for record in transformed_records:
                value = record.get(field, "unknown")
                counts[value] = counts.get(value, 0) + 1
            aggregation_result["aggregations"][f"{field}_counts"] = counts
    
    # Min/Max aggregations
    if "minmax_fields" in aggregation_config:
        for field in aggregation_config["minmax_fields"]:
            values = [record.get(field, 0) for record in transformed_records if field in record]
            if values:
                aggregation_result["aggregations"][f"{field}_min"] = min(values)
                aggregation_result["aggregations"][f"{field}_max"] = max(values)
    
    print(f"✅ Aggregation complete: {len(aggregation_result['aggregations'])} metrics calculated")
    return aggregation_result


def generate_report(aggregation_result: Dict[str, Any], report_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final report from aggregated data.
    
    Args:
        aggregation_result: Aggregated data
        report_config: Report generation configuration
    
    Returns:
        Final report data
    """
    print(f"📄 Generating report from {aggregation_result['total_records']} records...")
    
    report = {
        "report_metadata": {
            "generated_at": time.time(),
            "report_type": report_config.get("report_type", "summary"),
            "total_records_processed": aggregation_result["total_records"]
        },
        "summary_statistics": aggregation_result["aggregations"],
        "configuration": {
            "aggregation_config": aggregation_result["config"],
            "report_config": report_config
        }
    }
    
    # Add report-specific sections
    if report_config.get("include_recommendations", False):
        recommendations = []
        
        # Generate recommendations based on data
        if "transformed_value_total" in aggregation_result["aggregations"]:
            total_value = aggregation_result["aggregations"]["transformed_value_total"]
            if total_value > 1000:
                recommendations.append("High value detected - consider premium processing")
            elif total_value < 100:
                recommendations.append("Low value detected - review data quality")
        
        report["recommendations"] = recommendations
    
    if report_config.get("include_quality_metrics", False):
        quality_metrics = {
            "data_completeness": 0.95,  # Simulated
            "data_accuracy": 0.98,      # Simulated
            "processing_efficiency": aggregation_result["total_records"] / max(1, len(aggregation_result["aggregations"]))
        }
        report["quality_metrics"] = quality_metrics
    
    print(f"✅ Report generated successfully")
    return report


def run_data_pipeline(source_name: str = "test_source", record_count: int = 15) -> Dict[str, Any]:
    """
    Main pipeline function that orchestrates the entire data processing workflow.
    
    Args:
        source_name: Name of the data source
        record_count: Number of records to process
    
    Returns:
        Final pipeline result
    """
    print("🚀 Starting Data Processing Pipeline")
    print("=" * 50)
    
    pipeline_start_time = time.time()
    
    # Stage 1: Load raw data
    print("\n🔸 Stage 1: Data Loading")
    raw_data = load_raw_data(source_name, record_count)
    
    # Stage 2: Validate data
    print("\n🔸 Stage 2: Data Validation")
    validation_rules = {
        "required_fields": ["id", "name", "value"],
        "value_min": 5.0,
        "value_max": 200.0,
        "valid_categories": ["A", "B"]
    }
    validation_result = validate_data(raw_data, validation_rules)
    
    # Stage 3: Transform data
    print("\n🔸 Stage 3: Data Transformation")
    transformation_config = {
        "field_mappings": {
            "id": "record_id",
            "name": "record_name",
            "category": "record_category"
        },
        "value_multiplier": 2.5,
        "add_computed_fields": True,
        "flatten_nested": True
    }
    transformed_data = transform_data(validation_result, transformation_config)
    
    # Stage 4: Aggregate data
    print("\n🔸 Stage 4: Data Aggregation")
    aggregation_config = {
        "sum_fields": ["transformed_value", "computed_score"],
        "avg_fields": ["transformed_value", "computed_score"],
        "count_by_field": ["record_category"],
        "minmax_fields": ["transformed_value"]
    }
    aggregation_result = aggregate_data(transformed_data, aggregation_config)
    
    # Stage 5: Generate report
    print("\n🔸 Stage 5: Report Generation")
    report_config = {
        "report_type": "detailed_summary",
        "include_recommendations": True,
        "include_quality_metrics": True
    }
    final_report = generate_report(aggregation_result, report_config)
    
    # Pipeline completion
    pipeline_end_time = time.time()
    processing_time = pipeline_end_time - pipeline_start_time
    
    pipeline_result = {
        "status": "success",
        "processing_time": processing_time,
        "records_processed": record_count,
        "final_report": final_report,
        "pipeline_metadata": {
            "source_name": source_name,
            "stages_completed": 5,
            "start_time": pipeline_start_time,
            "end_time": pipeline_end_time
        }
    }
    
    print("\n" + "=" * 50)
    print(f"✅ Pipeline completed successfully in {processing_time:.2f} seconds")
    print(f"📊 Processed {record_count} records")
    
    return pipeline_result


if __name__ == "__main__":
    # Run the pipeline with default parameters
    result = run_data_pipeline("production_source", 20)
    
    print(f"\n🎉 Final Result Summary:")
    print(f"   Status: {result['status']}")
    print(f"   Processing Time: {result['processing_time']:.2f}s")
    print(f"   Records Processed: {result['records_processed']}")
    print(f"   Report Type: {result['final_report']['report_metadata']['report_type']}")