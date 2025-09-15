"""
Improved Statistical Aggregation with Quality Filtering
Enhanced version that filters out "unspecified" entries for better analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedStratumAggregator:
    """Enhanced stratum aggregator with quality filtering."""
    
    def __init__(self, min_stratum_size: int = 3, filter_unspecified: bool = True):
        """Initialize aggregator with quality settings."""
        self.min_stratum_size = min_stratum_size
        self.filter_unspecified = filter_unspecified
        
        # Terms to filter out for better quality
        self.unspecified_terms = [
            'unspecified', 'not specified', 'unclear', 'unknown', 'other', 
            'various', 'mixed', 'general', 'broad', 'diverse', 'multiple',
            'not reported', 'nr', 'n/a', 'na', 'none specified'
        ]
    
    def is_unspecified(self, value: str) -> bool:
        """Check if a value should be filtered as unspecified."""
        if pd.isna(value) or value == '' or value.lower().strip() == '':
            return True
        
        value_lower = str(value).lower().strip()
        return any(term in value_lower for term in self.unspecified_terms)
    
    def filter_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out low-quality unspecified entries."""
        if not self.filter_unspecified:
            return df
        
        logger.info(f"Filtering data quality - original rows: {len(df)}")
        
        # Create quality-filtered dataset
        quality_df = df.copy()
        
        # Filter each important column
        for col in ['risk_factor', 'treatment_category', 'outcome_direction', 'symptom']:
            if col in quality_df.columns:
                before_count = len(quality_df)
                quality_df = quality_df[~quality_df[col].apply(self.is_unspecified)]
                after_count = len(quality_df)
                logger.info(f"Filtered {col}: {before_count} → {after_count} rows ({before_count-after_count} removed)")
        
        logger.info(f"Quality filtering complete - final rows: {len(quality_df)}")
        return quality_df
    
    def analyze_by_strata_improved(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Enhanced stratum analysis with quality filtering."""
        logger.info("Starting improved stratum analysis with quality filtering")
        
        # Filter for quality
        quality_df = self.filter_quality_data(df)
        
        # Group by stratum
        stratum_groups = quality_df.groupby('stratum_id')
        
        # Filter strata by minimum size
        valid_strata = []
        for name, group in stratum_groups:
            if len(group['pmid'].unique()) >= self.min_stratum_size:
                valid_strata.append((name, group))
        
        logger.info(f"Found {len(valid_strata)} valid strata (≥{self.min_stratum_size} studies each)")
        
        results = {}
        
        # 1. Stratum summary
        stratum_summaries = []
        for stratum_name, stratum_data in valid_strata:
            summary = {
                'stratum_id': stratum_name,
                'total_records': len(stratum_data),
                'unique_studies': stratum_data['pmid'].nunique(),
                'avg_year': stratum_data['year'].mean(),
                'date_range': f"{stratum_data['year'].min()}-{stratum_data['year'].max()}"
            }
            stratum_summaries.append(summary)
        
        results['stratum_summary_by_stratum'] = pd.DataFrame(stratum_summaries).sort_values('unique_studies', ascending=False)
        
        # 2. Risk factors analysis (quality filtered)
        risk_factor_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'risk_factor' in stratum_data.columns:
                total_studies = stratum_data['pmid'].nunique()
                risk_counts = stratum_data.groupby('risk_factor')['pmid'].nunique().reset_index()
                risk_counts.columns = ['risk_factor', 'study_count']
                risk_counts['percentage'] = (risk_counts['study_count'] / total_studies) * 100
                risk_counts['stratum_id'] = stratum_name
                risk_counts['total_studies'] = total_studies
                
                # Only include meaningful risk factors (>5% prevalence)
                significant_risks = risk_counts[risk_counts['percentage'] >= 5.0]
                risk_factor_results.append(significant_risks)
        
        if risk_factor_results:
            results['risk_factors_by_stratum'] = pd.concat(risk_factor_results, ignore_index=True)
        
        # 3. Treatment analysis (quality filtered)
        treatment_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'treatment_category' in stratum_data.columns:
                total_studies = stratum_data['pmid'].nunique()
                treatment_counts = stratum_data.groupby('treatment_category')['pmid'].nunique().reset_index()
                treatment_counts.columns = ['treatment_category', 'study_count']
                treatment_counts['percentage'] = (treatment_counts['study_count'] / total_studies) * 100
                treatment_counts['stratum_id'] = stratum_name
                treatment_counts['total_studies'] = total_studies
                
                # Only include treatments with meaningful prevalence
                significant_treatments = treatment_counts[treatment_counts['percentage'] >= 5.0]
                treatment_results.append(significant_treatments)
        
        if treatment_results:
            results['treatments_by_stratum'] = pd.concat(treatment_results, ignore_index=True)
        
        # 4. Treatment-Outcome combinations (quality filtered)
        outcome_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'treatment_category' in stratum_data.columns and 'outcome_direction' in stratum_data.columns:
                # Create treatment-outcome pairs
                pairs = stratum_data.groupby(['treatment_category', 'outcome_direction']).size().reset_index(name='count')
                pairs['stratum_id'] = stratum_name
                pairs['total_studies'] = stratum_data['pmid'].nunique()
                pairs['percentage'] = (pairs['count'] / pairs['total_studies']) * 100
                
                # Only include meaningful combinations
                significant_pairs = pairs[pairs['percentage'] >= 5.0]
                outcome_results.append(significant_pairs)
        
        if outcome_results:
            results['treatment_outcomes_by_stratum'] = pd.concat(outcome_results, ignore_index=True)
        
        # 5. Symptoms analysis (quality filtered)
        symptom_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'symptom' in stratum_data.columns:
                # Filter out rows where symptom is unspecified
                symptom_data = stratum_data[~stratum_data['symptom'].apply(self.is_unspecified)]
                
                if len(symptom_data) > 0:
                    total_studies = symptom_data['pmid'].nunique()
                    symptom_counts = symptom_data.groupby('symptom')['pmid'].nunique().reset_index()
                    symptom_counts.columns = ['symptom', 'study_count']
                    symptom_counts['percentage'] = (symptom_counts['study_count'] / total_studies) * 100
                    symptom_counts['stratum_id'] = stratum_name
                    symptom_counts['total_studies'] = total_studies
                    
                    # Only include symptoms with meaningful prevalence
                    significant_symptoms = symptom_counts[symptom_counts['percentage'] >= 10.0]
                    if len(significant_symptoms) > 0:
                        symptom_results.append(significant_symptoms)
        
        if symptom_results:
            results['symptoms_by_stratum'] = pd.concat(symptom_results, ignore_index=True)
        
        logger.info(f"Analysis complete. Generated {len(results)} result tables.")
        return results
    
    def save_analysis_results(self, results: Dict[str, pd.DataFrame], output_dir: str):
        """Save analysis results to CSV files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in results.items():
            output_path = f"{output_dir}/{name}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {name} with {len(df)} rows to {output_path}")
    
    def generate_quality_report(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame) -> Dict[str, any]:
        """Generate data quality improvement report."""
        report = {
            'original_records': len(original_df),
            'filtered_records': len(filtered_df),
            'quality_improvement': len(original_df) - len(filtered_df),
            'retention_rate': (len(filtered_df) / len(original_df)) * 100,
            'improvements': []
        }
        
        # Analyze specific improvements
        for col in ['risk_factor', 'treatment_category', 'outcome_direction', 'symptom']:
            if col in original_df.columns:
                original_unspecified = original_df[col].apply(self.is_unspecified).sum()
                filtered_unspecified = filtered_df[col].apply(self.is_unspecified).sum() if col in filtered_df.columns else 0
                
                report['improvements'].append({
                    'field': col,
                    'original_unspecified': original_unspecified,
                    'filtered_unspecified': filtered_unspecified,
                    'improvement': original_unspecified - filtered_unspecified
                })
        
        return report


def main():
    """Test improved aggregation."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python improved_aggregates.py <normalized_csv> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_file)
    
    # Analyze with improvements
    aggregator = ImprovedStratumAggregator(min_stratum_size=3, filter_unspecified=True)
    results = aggregator.analyze_by_strata_improved(df)
    
    # Save results
    aggregator.save_analysis_results(results, output_dir)
    
    # Generate quality report
    original_df = pd.read_csv(input_file)
    filtered_df = aggregator.filter_quality_data(original_df)
    quality_report = aggregator.generate_quality_report(original_df, filtered_df)
    
    print("\n" + "="*60)
    print("🔍 DATA QUALITY IMPROVEMENT REPORT")
    print("="*60)
    print(f"Original records: {quality_report['original_records']}")
    print(f"Quality-filtered records: {quality_report['filtered_records']}")
    print(f"Records removed: {quality_report['quality_improvement']}")
    print(f"Data retention rate: {quality_report['retention_rate']:.1f}%")
    
    print("\nField-specific improvements:")
    for improvement in quality_report['improvements']:
        print(f"  • {improvement['field']}: removed {improvement['improvement']} unspecified entries")


if __name__ == "__main__":
    main()