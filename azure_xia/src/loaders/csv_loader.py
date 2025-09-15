"""
CSV Data Loader with Validation
Loads and validates the processed mental health literature data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MentalHealthDataLoader:
    """Loads and validates mental health literature data from CSV."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.required_columns = [
            'pmid', 'title', 'abstract', 'year', 'journal',
            'population', 'risk_factors', 'symptoms', 'treatments', 'outcomes'
        ]
        self.optional_columns = ['chain_of_thought', 'date', 'publication_type', 'classification']
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load data from CSV file with validation."""
        logger.info(f"Loading data from {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Validate structure
            self._validate_structure(df)
            
            # Clean and prepare data
            df = self._clean_data(df)
            
            logger.info(f"Data validation successful. Final shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
    
    def _validate_structure(self, df: pd.DataFrame):
        """Validate the DataFrame structure."""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.info("✓ All required columns present")
        
        # Check for completely empty columns
        empty_columns = [col for col in self.required_columns if df[col].isna().all()]
        if empty_columns:
            logger.warning(f"Warning: Columns with all missing values: {empty_columns}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the data."""
        df = df.copy()
        
        # Convert year to numeric
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            year_range = (df['year'].min(), df['year'].max())
            logger.info(f"Year range: {year_range}")
        
        # Clean text fields
        text_fields = ['population', 'risk_factors', 'symptoms', 'treatments', 'outcomes']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str)
                df[field] = df[field].str.strip()
                df[field] = df[field].replace('nan', '')
                df[field] = df[field].replace('', np.nan)
        
        # Log data quality
        self._log_data_quality(df)
        
        return df
    
    def _log_data_quality(self, df: pd.DataFrame):
        """Log data quality statistics."""
        logger.info("Data Quality Summary:")
        for col in self.required_columns:
            if col in df.columns:
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                logger.info(f"  {col}: {missing_pct:.1f}% missing")
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics about the dataset."""
        stats = {
            'total_records': len(df),
            'year_range': (df['year'].min(), df['year'].max()) if 'year' in df.columns else None,
            'unique_journals': df['journal'].nunique() if 'journal' in df.columns else None,
            'field_completeness': {}
        }
        
        # Calculate field completeness
        for field in ['population', 'risk_factors', 'symptoms', 'treatments', 'outcomes']:
            if field in df.columns:
                non_empty = df[field].notna() & (df[field] != '')
                stats['field_completeness'][field] = {
                    'count': non_empty.sum(),
                    'percentage': (non_empty.sum() / len(df)) * 100
                }
        
        return stats


def main():
    """Main function for testing the loader."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python csv_loader.py <input_csv>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Load and validate data
    loader = MentalHealthDataLoader()
    df = loader.load_data(input_path)
    
    # Get summary statistics
    stats = loader.get_summary_stats(df)
    
    print("\n" + "="*50)
    print("DATASET SUMMARY")
    print("="*50)
    print(f"Total Records: {stats['total_records']}")
    print(f"Year Range: {stats['year_range']}")
    print(f"Unique Journals: {stats['unique_journals']}")
    
    print("\nField Completeness:")
    for field, data in stats['field_completeness'].items():
        print(f"  {field}: {data['count']} ({data['percentage']:.1f}%)")


if __name__ == "__main__":
    main()