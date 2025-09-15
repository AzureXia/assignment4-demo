"""
Element-Specific Analysis with Targeted Filtering
Only includes studies that have meaningful data for each specific analysis element.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElementSpecificAggregator:
    """Analyzes each element using only studies with meaningful data for that element."""
    
    def __init__(self, min_stratum_size: int = 3):
        """Initialize aggregator."""
        self.min_stratum_size = min_stratum_size
        
        # Terms that indicate no meaningful data
        self.meaningless_terms = [
            'unspecified', 'not specified', 'unclear', 'unknown', 
            'not reported', 'nr', 'n/a', 'na', '', 'none'
        ]
        # Note: 'other' is kept as it represents a meaningful category
    
    def is_meaningless(self, value: str) -> bool:
        """Check if a value indicates no meaningful data."""
        if pd.isna(value) or value == '':
            return True
        
        value_lower = str(value).lower().strip()
        # Check for exact matches or specific patterns
        return (
            value_lower in self.meaningless_terms or
            value_lower.startswith('unspecified') or
            value_lower.startswith('not specified') or
            value_lower.startswith('unclear') or
            value_lower.startswith('unknown')
        )
    
    def analyze_all_elements(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Perform element-specific analysis."""
        logger.info("Starting element-specific analysis")
        results = {}
        
        # 1. Stratum Summary (using all data)
        results['stratum_summary_by_stratum'] = self._analyze_stratum_summary(df)
        
        # 2. Risk Factors (only studies with meaningful risk factors)
        results['risk_factors_by_stratum'] = self._analyze_risk_factors(df)
        
        # 3. Treatments (only studies with meaningful treatments)  
        results['treatments_by_stratum'] = self._analyze_treatments(df)
        
        # 4. Treatment-Outcomes (only studies with both meaningful treatment AND outcome)
        results['treatment_outcomes_by_stratum'] = self._analyze_treatment_outcomes(df)
        
        # 5. Symptoms (only studies with meaningful symptoms)
        results['symptoms_by_stratum'] = self._analyze_symptoms(df)
        
        return results
    
    def _analyze_stratum_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze overall stratum coverage."""
        summaries = []
        
        for stratum_id in df['stratum_id'].unique():
            stratum_data = df[df['stratum_id'] == stratum_id]
            unique_studies = stratum_data['pmid'].nunique()
            
            if unique_studies >= self.min_stratum_size:
                summary = {
                    'stratum_id': stratum_id,
                    'total_records': len(stratum_data),
                    'unique_studies': unique_studies,
                    'avg_year': stratum_data['year'].mean(),
                    'date_range': f"{stratum_data['year'].min()}-{stratum_data['year'].max()}"
                }
                summaries.append(summary)
        
        return pd.DataFrame(summaries).sort_values('unique_studies', ascending=False)
    
    def _analyze_risk_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze risk factors using only studies that report meaningful risk factors."""
        if 'risk_factors' not in df.columns:
            return pd.DataFrame()
        
        # Filter to only meaningful risk factor data
        meaningful_rf = df[~df['risk_factors'].apply(self.is_meaningless)]
        logger.info(f"Risk factor analysis: {len(df)} total → {len(meaningful_rf)} with meaningful risk factors")
        
        results = []
        
        for stratum_id in meaningful_rf['stratum_id'].unique():
            stratum_data = meaningful_rf[meaningful_rf['stratum_id'] == stratum_id]
            unique_studies = stratum_data['pmid'].nunique()
            
            if unique_studies >= self.min_stratum_size:
                # Count risk factors
                rf_counts = stratum_data.groupby('risk_factors')['pmid'].nunique().reset_index()
                rf_counts.columns = ['risk_factors', 'count']
                rf_counts['total_studies'] = unique_studies
                rf_counts['percentage'] = (rf_counts['count'] / unique_studies) * 100
                rf_counts['stratum_id'] = stratum_id
                
                # Only include risk factors mentioned in ≥10% of studies
                significant_rf = rf_counts[rf_counts['percentage'] >= 10.0]
                results.append(significant_rf)
        
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    
    def _analyze_treatments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze treatments using only studies that report meaningful treatments."""
        if 'treatment_category' not in df.columns:
            return pd.DataFrame()
        
        # Filter to only meaningful treatment data
        meaningful_tx = df[~df['treatment_category'].apply(self.is_meaningless)]
        logger.info(f"Treatment analysis: {len(df)} total → {len(meaningful_tx)} with meaningful treatments")
        
        results = []
        
        for stratum_id in meaningful_tx['stratum_id'].unique():
            stratum_data = meaningful_tx[meaningful_tx['stratum_id'] == stratum_id]
            unique_studies = stratum_data['pmid'].nunique()
            
            if unique_studies >= self.min_stratum_size:
                # Count treatments
                tx_counts = stratum_data.groupby('treatment_category')['pmid'].nunique().reset_index()
                tx_counts.columns = ['treatment_category', 'count']
                tx_counts['total_studies'] = unique_studies
                tx_counts['percentage'] = (tx_counts['count'] / unique_studies) * 100
                tx_counts['stratum_id'] = stratum_id
                
                # Only include treatments mentioned in ≥10% of studies
                significant_tx = tx_counts[tx_counts['percentage'] >= 10.0]
                results.append(significant_tx)
        
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    
    def _analyze_treatment_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze treatment-outcome combinations using only studies with BOTH meaningful treatment AND outcome."""
        if 'treatment_category' not in df.columns or 'outcome_direction' not in df.columns:
            return pd.DataFrame()
        
        # Filter to studies with BOTH meaningful treatment AND meaningful outcome
        meaningful_both = df[
            (~df['treatment_category'].apply(self.is_meaningless)) & 
            (~df['outcome_direction'].apply(self.is_meaningless))
        ]
        logger.info(f"Treatment-outcome analysis: {len(df)} total → {len(meaningful_both)} with both treatment & outcome")
        
        results = []
        
        for stratum_id in meaningful_both['stratum_id'].unique():
            stratum_data = meaningful_both[meaningful_both['stratum_id'] == stratum_id]
            unique_studies = stratum_data['pmid'].nunique()
            
            if unique_studies >= self.min_stratum_size:
                # Count treatment-outcome combinations
                combo_counts = stratum_data.groupby(['treatment_category', 'outcome_direction']).size().reset_index(name='count')
                combo_counts['total_studies'] = unique_studies
                combo_counts['percentage'] = (combo_counts['count'] / unique_studies) * 100
                combo_counts['stratum_id'] = stratum_id
                
                # Only include combinations mentioned in ≥5% of studies
                significant_combos = combo_counts[combo_counts['percentage'] >= 5.0]
                results.append(significant_combos)
        
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    
    def _analyze_symptoms(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze symptoms using only studies that report meaningful symptoms."""
        if 'symptoms' not in df.columns:
            return pd.DataFrame()
        
        # Filter to only meaningful symptom data
        meaningful_sx = df[~df['symptoms'].apply(self.is_meaningless)]
        logger.info(f"Symptom analysis: {len(df)} total → {len(meaningful_sx)} with meaningful symptoms")
        
        results = []
        
        for stratum_id in meaningful_sx['stratum_id'].unique():
            stratum_data = meaningful_sx[meaningful_sx['stratum_id'] == stratum_id]
            unique_studies = stratum_data['pmid'].nunique()
            
            if unique_studies >= self.min_stratum_size:
                # Count symptoms
                sx_counts = stratum_data.groupby('symptoms')['pmid'].nunique().reset_index()
                sx_counts.columns = ['symptoms', 'count']
                sx_counts['total_studies'] = unique_studies
                sx_counts['percentage'] = (sx_counts['count'] / unique_studies) * 100
                sx_counts['stratum_id'] = stratum_id
                
                # Only include symptoms mentioned in ≥10% of studies
                significant_sx = sx_counts[sx_counts['percentage'] >= 10.0]
                results.append(significant_sx)
        
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()
    
    def save_results(self, results: Dict[str, pd.DataFrame], output_dir: str):
        """Save analysis results."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in results.items():
            if not df.empty:
                output_path = f"{output_dir}/{name}.csv"
                df.to_csv(output_path, index=False)
                logger.info(f"Saved {name} with {len(df)} rows to {output_path}")
            else:
                logger.warning(f"Skipping empty result: {name}")
    
    def generate_filtering_report(self, df: pd.DataFrame) -> Dict[str, any]:
        """Generate report on filtering effectiveness."""
        report = {
            'original_total_records': len(df),
            'element_analysis': []
        }
        
        # Risk factors
        if 'risk_factors' in df.columns:
            meaningful_rf = df[~df['risk_factors'].apply(self.is_meaningless)]
            report['element_analysis'].append({
                'element': 'risk_factors',
                'total_records': len(df),
                'meaningful_records': len(meaningful_rf),
                'retention_rate': (len(meaningful_rf) / len(df)) * 100,
                'excluded_records': len(df) - len(meaningful_rf)
            })
        
        # Treatments  
        if 'treatment_category' in df.columns:
            meaningful_tx = df[~df['treatment_category'].apply(self.is_meaningless)]
            report['element_analysis'].append({
                'element': 'treatment_category',
                'total_records': len(df),
                'meaningful_records': len(meaningful_tx),
                'retention_rate': (len(meaningful_tx) / len(df)) * 100,
                'excluded_records': len(df) - len(meaningful_tx)
            })
        
        # Treatment-Outcome combinations
        if 'treatment_category' in df.columns and 'outcome_direction' in df.columns:
            meaningful_both = df[
                (~df['treatment_category'].apply(self.is_meaningless)) & 
                (~df['outcome_direction'].apply(self.is_meaningless))
            ]
            report['element_analysis'].append({
                'element': 'treatment_outcome_combinations',
                'total_records': len(df),
                'meaningful_records': len(meaningful_both),
                'retention_rate': (len(meaningful_both) / len(df)) * 100,
                'excluded_records': len(df) - len(meaningful_both)
            })
        
        return report


def main():
    """Run element-specific analysis."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python element_specific_aggregates.py <normalized_csv> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_file)
    
    # Run analysis
    aggregator = ElementSpecificAggregator(min_stratum_size=3)
    results = aggregator.analyze_all_elements(df)
    
    # Save results
    aggregator.save_results(results, output_dir)
    
    # Generate report
    report = aggregator.generate_filtering_report(df)
    
    print("\n" + "="*80)
    print("🎯 ELEMENT-SPECIFIC ANALYSIS REPORT")
    print("="*80)
    print(f"Total records in dataset: {report['original_total_records']}")
    print("\nElement-specific filtering results:")
    
    for analysis in report['element_analysis']:
        print(f"\n📊 {analysis['element'].upper()}:")
        print(f"   • Meaningful records: {analysis['meaningful_records']:,}")
        print(f"   • Retention rate: {analysis['retention_rate']:.1f}%")
        print(f"   • Excluded records: {analysis['excluded_records']:,}")
    
    print(f"\n✅ Generated {len([r for r in results.values() if not r.empty])} analysis tables")


if __name__ == "__main__":
    main()