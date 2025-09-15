"""
Aggregation Analysis Module
Performs population-stratum aggregation analysis for mental health literature.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StratumAggregator:
    """Performs aggregation analysis by population strata."""
    
    def __init__(self, min_stratum_size: int = 3):
        """Initialize the aggregator.
        
        Args:
            min_stratum_size: Minimum number of studies required for a stratum to be included
        """
        self.min_stratum_size = min_stratum_size
    
    def analyze_by_strata(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Perform comprehensive stratum analysis."""
        logger.info(f"Analyzing {len(df)} records across strata")
        
        # Filter to strata with sufficient data
        stratum_counts = df['stratum_id'].value_counts()
        valid_strata = stratum_counts[stratum_counts >= self.min_stratum_size].index
        df_filtered = df[df['stratum_id'].isin(valid_strata)]
        
        logger.info(f"Analyzing {len(valid_strata)} strata with >= {self.min_stratum_size} studies")
        
        results = {
            'risk_factors': self._analyze_risk_factors(df_filtered),
            'symptoms': self._analyze_symptoms(df_filtered),
            'treatments': self._analyze_treatments(df_filtered),
            'outcomes': self._analyze_outcomes(df_filtered),
            'treatment_outcomes': self._analyze_treatment_outcomes(df_filtered),
            'stratum_summary': self._create_stratum_summary(df_filtered)
        }
        
        return results
    
    def _analyze_risk_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze risk factors by stratum."""
        logger.info("Analyzing risk factors by stratum")
        
        # Explode risk factors
        risk_data = []
        for _, row in df.iterrows():
            if pd.notna(row['risk_factors']) and row['risk_factors']:
                factors = [f.strip() for f in str(row['risk_factors']).split(';') if f.strip()]
                for factor in factors:
                    risk_data.append({
                        'stratum_id': row['stratum_id'],
                        'pmid': row['pmid'],
                        'risk_factor': factor
                    })
        
        if not risk_data:
            return pd.DataFrame()
        
        risk_df = pd.DataFrame(risk_data)
        
        # Calculate frequencies
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_pmids = df[df['stratum_id'] == stratum]['pmid'].nunique()
            stratum_risks = risk_df[risk_df['stratum_id'] == stratum]
            
            factor_counts = stratum_risks['risk_factor'].value_counts()
            
            for factor, count in factor_counts.items():
                result.append({
                    'stratum_id': stratum,
                    'risk_factor': factor,
                    'count': count,
                    'total_studies': stratum_pmids,
                    'percentage': (count / stratum_pmids) * 100
                })
        
        return pd.DataFrame(result)
    
    def _analyze_symptoms(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze symptoms by stratum."""
        logger.info("Analyzing symptoms by stratum")
        
        # Filter out rows without symptoms
        df_with_symptoms = df[df['symptoms'].notna() & (df['symptoms'] != '')]
        
        if df_with_symptoms.empty:
            return pd.DataFrame()
        
        # Explode symptoms
        symptom_data = []
        for _, row in df_with_symptoms.iterrows():
            symptoms = [s.strip() for s in str(row['symptoms']).split(';') if s.strip()]
            for symptom in symptoms:
                symptom_data.append({
                    'stratum_id': row['stratum_id'],
                    'pmid': row['pmid'],
                    'symptom': symptom
                })
        
        if not symptom_data:
            return pd.DataFrame()
        
        symptom_df = pd.DataFrame(symptom_data)
        
        # Calculate frequencies
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_pmids = df[df['stratum_id'] == stratum]['pmid'].nunique()
            stratum_symptoms = symptom_df[symptom_df['stratum_id'] == stratum]
            
            symptom_counts = stratum_symptoms['symptom'].value_counts()
            
            for symptom, count in symptom_counts.items():
                result.append({
                    'stratum_id': stratum,
                    'symptom': symptom,
                    'count': count,
                    'total_studies': stratum_pmids,
                    'percentage': (count / stratum_pmids) * 100
                })
        
        return pd.DataFrame(result)
    
    def _analyze_treatments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze treatments by stratum."""
        logger.info("Analyzing treatments by stratum")
        
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_data = df[df['stratum_id'] == stratum]
            stratum_pmids = stratum_data['pmid'].nunique()
            
            # Treatment categories
            treatment_cats = stratum_data['treatment_category'].value_counts()
            
            for category, count in treatment_cats.items():
                result.append({
                    'stratum_id': stratum,
                    'treatment_type': 'category',
                    'treatment': category,
                    'count': count,
                    'total_studies': stratum_pmids,
                    'percentage': (count / stratum_pmids) * 100
                })
            
            # Treatment names (if available)
            treatment_names_data = []
            for _, row in stratum_data.iterrows():
                if pd.notna(row['treatment_names']) and row['treatment_names']:
                    names = [n.strip() for n in str(row['treatment_names']).split(';') if n.strip()]
                    treatment_names_data.extend(names)
            
            if treatment_names_data:
                name_counts = Counter(treatment_names_data)
                for name, count in name_counts.items():
                    result.append({
                        'stratum_id': stratum,
                        'treatment_type': 'name',
                        'treatment': name,
                        'count': count,
                        'total_studies': stratum_pmids,
                        'percentage': (count / stratum_pmids) * 100
                    })
        
        return pd.DataFrame(result)
    
    def _analyze_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze outcomes by stratum."""
        logger.info("Analyzing outcomes by stratum")
        
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_data = df[df['stratum_id'] == stratum]
            stratum_pmids = stratum_data['pmid'].nunique()
            
            outcome_counts = stratum_data['outcome_direction'].value_counts()
            
            for direction, count in outcome_counts.items():
                result.append({
                    'stratum_id': stratum,
                    'outcome_direction': direction,
                    'count': count,
                    'total_studies': stratum_pmids,
                    'percentage': (count / stratum_pmids) * 100
                })
        
        return pd.DataFrame(result)
    
    def _analyze_treatment_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze treatment-outcome combinations by stratum."""
        logger.info("Analyzing treatment-outcome combinations")
        
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_data = df[df['stratum_id'] == stratum]
            
            # Group by treatment category and outcome direction
            combinations = stratum_data.groupby(['treatment_category', 'outcome_direction']).size().reset_index(name='count')
            
            for _, row in combinations.iterrows():
                stratum_pmids = stratum_data['pmid'].nunique()
                result.append({
                    'stratum_id': stratum,
                    'treatment_category': row['treatment_category'],
                    'outcome_direction': row['outcome_direction'],
                    'count': row['count'],
                    'total_studies': stratum_pmids,
                    'percentage': (row['count'] / stratum_pmids) * 100
                })
        
        return pd.DataFrame(result)
    
    def _create_stratum_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics for each stratum."""
        logger.info("Creating stratum summary")
        
        result = []
        for stratum in df['stratum_id'].unique():
            stratum_data = df[df['stratum_id'] == stratum]
            
            # Parse stratum components
            components = stratum.split('|') if stratum != 'general' else ['general']
            
            summary = {
                'stratum_id': stratum,
                'total_records': len(stratum_data),
                'unique_studies': stratum_data['pmid'].nunique(),
                'year_range': f"{stratum_data['year'].min():.0f}-{stratum_data['year'].max():.0f}",
                'journals_count': stratum_data['journal'].nunique(),
                'components': '; '.join(components)
            }
            
            # Most common elements
            summary['top_risk_factor'] = self._get_top_item(stratum_data, 'risk_factors')
            summary['top_treatment'] = stratum_data['treatment_category'].mode().iloc[0] if not stratum_data['treatment_category'].empty else 'unknown'
            summary['top_outcome'] = stratum_data['outcome_direction'].mode().iloc[0] if not stratum_data['outcome_direction'].empty else 'unknown'
            
            result.append(summary)
        
        return pd.DataFrame(result)
    
    def _get_top_item(self, stratum_data: pd.DataFrame, field: str) -> str:
        """Get the most common item from a multi-valued field."""
        items = []
        for _, row in stratum_data.iterrows():
            if pd.notna(row[field]) and row[field]:
                field_items = [item.strip() for item in str(row[field]).split(';') if item.strip()]
                items.extend(field_items)
        
        if items:
            return Counter(items).most_common(1)[0][0]
        return 'unknown'
    
    def save_analysis_results(self, results: Dict[str, pd.DataFrame], output_dir: str):
        """Save all analysis results to CSV files."""
        logger.info(f"Saving analysis results to {output_dir}")
        
        for name, df in results.items():
            if not df.empty:
                output_path = f"{output_dir}/{name}_by_stratum.csv"
                df.to_csv(output_path, index=False)
                logger.info(f"Saved {name} analysis to {output_path}")


def main():
    """Main function for testing aggregation analysis."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python aggregates.py <input_csv> <output_dir>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows from {input_path}")
    
    # Analyze
    aggregator = StratumAggregator()
    results = aggregator.analyze_by_strata(df)
    
    # Save results
    aggregator.save_analysis_results(results, output_dir)
    
    print("\nAnalysis Summary:")
    for name, df_result in results.items():
        print(f"  {name}: {len(df_result)} rows")


if __name__ == "__main__":
    main()