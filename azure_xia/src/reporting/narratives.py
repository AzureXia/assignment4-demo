"""
LLM-Enhanced Narrative Generation
Uses Amplify API to generate insights and summaries for population strata.
"""

import pandas as pd
import json
import sys
import os
from typing import Dict, List, Any, Optional
import logging

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from agents.amplify_client import AmplifyClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StratumNarrativeGenerator:
    """Generates LLM-powered narratives and insights for population strata."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize with Amplify client."""
        try:
            self.client = AmplifyClient(model=model)
            logger.info(f"Initialized Amplify client with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Amplify client: {e}")
            self.client = None
    
    def generate_stratum_insights(self, stratum_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate insights for a single population stratum."""
        if not self.client:
            return {"error": "Amplify client not available"}
        
        # Prepare data summary for LLM
        prompt = self._build_analysis_prompt(stratum_data)
        
        try:
            messages = [
                {"role": "system", "content": "You are a mental health research analyst. Provide concise, evidence-based insights about population strata in clinical depression and anxiety research."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.query(messages, max_tokens=300)
            
            return {
                "stratum_id": stratum_data["stratum_id"],
                "insight": response,
                "data_summary": stratum_data
            }
            
        except Exception as e:
            logger.error(f"LLM query failed for stratum {stratum_data['stratum_id']}: {e}")
            return {
                "stratum_id": stratum_data["stratum_id"],
                "insight": f"Analysis unavailable due to API error: {str(e)}",
                "data_summary": stratum_data
            }
    
    def _build_analysis_prompt(self, stratum_data: Dict[str, Any]) -> str:
        """Build analysis prompt for LLM."""
        prompt = f"""
Analyze this population stratum from mental health literature:

**Population Stratum**: {stratum_data['stratum_id']}
**Studies**: {stratum_data.get('unique_studies', 0)} unique studies
**Time Period**: {stratum_data.get('year_range', 'Unknown')}

**Key Data Points**:
- Top Risk Factor: {stratum_data.get('top_risk_factor', 'Not specified')[:100]}
- Most Common Treatment: {stratum_data.get('top_treatment', 'Not specified')}
- Primary Outcome: {stratum_data.get('top_outcome', 'Not specified')}

**Additional Context**:
{stratum_data.get('additional_context', '')}

Please provide:
1. **Key Clinical Insights** (2-3 sentences about what this data reveals)
2. **Research Gaps** (1-2 sentences about missing information)
3. **Clinical Implications** (1-2 sentences about practical applications)

Keep response under 200 words, focused on actionable insights for researchers and clinicians.
        """
        return prompt.strip()
    
    def enhance_population_classification(self, population_text: str) -> Dict[str, List[str]]:
        """Use LLM to enhance population classification beyond keyword matching."""
        if not self.client:
            return {"error": ["LLM not available"]}
        
        prompt = f"""
Analyze this population description from a mental health research abstract:

"{population_text}"

Classify into these categories (return only the category names that apply):

**Age Groups**: children, adolescents, adults, older_adults, perinatal, mixed, unspecified
**Sex**: male, female, mixed, unspecified  
**Clinical Cohorts**: cancer, cardiovascular, diabetes, chronic_pain, substance_use, autism, adhd, comorbid_mental, medical_general, unspecified
**Settings**: primary_care, inpatient, outpatient, school, community, unspecified

Return as JSON:
{{"age_group": ["category"], "sex": ["category"], "clinical_cohort": ["category"], "setting": ["category"]}}

Only include categories that clearly apply. Use "unspecified" if unclear.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a clinical research classifier. Return only valid JSON with the specified categories."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.query(messages, max_tokens=150)
            
            # Parse JSON response
            import json
            classification = json.loads(response)
            return classification
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # Fallback to keyword-based classification
            from prepare.normalize_labels import FieldNormalizer
            normalizer = FieldNormalizer()
            return normalizer.normalize_population(population_text)
    
    def generate_controversy_analysis(self, controversy_data: pd.DataFrame) -> str:
        """Analyze controversial findings using LLM."""
        if not self.client or controversy_data.empty:
            return "No controversial findings analysis available."
        
        # Prepare controversy summary
        conflicts = []
        for _, row in controversy_data.head(5).iterrows():  # Top 5 controversies
            conflicts.append({
                "stratum": row.get('stratum_id', ''),
                "treatment": row.get('treatment_category', ''),
                "benefit_studies": row.get('n_benefit', 0),
                "harm_studies": row.get('n_harm', 0),
                "no_effect_studies": row.get('n_no_effect', 0)
            })
        
        prompt = f"""
Analyze these controversial findings in mental health treatment research:

{json.dumps(conflicts, indent=2)}

For each controversy, provide:
1. **Possible Explanations** for conflicting results
2. **Research Quality Considerations** that might explain differences
3. **Clinical Recommendations** for practitioners facing these uncertainties

Keep analysis concise (under 300 words total). Focus on actionable insights.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a clinical research methodologist analyzing conflicting study results."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.query(messages, max_tokens=400)
            return response
            
        except Exception as e:
            logger.error(f"Controversy analysis failed: {e}")
            return f"Controversy analysis unavailable: {str(e)}"
    
    def generate_comparative_insights(self, stratum_summaries: pd.DataFrame) -> str:
        """Generate comparative insights across population strata."""
        if not self.client or stratum_summaries.empty:
            return "Comparative analysis unavailable."
        
        # Prepare comparison data
        top_strata = stratum_summaries.nlargest(5, 'unique_studies')
        comparison_data = []
        
        for _, row in top_strata.iterrows():
            comparison_data.append({
                "stratum": row['stratum_id'],
                "studies": row['unique_studies'],
                "top_treatment": row['top_treatment'],
                "components": row['components']
            })
        
        prompt = f"""
Compare these top population strata from mental health research:

{json.dumps(comparison_data, indent=2)}

Identify:
1. **Key Differences** in treatment patterns across populations
2. **Underrepresented Groups** that need more research
3. **Research Priorities** based on study distribution

Provide actionable insights for future research planning (under 250 words).
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a research strategist analyzing mental health literature coverage."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.query(messages, max_tokens=350)
            return response
            
        except Exception as e:
            logger.error(f"Comparative analysis failed: {e}")
            return f"Comparative analysis unavailable: {str(e)}"


def main():
    """Test narrative generation."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python narratives.py <stratum_summary_csv>")
        sys.exit(1)
    
    # Load stratum summary
    summary_path = sys.argv[1]
    df = pd.read_csv(summary_path)
    
    # Initialize generator
    generator = StratumNarrativeGenerator()
    
    if generator.client:
        print("✓ Amplify client initialized successfully")
        
        # Test with first stratum
        if not df.empty:
            test_stratum = df.iloc[0].to_dict()
            print(f"\nGenerating insights for: {test_stratum['stratum_id']}")
            
            insights = generator.generate_stratum_insights(test_stratum)
            print("\n" + "="*60)
            print(f"STRATUM: {insights['stratum_id']}")
            print("="*60)
            print(insights['insight'])
            
            # Generate comparative insights
            print("\n" + "="*60)
            print("COMPARATIVE INSIGHTS")
            print("="*60)
            comparison = generator.generate_comparative_insights(df)
            print(comparison)
    else:
        print("❌ Amplify client initialization failed")
        print("Check your .env file with AMPLIFY_API_KEY and AMPLIFY_API_URL")


if __name__ == "__main__":
    main()