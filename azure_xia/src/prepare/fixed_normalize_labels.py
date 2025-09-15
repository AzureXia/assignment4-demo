"""
Fixed Population Normalization - Mutually Exclusive Categories
Creates hierarchical, non-overlapping population strata.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Set
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FixedFieldNormalizer:
    """Creates mutually exclusive population categories."""
    
    def __init__(self):
        """Initialize with hierarchical mapping."""
        
        # Age groups (mutually exclusive)
        self.age_group_mapping = {
            'children': ['child', 'children', 'pediatric', 'youth under', 'age 5-12', 'elementary', 'school age', 'kids'],
            'adolescents': ['adolescent', 'teenager', 'teen', 'youth', 'high school', 'age 13-17', 'puberty'],
            'adults': ['adult', 'working age', 'age 18-64', 'college', 'university', 'employment'],
            'older_adults': ['older adult', 'elderly', 'senior', 'geriatric', 'age 65+', 'retirement', 'aging'],
            'perinatal': ['perinatal', 'pregnant', 'pregnancy', 'postpartum', 'maternal', 'prenatal', 'antenatal']
        }
        
        # Sex categories (mutually exclusive)
        self.sex_mapping = {
            'male': ['male', 'men', 'man', 'father', 'paternal'],
            'female': ['female', 'women', 'woman', 'mother', 'maternal'],
            'mixed': ['mixed', 'both', 'combined', 'all genders']
        }
        
        # Clinical cohorts
        self.clinical_cohort_mapping = {
            'diabetes': ['diabetes', 'diabetic', 'type 1 diabetes', 'type 2 diabetes', 'glucose'],
            'cancer': ['cancer', 'oncology', 'tumor', 'chemotherapy', 'radiation'],
            'cardiovascular': ['heart', 'cardiac', 'cardiovascular', 'hypertension', 'stroke'],
            'chronic_pain': ['chronic pain', 'pain', 'fibromyalgia', 'arthritis'],
            'general_population': ['general', 'community', 'population-based', 'general population']
        }
        
        # Settings
        self.setting_mapping = {
            'primary_care': ['primary care', 'clinic', 'outpatient', 'gp', 'family practice'],
            'hospital': ['hospital', 'inpatient', 'medical center', 'emergency'],
            'school': ['school', 'educational', 'classroom', 'university', 'college'],
            'community': ['community', 'home-based', 'neighborhood', 'public health']
        }
    
    def extract_single_match(self, text: str, category_mapping: Dict[str, List[str]]) -> str:
        """Extract single best match from category mapping."""
        if pd.isna(text) or str(text).strip() == '':
            return 'unspecified'
        
        text_lower = str(text).lower()
        
        # Find all matches
        matches = []
        for category, keywords in category_mapping.items():
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append((category, len(keyword)))  # Prefer longer matches
        
        if matches:
            # Return the match with longest keyword (most specific)
            return max(matches, key=lambda x: x[1])[0]
        
        return 'unspecified'
    
    def create_mutually_exclusive_stratum(self, row: pd.Series) -> str:
        """Create mutually exclusive stratum identifier."""
        components = []
        
        # Extract each dimension
        age = self.extract_single_match(row.get('population', ''), self.age_group_mapping)
        sex = self.extract_single_match(row.get('population', ''), self.sex_mapping)
        cohort = self.extract_single_match(row.get('population', ''), self.clinical_cohort_mapping)
        setting = self.extract_single_match(row.get('population', ''), self.setting_mapping)
        
        # Build stratum with hierarchy: Age > Sex > Cohort > Setting
        # Only include meaningful (non-unspecified) components
        
        primary_component = None
        
        # Priority 1: Specific age + sex combinations (most specific)
        if age != 'unspecified' and sex != 'unspecified':
            primary_component = f"{age}_{sex}"
        # Priority 2: Age groups alone
        elif age != 'unspecified':
            primary_component = age
        # Priority 3: Sex alone (only if age is unspecified)
        elif sex != 'unspecified':
            primary_component = sex
        # Priority 4: Clinical cohort
        elif cohort != 'unspecified':
            primary_component = cohort
        # Priority 5: Setting
        elif setting != 'unspecified':
            primary_component = setting
        else:
            primary_component = 'general_population'
        
        # Add secondary descriptors only if they add meaningful information
        secondary_components = []
        
        # Add cohort if it's different from primary
        if cohort != 'unspecified' and cohort not in primary_component:
            secondary_components.append(cohort)
        
        # Add setting if it's specific
        if setting != 'unspecified' and setting not in primary_component and len(secondary_components) < 2:
            secondary_components.append(setting)
        
        # Build final stratum ID
        if secondary_components:
            return f"{primary_component}_{secondary_components[0]}"
        else:
            return primary_component
    
    def explode_to_long_format_fixed(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert to long format with mutually exclusive strata."""
        logger.info(f"Converting {len(df)} records to mutually exclusive long format")
        
        # Ensure we have the required columns
        required_cols = ['pmid', 'year', 'population', 'treatments', 'outcomes']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Missing column {col}, using empty values")
                df[col] = ''
        
        long_records = []
        
        for _, row in df.iterrows():
            # Create mutually exclusive stratum
            stratum_id = self.create_mutually_exclusive_stratum(row)
            
            # Extract age, sex for separate columns (for analysis)
            age_group = self.extract_single_match(row.get('population', ''), self.age_group_mapping)
            sex = self.extract_single_match(row.get('population', ''), self.sex_mapping)
            clinical_cohort = self.extract_single_match(row.get('population', ''), self.clinical_cohort_mapping)
            setting = self.extract_single_match(row.get('population', ''), self.setting_mapping)
            
            # Split treatments if multiple
            treatments = str(row.get('treatments', '')).split(';') if pd.notna(row.get('treatments', '')) else ['']
            outcomes = str(row.get('outcomes', '')).split(';') if pd.notna(row.get('outcomes', '')) else ['']
            
            # Create records for each treatment-outcome combination
            for treatment in treatments:
                for outcome in outcomes:
                    long_record = {
                        'pmid': row.get('pmid', ''),
                        'title': row.get('title', ''),
                        'year': row.get('year', ''),
                        'journal': row.get('journal', ''),
                        'stratum_id': stratum_id,
                        'age_group': age_group,
                        'sex': sex,
                        'clinical_cohort': clinical_cohort,
                        'setting': setting,
                        'treatment_category': self.clean_treatment(treatment.strip()),
                        'treatment_names': treatment.strip(),
                        'outcome_direction': self.clean_outcome(outcome.strip()),
                        'risk_factors': row.get('risk_factors', ''),
                        'symptoms': row.get('symptoms', '')
                    }
                    long_records.append(long_record)
        
        result_df = pd.DataFrame(long_records)
        logger.info(f"Created {len(result_df)} long-format records with {result_df['stratum_id'].nunique()} mutually exclusive strata")
        
        return result_df
    
    def clean_treatment(self, treatment: str) -> str:
        """Clean treatment names."""
        if pd.isna(treatment) or treatment == '':
            return 'unspecified'
        
        treatment_lower = str(treatment).lower().strip()
        
        # Standard mappings
        if 'cbt' in treatment_lower or 'cognitive behavioral' in treatment_lower:
            return 'CBT'
        elif 'act' in treatment_lower or 'acceptance and commitment' in treatment_lower:
            return 'ACT'
        elif 'dbt' in treatment_lower or 'dialectical behavior' in treatment_lower:
            return 'DBT'
        elif 'mindfulness' in treatment_lower or 'meditation' in treatment_lower:
            return 'mindfulness'
        elif 'psychotherapy' in treatment_lower or 'therapy' in treatment_lower:
            return 'psychotherapy'
        elif 'medication' in treatment_lower or 'pharmacotherapy' in treatment_lower:
            return 'medication'
        elif 'exercise' in treatment_lower or 'physical activity' in treatment_lower:
            return 'exercise'
        else:
            return 'other'
    
    def clean_outcome(self, outcome: str) -> str:
        """Clean outcome names."""
        if pd.isna(outcome) or outcome == '':
            return 'unspecified'
        
        outcome_lower = str(outcome).lower().strip()
        
        if 'improve' in outcome_lower or 'better' in outcome_lower or 'positive' in outcome_lower:
            return 'improvement'
        elif 'reduce' in outcome_lower or 'decrease' in outcome_lower:
            return 'symptom_reduction'
        elif 'no change' in outcome_lower or 'unchanged' in outcome_lower:
            return 'no_change'
        elif 'mixed' in outcome_lower or 'variable' in outcome_lower:
            return 'mixed_results'
        else:
            return 'unspecified'


def main():
    """Test fixed normalization."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python fixed_normalize_labels.py <input_csv> <output_csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} records from {input_file}")
    
    # Create mutually exclusive normalization
    normalizer = FixedFieldNormalizer()
    normalized_df = normalizer.explode_to_long_format_fixed(df)
    
    # Save results
    normalized_df.to_csv(output_file, index=False)
    
    print(f"\n🔧 FIXED NORMALIZATION COMPLETE")
    print("="*50)
    print(f"Original records: {len(df)}")
    print(f"Normalized records: {len(normalized_df)}")
    print(f"Mutually exclusive strata: {normalized_df['stratum_id'].nunique()}")
    
    # Show top strata
    print("\nTop 10 mutually exclusive strata:")
    strata_counts = normalized_df['stratum_id'].value_counts().head(10)
    for stratum, count in strata_counts.items():
        print(f"  • {stratum}: {count} records")
    
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()