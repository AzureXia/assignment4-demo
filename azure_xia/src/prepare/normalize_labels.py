"""
Field Normalization Module
Normalizes extracted fields into standardized categories for analysis.
"""

import pandas as pd
import re
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FieldNormalizer:
    """Normalizes extracted fields into standardized categories."""
    
    def __init__(self):
        """Initialize normalization mappings."""
        self.age_group_mapping = {
            'adolescents': ['adolescent', 'teen', 'teenage', 'youth', 'young people', 'minors', '13-17', '12-18'],
            'adults': ['adult', 'grown-up', '18-65', '18-64', 'working age'],
            'older_adults': ['older adult', 'elderly', 'senior', 'geriatric', '65+', 'aged'],
            'children': ['child', 'children', 'pediatric', 'kid', 'infant', 'toddler', '0-12'],
            'perinatal': ['pregnant', 'pregnancy', 'postpartum', 'maternal', 'prenatal', 'perinatal'],
            'mixed': ['all ages', 'mixed ages', 'various ages', 'cross-sectional age'],
            'unspecified': ['general population', 'participants', 'subjects', 'patients', 'individuals']
        }
        
        self.sex_mapping = {
            'female': ['female', 'women', 'woman', 'girls', 'girl'],
            'male': ['male', 'men', 'man', 'boys', 'boy'],
            'mixed': ['both sexes', 'mixed gender', 'male and female'],
            'unspecified': ['participants', 'patients', 'individuals', 'people']
        }
        
        self.clinical_cohort_mapping = {
            'cancer': ['cancer', 'oncology', 'tumor', 'malignancy', 'chemotherapy'],
            'cardiovascular': ['cardiovascular', 'cardiac', 'heart disease', 'hypertension'],
            'diabetes': ['diabetes', 'diabetic', 'glucose', 'insulin'],
            'chronic_pain': ['chronic pain', 'fibromyalgia', 'arthritis', 'pain'],
            'substance_use': ['substance use', 'addiction', 'alcohol', 'drug use'],
            'autism': ['autism', 'asd', 'asperger'],
            'adhd': ['adhd', 'attention deficit', 'hyperactivity'],
            'comorbid_mental': ['bipolar', 'schizophrenia', 'ptsd', 'ocd'],
            'medical_general': ['medical patients', 'chronic illness', 'comorbidity']
        }
        
        self.setting_mapping = {
            'primary_care': ['primary care', 'gp', 'family medicine', 'community'],
            'inpatient': ['inpatient', 'hospital', 'ward', 'admission'],
            'outpatient': ['outpatient', 'clinic', 'ambulatory'],
            'school': ['school', 'educational', 'university', 'college'],
            'community': ['community', 'home', 'residential']
        }
        
        self.treatment_category_mapping = {
            'pharmacological': [
                'antidepressant', 'ssri', 'snri', 'medication', 'drug', 'pharmaceutical',
                'sertraline', 'fluoxetine', 'escitalopram', 'paroxetine', 'bupropion'
            ],
            'psychotherapy': [
                'psychotherapy', 'cbt', 'cognitive behavioral', 'therapy', 'counseling',
                'psychodynamic', 'interpersonal therapy', 'dbt', 'act'
            ],
            'behavioral': [
                'behavioral', 'lifestyle', 'exercise', 'diet', 'mindfulness',
                'meditation', 'relaxation', 'stress management'
            ],
            'digital': [
                'digital', 'online', 'app', 'internet', 'web-based', 'telemedicine'
            ],
            'combined': [
                'combined', 'multimodal', 'integrated', 'combination'
            ]
        }
        
        self.outcome_direction_mapping = {
            'benefit': [
                'improved', 'decreased', 'reduced', 'effective', 'successful',
                'better', 'positive', 'significant improvement', 'remission'
            ],
            'no_effect': [
                'no difference', 'no effect', 'non-significant', 'unchanged',
                'no improvement', 'ineffective'
            ],
            'harm': [
                'worsened', 'increased', 'adverse', 'side effects', 'harmful',
                'deteriorated', 'negative'
            ],
            'mixed': [
                'mixed', 'variable', 'inconsistent', 'some improvement',
                'partial', 'limited effect'
            ]
        }
    
    def normalize_population(self, text: str) -> Dict[str, List[str]]:
        """Normalize population text into structured categories."""
        if not text or pd.isna(text):
            return {'age_group': [], 'sex': [], 'clinical_cohort': [], 'setting': []}
        
        text_lower = text.lower()
        
        result = {
            'age_group': self._match_categories(text_lower, self.age_group_mapping),
            'sex': self._match_categories(text_lower, self.sex_mapping),
            'clinical_cohort': self._match_categories(text_lower, self.clinical_cohort_mapping),
            'setting': self._match_categories(text_lower, self.setting_mapping)
        }
        
        # Default to unspecified if no matches
        for key in result:
            if not result[key]:
                result[key] = ['unspecified']
        
        return result
    
    def normalize_treatments(self, text: str) -> Dict[str, List[str]]:
        """Normalize treatments into categories and extract names."""
        if not text or pd.isna(text):
            return {'categories': [], 'names': []}
        
        text_lower = text.lower()
        categories = self._match_categories(text_lower, self.treatment_category_mapping)
        
        # Extract treatment names (simple approach)
        names = self._extract_treatment_names(text)
        
        return {
            'categories': categories if categories else ['other'],
            'names': names
        }
    
    def normalize_outcomes(self, text: str) -> List[str]:
        """Normalize outcomes into direction categories."""
        if not text or pd.isna(text):
            return ['unspecified']
        
        text_lower = text.lower()
        directions = self._match_categories(text_lower, self.outcome_direction_mapping)
        
        return directions if directions else ['unspecified']
    
    def _match_categories(self, text: str, mapping: Dict[str, List[str]]) -> List[str]:
        """Match text against category mapping."""
        matches = []
        for category, keywords in mapping.items():
            for keyword in keywords:
                if keyword in text:
                    matches.append(category)
                    break  # Only add category once
        return matches
    
    def _extract_treatment_names(self, text: str) -> List[str]:
        """Extract specific treatment names from text."""
        # Simple extraction - look for capitalized words that might be treatment names
        names = []
        
        # Common treatment patterns
        patterns = [
            r'(?i)(cognitive behavioral therapy|cbt)',
            r'(?i)(dialectical behavior therapy|dbt)',
            r'(?i)(acceptance and commitment therapy|act)',
            r'(?i)(mindfulness-based|mbsr|mbct)',
            r'(?i)(interpersonal therapy|ipt)',
            r'(?i)(sertraline|fluoxetine|escitalopram|paroxetine|bupropion)',
            r'(?i)(exercise|yoga|meditation|mindfulness)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            names.extend([match[0] if isinstance(match, tuple) else match for match in matches])
        
        return list(set(names))  # Remove duplicates
    
    def explode_to_long_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert multi-valued fields to long format for analysis."""
        logger.info("Converting to long format for analysis")
        
        rows = []
        for _, row in df.iterrows():
            # Normalize fields
            pop_norm = self.normalize_population(row.get('population', ''))
            treat_norm = self.normalize_treatments(row.get('treatments', ''))
            outcome_norm = self.normalize_outcomes(row.get('outcomes', ''))
            
            # Parse multi-valued fields
            risk_factors = self._parse_list_field(row.get('risk_factors', ''))
            symptoms = self._parse_list_field(row.get('symptoms', ''))
            
            # Create combinations
            for age_group in pop_norm['age_group']:
                for sex in pop_norm['sex']:
                    for clinical_cohort in pop_norm['clinical_cohort']:
                        for setting in pop_norm['setting']:
                            for treat_cat in treat_norm['categories']:
                                for outcome_dir in outcome_norm:
                                    # Create stratum ID
                                    stratum_parts = []
                                    if age_group != 'unspecified':
                                        stratum_parts.append(age_group)
                                    if sex != 'unspecified':
                                        stratum_parts.append(sex)
                                    if clinical_cohort != 'unspecified':
                                        stratum_parts.append(clinical_cohort)
                                    if setting != 'unspecified':
                                        stratum_parts.append(setting)
                                    
                                    stratum_id = '|'.join(stratum_parts) if stratum_parts else 'general'
                                    
                                    base_row = {
                                        'pmid': row['pmid'],
                                        'title': row['title'],
                                        'year': row['year'],
                                        'journal': row['journal'],
                                        'stratum_id': stratum_id,
                                        'age_group': age_group,
                                        'sex': sex,
                                        'clinical_cohort': clinical_cohort,
                                        'setting': setting,
                                        'treatment_category': treat_cat,
                                        'treatment_names': '; '.join(treat_norm['names']),
                                        'outcome_direction': outcome_dir,
                                        'risk_factors': '; '.join(risk_factors),
                                        'symptoms': '; '.join(symptoms)
                                    }
                                    rows.append(base_row)
        
        result_df = pd.DataFrame(rows)
        logger.info(f"Exploded to {len(result_df)} rows from {len(df)} original rows")
        
        return result_df
    
    def _parse_list_field(self, text: str) -> List[str]:
        """Parse list-like field (semicolon or comma separated)."""
        if not text or pd.isna(text):
            return []
        
        # Split by semicolons or commas, clean up
        items = re.split(r'[;,]', str(text))
        items = [item.strip() for item in items if item.strip()]
        return items


def main():
    """Main function for testing normalization."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python normalize_labels.py <input_csv> <output_csv>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows from {input_path}")
    
    # Normalize
    normalizer = FieldNormalizer()
    normalized_df = normalizer.explode_to_long_format(df)
    
    # Save
    normalized_df.to_csv(output_path, index=False)
    print(f"Normalization complete. Results saved to {output_path}")
    print(f"Output shape: {normalized_df.shape}")


if __name__ == "__main__":
    main()