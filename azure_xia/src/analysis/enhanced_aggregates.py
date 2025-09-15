"""
Enhanced Statistical Aggregation with Clear Categories
Includes symptoms and risk factors per stratum with cleaned labels.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedStratumAggregator:
    """Enhanced stratum aggregator with clear categorization."""
    
    def __init__(self, min_stratum_size: int = 3):
        """Initialize aggregator."""
        self.min_stratum_size = min_stratum_size
        
        # Risk factor categorization mapping
        self.risk_factor_categories = {
            'depression': ['depression', 'depressive', 'depressed', 'major depression', 'mdd'],
            'anxiety': ['anxiety', 'anxious', 'panic', 'worry', 'gad', 'generalized anxiety'],
            'trauma': ['trauma', 'ptsd', 'post-traumatic', 'abuse', 'violence', 'combat'],
            'substance_use': ['substance', 'alcohol', 'drug', 'addiction', 'dependence', 'abuse'],
            'chronic_illness': ['diabetes', 'cancer', 'cardiovascular', 'chronic pain', 'heart disease'],
            'social_factors': ['isolation', 'loneliness', 'social support', 'poverty', 'unemployment'],
            'cognitive_factors': ['cognition', 'memory', 'attention', 'executive', 'cognitive'],
            'behavioral_factors': ['sleep', 'eating', 'exercise', 'lifestyle', 'diet', 'physical activity'],
            'developmental': ['childhood', 'adolescent', 'developmental', 'early life', 'parental'],
            'other': []  # catch-all
        }
        
        # Symptom categorization mapping  
        self.symptom_categories = {
            'mood_symptoms': ['sad', 'hopeless', 'empty', 'irritable', 'mood', 'emotional'],
            'anxiety_symptoms': ['worry', 'fear', 'nervous', 'panic', 'restless', 'tension'],
            'cognitive_symptoms': ['concentration', 'memory', 'decision', 'thinking', 'attention', 'focus'],
            'physical_symptoms': ['fatigue', 'sleep', 'appetite', 'weight', 'energy', 'pain', 'headache'],
            'behavioral_symptoms': ['withdrawal', 'isolation', 'avoidance', 'aggression', 'self-harm'],
            'psychotic_symptoms': ['hallucination', 'delusion', 'psychosis', 'paranoid', 'bizarre'],
            'other': []  # catch-all
        }
    
    def categorize_text(self, text: str, category_mapping: Dict) -> str:
        """Categorize text into predefined categories."""
        if pd.isna(text) or text == '' or str(text).lower().strip() == '':
            return 'unspecified'
        
        text_lower = str(text).lower().strip()
        
        # Remove common prefixes/suffixes and clean
        text_clean = re.sub(r'^(the |a |an )', '', text_lower)
        text_clean = re.sub(r'[^\w\s]', ' ', text_clean)
        text_clean = ' '.join(text_clean.split())  # normalize whitespace
        
        # Skip overly long or generic entries
        if len(text_clean) > 100 or text_clean in ['other', 'various', 'multiple', 'mixed', 'general']:
            return 'other'
        
        # Match against categories
        for category, keywords in category_mapping.items():
            if category == 'other':
                continue
            for keyword in keywords:
                if keyword in text_clean:
                    return category
        
        # If no match and reasonably specific, create a cleaned version
        if len(text_clean) > 5 and len(text_clean) < 50:
            return text_clean[:30]  # truncate for display
        
        return 'other'
    
    def analyze_enhanced_strata(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Enhanced stratum analysis with symptoms and risk factors."""
        logger.info("Starting enhanced stratum analysis with clear categorization")
        
        # Group by stratum
        stratum_groups = df.groupby('stratum_id')
        
        # Filter strata by minimum size
        valid_strata = []
        for name, group in stratum_groups:
            if len(group['pmid'].unique()) >= self.min_stratum_size:
                valid_strata.append((name, group))
        
        logger.info(f"Found {len(valid_strata)} valid strata (≥{self.min_stratum_size} studies each)")
        
        results = {}
        
        # 1. Enhanced Stratum Summary
        stratum_summaries = []
        for stratum_name, stratum_data in valid_strata:
            summary = {
                'stratum_id': stratum_name,
                'total_records': len(stratum_data),
                'unique_studies': stratum_data['pmid'].nunique(),
                'unique_papers': stratum_data['pmid'].nunique(),  # Same as unique_studies for clarity
                'avg_year': round(stratum_data['year'].mean(), 1),
                'year_range': f"{stratum_data['year'].min()}-{stratum_data['year'].max()}"
            }
            stratum_summaries.append(summary)
        
        results['stratum_summary_by_stratum'] = pd.DataFrame(stratum_summaries).sort_values('unique_studies', ascending=False)
        
        # 2. Enhanced Risk Factors Analysis
        risk_factor_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'risk_factor' in stratum_data.columns:
                # Categorize risk factors
                stratum_data_copy = stratum_data.copy()
                stratum_data_copy['risk_category'] = stratum_data_copy['risk_factor'].apply(
                    lambda x: self.categorize_text(x, self.risk_factor_categories)
                )
                
                # Filter out unspecified
                meaningful_risks = stratum_data_copy[stratum_data_copy['risk_category'] != 'unspecified']
                
                if len(meaningful_risks) > 0:
                    total_studies = meaningful_risks['pmid'].nunique()
                    risk_counts = meaningful_risks.groupby('risk_category')['pmid'].nunique().reset_index()
                    risk_counts.columns = ['risk_factor', 'study_count']
                    risk_counts['percentage'] = (risk_counts['study_count'] / total_studies) * 100
                    risk_counts['stratum_id'] = stratum_name
                    risk_counts['total_studies'] = total_studies
                    
                    # Only include significant risk factors
                    significant_risks = risk_counts[risk_counts['percentage'] >= 10.0]
                    risk_factor_results.append(significant_risks)
        
        if risk_factor_results:
            results['risk_factors_by_stratum'] = pd.concat(risk_factor_results, ignore_index=True)
        
        # 3. Enhanced Symptoms Analysis
        symptom_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'symptom' in stratum_data.columns:
                # Categorize symptoms
                stratum_data_copy = stratum_data.copy()
                stratum_data_copy['symptom_category'] = stratum_data_copy['symptom'].apply(
                    lambda x: self.categorize_text(x, self.symptom_categories)
                )
                
                # Filter out unspecified
                meaningful_symptoms = stratum_data_copy[stratum_data_copy['symptom_category'] != 'unspecified']
                
                if len(meaningful_symptoms) > 0:
                    total_studies = meaningful_symptoms['pmid'].nunique()
                    symptom_counts = meaningful_symptoms.groupby('symptom_category')['pmid'].nunique().reset_index()
                    symptom_counts.columns = ['symptom', 'study_count']
                    symptom_counts['percentage'] = (symptom_counts['study_count'] / total_studies) * 100
                    symptom_counts['stratum_id'] = stratum_name
                    symptom_counts['total_studies'] = total_studies
                    
                    # Only include significant symptoms
                    significant_symptoms = symptom_counts[symptom_counts['percentage'] >= 15.0]
                    symptom_results.append(significant_symptoms)
        
        if symptom_results:
            results['symptoms_by_stratum'] = pd.concat(symptom_results, ignore_index=True)
        
        # 4. Enhanced Treatment Analysis
        treatment_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'treatment_category' in stratum_data.columns:
                # Clean treatment categories
                stratum_data_copy = stratum_data.copy()
                stratum_data_copy['clean_treatment'] = stratum_data_copy['treatment_category'].apply(
                    lambda x: self.clean_treatment_name(x)
                )
                
                # Filter out unspecified
                meaningful_treatments = stratum_data_copy[stratum_data_copy['clean_treatment'] != 'unspecified']
                
                if len(meaningful_treatments) > 0:
                    total_studies = meaningful_treatments['pmid'].nunique()
                    treatment_counts = meaningful_treatments.groupby('clean_treatment')['pmid'].nunique().reset_index()
                    treatment_counts.columns = ['treatment_category', 'study_count']
                    treatment_counts['percentage'] = (treatment_counts['study_count'] / total_studies) * 100
                    treatment_counts['stratum_id'] = stratum_name
                    treatment_counts['total_studies'] = total_studies
                    
                    # Only include significant treatments
                    significant_treatments = treatment_counts[treatment_counts['percentage'] >= 10.0]
                    treatment_results.append(significant_treatments)
        
        if treatment_results:
            results['treatments_by_stratum'] = pd.concat(treatment_results, ignore_index=True)
        
        # 5. Treatment-Outcome Analysis (enhanced)
        outcome_results = []
        for stratum_name, stratum_data in valid_strata:
            if 'treatment_category' in stratum_data.columns and 'outcome_direction' in stratum_data.columns:
                # Clean both columns
                stratum_data_copy = stratum_data.copy()
                stratum_data_copy['clean_treatment'] = stratum_data_copy['treatment_category'].apply(self.clean_treatment_name)
                stratum_data_copy['clean_outcome'] = stratum_data_copy['outcome_direction'].apply(self.clean_outcome_name)
                
                # Filter meaningful combinations
                meaningful_data = stratum_data_copy[
                    (stratum_data_copy['clean_treatment'] != 'unspecified') &
                    (stratum_data_copy['clean_outcome'] != 'unspecified')
                ]
                
                if len(meaningful_data) > 0:
                    pairs = meaningful_data.groupby(['clean_treatment', 'clean_outcome']).size().reset_index(name='count')
                    pairs['stratum_id'] = stratum_name
                    pairs['total_studies'] = meaningful_data['pmid'].nunique()
                    pairs['percentage'] = (pairs['count'] / pairs['total_studies']) * 100
                    pairs = pairs.rename(columns={'clean_treatment': 'treatment_category', 'clean_outcome': 'outcome_direction'})
                    
                    # Only meaningful combinations
                    significant_pairs = pairs[pairs['percentage'] >= 15.0]
                    outcome_results.append(significant_pairs)
        
        if outcome_results:
            results['treatment_outcomes_by_stratum'] = pd.concat(outcome_results, ignore_index=True)
        
        logger.info(f"Enhanced analysis complete. Generated {len(results)} result tables.")
        return results
    
    def clean_treatment_name(self, text: str) -> str:
        """Clean treatment names for better display."""
        if pd.isna(text) or text == '':
            return 'unspecified'
        
        text_clean = str(text).lower().strip()
        
        # Map common treatments to standard names
        treatment_mapping = {
            'cognitive behavioral therapy': 'CBT',
            'cbt': 'CBT',
            'acceptance and commitment therapy': 'ACT',
            'act': 'ACT',
            'dialectical behavior therapy': 'DBT',
            'dbt': 'DBT',
            'mindfulness': 'Mindfulness-Based',
            'meditation': 'Mindfulness-Based',
            'psychotherapy': 'Psychotherapy',
            'therapy': 'Psychotherapy',
            'counseling': 'Counseling',
            'medication': 'Pharmacotherapy',
            'antidepressant': 'Pharmacotherapy',
            'exercise': 'Exercise Therapy',
            'physical activity': 'Exercise Therapy',
            'group therapy': 'Group Therapy',
            'individual therapy': 'Individual Therapy'
        }
        
        for key, value in treatment_mapping.items():
            if key in text_clean:
                return value
        
        # If no mapping and not too long/generic
        if len(text_clean) > 3 and len(text_clean) < 30 and text_clean not in ['other', 'various', 'mixed']:
            return text_clean.title()
        
        return 'Other'
    
    def clean_outcome_name(self, text: str) -> str:
        """Clean outcome names for better display."""
        if pd.isna(text) or text == '':
            return 'unspecified'
        
        text_clean = str(text).lower().strip()
        
        # Map common outcomes to standard names
        outcome_mapping = {
            'improvement': 'Improved',
            'improved': 'Improved',
            'better': 'Improved',
            'positive': 'Improved',
            'effective': 'Improved',
            'reduced': 'Reduced Symptoms',
            'decrease': 'Reduced Symptoms',
            'lower': 'Reduced Symptoms',
            'no change': 'No Change',
            'unchanged': 'No Change',
            'mixed': 'Mixed Results',
            'variable': 'Mixed Results'
        }
        
        for key, value in outcome_mapping.items():
            if key in text_clean:
                return value
        
        # If no mapping and reasonable length
        if len(text_clean) > 3 and len(text_clean) < 25:
            return text_clean.title()
        
        return 'Other'
    
    def save_analysis_results(self, results: Dict[str, pd.DataFrame], output_dir: str):
        """Save analysis results to CSV files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in results.items():
            output_path = f"{output_dir}/{name}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {name} with {len(df)} rows to {output_path}")


def main():
    """Test enhanced aggregation."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python enhanced_aggregates.py <normalized_csv> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_file)
    
    # Analyze with enhancements
    aggregator = EnhancedStratumAggregator(min_stratum_size=3)
    results = aggregator.analyze_enhanced_strata(df)
    
    # Save results
    aggregator.save_analysis_results(results, output_dir)
    
    print("\n" + "="*60)
    print("✨ ENHANCED ANALYSIS COMPLETE")
    print("="*60)
    print(f"Generated {len(results)} analysis tables with:")
    print("• Clear risk factor categories")
    print("• Clean symptom classifications") 
    print("• Standardized treatment names")
    print("• Meaningful outcome labels")
    
    for name, df in results.items():
        print(f"  📊 {name}: {len(df)} rows")


if __name__ == "__main__":
    main()