"""
GPT Output Field Splitter Module
Extracts structured fields from the gpt_output column containing:
- Population
- Risk Factors  
- Symptoms
- Treatments/Interventions
- Outcomes
- Chain of Thought reasoning
"""

import pandas as pd
import re
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPTOutputSplitter:
    """Splits the gpt_output field into structured components."""
    
    def __init__(self):
        """Initialize the splitter with field patterns."""
        self.field_patterns = {
            'population': [
                r'(?i)(?:population|participants?|subjects?|cohort|demographic).*?(?:focus|in focus|studied|examined):?\s*[-]?\s*(.+?)(?=\n\d+\.|$)',
                r'(?i)\*\*(?:population|participants?|subjects?|cohort|demographic).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)',
                r'(?i)(?:population|participants?|subjects?|cohort|demographic)\s*(?:in focus|studied|examined)?:?\s*[-]?\s*(.+?)(?=\n|$)'
            ],
            'risk_factors': [
                r'(?i)(?:risk factors?|causes?|triggers?|predictors?).*?:?\s*[-]?\s*(.+?)(?=\n\d+\.|$)',
                r'(?i)\*\*(?:risk factors?|causes?|triggers?|predictors?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)'
            ],
            'symptoms': [
                r'(?i)(?:symptoms?|manifestations?|presentations?|clinical features?).*?:?\s*[-]?\s*(.+?)(?=\n\d+\.|$)',
                r'(?i)\*\*(?:symptoms?|manifestations?|presentations?|clinical features?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)'
            ],
            'treatments': [
                r'(?i)(?:treatments?|interventions?|therapies?|management|approaches?).*?:?\s*[-]?\s*(.+?)(?=\n\d+\.|$)',
                r'(?i)\*\*(?:treatments?|interventions?|therapies?|management|approaches?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)'
            ],
            'outcomes': [
                r'(?i)(?:outcomes?|results?|effects?|findings?|conclusions?).*?:?\s*[-]?\s*(.+?)(?=\n\d+\.|$)',
                r'(?i)\*\*(?:outcomes?|results?|effects?|findings?|conclusions?).*?\*\*:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)'
            ]
        }
    
    def extract_field(self, text: str, field_name: str) -> str:
        """Extract a specific field from GPT output text."""
        if not text or field_name not in self.field_patterns:
            return ""
        
        # Try each pattern for the field
        for pattern in self.field_patterns[field_name]:
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                extracted = match.group(1).strip()
                # Clean up the extracted text
                extracted = re.sub(r'\n+', ' ', extracted)
                extracted = re.sub(r'\s+', ' ', extracted)
                extracted = extracted.strip('- ')
                if extracted and len(extracted) > 10:  # Minimum meaningful length
                    return extracted
        
        return ""
    
    def extract_all_fields(self, gpt_output: str) -> Dict[str, str]:
        """Extract all fields from a single GPT output."""
        result = {}
        for field_name in self.field_patterns.keys():
            result[field_name] = self.extract_field(gpt_output, field_name)
        
        # Extract Chain of Thought if present
        cot_pattern = r'(?i)(?:chain of thought|reasoning|rationale).*?:?\s*[-]?\s*(.+?)(?=\n\*\*|\n\d+\.|$)'
        cot_match = re.search(cot_pattern, gpt_output, re.DOTALL | re.MULTILINE)
        result['chain_of_thought'] = cot_match.group(1).strip() if cot_match else ""
        
        return result
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process a dataframe with gpt_output column and split into structured fields."""
        logger.info(f"Processing {len(df)} rows with GPT output splitting")
        
        if 'gpt_output' not in df.columns:
            raise ValueError("DataFrame must contain 'gpt_output' column")
        
        # Extract fields for each row
        extracted_fields = []
        for idx, row in df.iterrows():
            gpt_output = str(row['gpt_output']) if pd.notna(row['gpt_output']) else ""
            fields = self.extract_all_fields(gpt_output)
            extracted_fields.append(fields)
        
        # Convert to DataFrame and merge with original
        fields_df = pd.DataFrame(extracted_fields)
        result_df = pd.concat([df, fields_df], axis=1)
        
        logger.info(f"Extracted fields: {list(fields_df.columns)}")
        logger.info(f"Non-empty extractions per field:")
        for col in fields_df.columns:
            non_empty = fields_df[col].str.len() > 0
            logger.info(f"  {col}: {non_empty.sum()}/{len(fields_df)} ({non_empty.mean():.1%})")
        
        return result_df
    
    def save_processed_data(self, df: pd.DataFrame, output_path: str):
        """Save the processed dataframe with extracted fields."""
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")


def main():
    """Main function for testing the splitter."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python gpt_output_splitter.py <input_csv> <output_csv>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Load data
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows from {input_path}")
    
    # Process
    splitter = GPTOutputSplitter()
    processed_df = splitter.process_dataframe(df)
    
    # Save
    splitter.save_processed_data(processed_df, output_path)
    print(f"Processing complete. Results saved to {output_path}")


if __name__ == "__main__":
    main()