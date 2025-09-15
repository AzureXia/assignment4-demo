"""
Plot Interpretation Generator
Creates detailed explanations for each visualization.
"""

import pandas as pd
import base64
import os
from typing import Dict, Any


class PlotInterpreter:
    """Generates detailed plot interpretations."""
    
    def __init__(self, tables_dir: str, plots_dir: str):
        """Initialize with data directories."""
        self.tables_dir = tables_dir
        self.plots_dir = plots_dir
    
    def interpret_stratum_overview(self) -> Dict[str, Any]:
        """Interpret the stratum overview plot."""
        # Load stratum data
        df = pd.read_csv(f"{self.tables_dir}/stratum_summary_by_stratum.csv")
        
        total_strata = len(df)
        top_group = df.iloc[0]['stratum_id']
        top_studies = df.iloc[0]['unique_studies'] 
        top_records = df.iloc[0]['total_records']
        
        interpretation = {
            "title": "Population Groups: Research Coverage Analysis",
            "what_it_shows": "This chart displays research coverage across different population groups, showing both the number of unique studies and total data records for each group.",
            "key_difference": {
                "unique_studies": "Each research paper counts once, regardless of how many data points it contributes",
                "total_records": "All data entries from each paper are counted separately (one paper may contribute multiple records)"
            },
            "key_findings": [
                f"**Most Studied Group**: '{top_group}' with {top_studies} unique studies and {top_records} total records",
                f"**Population Diversity**: {total_strata} distinct population groups identified from the literature",
                f"**Research Gaps**: Several groups have fewer than 5 studies, indicating underresearched populations",
                "**Hierarchical Structure**: Groups are mutually exclusive (e.g., 'male' vs 'adults_male' vs 'perinatal_female')"
            ],
            "clinical_implications": [
                "**Research Priorities**: Groups with fewer studies may need targeted funding",
                "**Evidence Quality**: Groups with more studies provide stronger evidence for clinical decisions", 
                "**Population Coverage**: The diversity shows mental health research spans various demographics",
                "**Data Richness**: Higher record counts indicate more detailed analysis opportunities"
            ],
            "interpretation_guide": "Look for groups on the left side of the chart - these are underrepresented in current research. The gap between studies and records shows how much detail each population group has been studied with."
        }
        
        return interpretation
    
    def interpret_risk_factors(self) -> Dict[str, Any]:
        """Interpret the risk factors plot."""
        # Load risk factors data
        df = pd.read_csv(f"{self.tables_dir}/risk_factors_by_stratum.csv")
        
        top_strata = df.groupby('stratum_id')['total_studies'].first().nlargest(6).index.tolist()
        
        interpretation = {
            "title": "Risk Factors by Population Group",
            "what_it_shows": "This multi-panel chart shows the most common risk factors for mental health issues within each population group, displayed as percentages of studies reporting each risk factor.",
            "methodology": "Only risk factors mentioned in ≥10% of studies within each group are shown to focus on the most significant patterns.",
            "key_findings": [
                f"**Population Groups Analyzed**: {len(top_strata)} groups with sufficient data",
                "**Risk Factor Diversity**: Different populations show different risk factor profiles",
                "**Data Quality Issue**: Many entries show 'Triggers' or incomplete extraction, indicating room for improvement in data processing",
                "**Population-Specific Patterns**: Each group has distinct risk factor frequencies"
            ],
            "how_to_read": [
                "**Each Panel**: Shows one population group (e.g., 'male', 'general_population')",
                "**Horizontal Bars**: Length represents percentage of studies mentioning that risk factor", 
                "**Y-axis Labels**: Specific risk factors identified in the literature",
                "**Percentages**: What proportion of studies in that group reported each risk factor"
            ],
            "clinical_implications": [
                "**Targeted Interventions**: Different populations may need different prevention strategies",
                "**Risk Assessment**: Clinicians can focus on population-specific risk factors",
                "**Research Gaps**: Some risk factors may be under-studied in certain populations",
                "**Prevention Planning**: Public health interventions can be tailored by population"
            ],
            "limitations": "Current data shows many 'unspecified' or partial entries, suggesting need for better extraction methods to reveal more specific risk factors."
        }
        
        return interpretation
    
    def interpret_symptoms_comparison(self) -> Dict[str, Any]:
        """Interpret the symptoms comparison heatmap."""
        # Load symptoms data
        df = pd.read_csv(f"{self.tables_dir}/symptoms_by_stratum.csv")
        
        num_groups = df['stratum_id'].nunique()
        
        interpretation = {
            "title": "Symptom Categories Across Population Groups",
            "what_it_shows": "This heatmap reveals how symptom reporting varies across different population groups, with color intensity showing the percentage of studies in each group that report specific symptoms.",
            "color_guide": {
                "Light Blue/White": "Low percentage of studies (0-20%) report this symptom",
                "Medium Blue": "Moderate percentage of studies (20-50%) report this symptom", 
                "Dark Blue": "High percentage of studies (50%+) report this symptom"
            },
            "key_findings": [
                f"**Population Coverage**: {num_groups} population groups with symptom data",
                "**Symptom Variability**: Different populations show different symptom profiles",
                "**Reporting Patterns**: Some symptoms are consistently reported across groups, others are population-specific",
                "**Data Challenges**: Long symptom descriptions suggest need for better categorization"
            ],
            "how_to_read": [
                "**Rows**: Different population groups (e.g., 'male', 'adolescents', 'perinatal_female')",
                "**Columns**: Different symptom categories identified in studies",
                "**Cell Values**: Percentage of studies in that population reporting that symptom",
                "**Color Intensity**: Darker = higher percentage, lighter = lower percentage"
            ],
            "clinical_applications": [
                "**Diagnostic Focus**: Clinicians can look for population-typical symptoms",
                "**Assessment Tools**: Different populations may need different symptom checklists", 
                "**Treatment Planning**: Symptom profiles can inform intervention selection",
                "**Research Priorities**: Empty or light cells indicate under-studied symptom-population combinations"
            ],
            "research_insights": [
                "**Population Specificity**: Mental health symptoms may manifest differently across demographics",
                "**Assessment Gaps**: Some populations may have understudied symptom presentations",
                "**Measurement Issues**: Long, unclear symptom descriptions indicate need for standardized measures"
            ]
        }
        
        return interpretation
    
    def interpret_treatment_outcomes(self) -> Dict[str, Any]:
        """Interpret treatment outcomes heatmap."""
        # Load treatment outcomes data  
        df = pd.read_csv(f"{self.tables_dir}/treatment_outcomes_by_stratum.csv")
        
        interpretation = {
            "title": "Treatment Categories vs Outcome Directions",
            "what_it_shows": "This heatmap shows the relationship between different treatment types and their reported outcomes across all population groups, revealing which treatments are associated with which types of results.",
            "methodology": "Data combines all population groups to show overall treatment-outcome patterns in the mental health literature (2020-2024).",
            "key_findings": [
                "**Treatment Diversity**: Multiple treatment approaches represented in the literature",
                "**Outcome Patterns**: Some treatments show consistent outcome patterns",
                "**Data Quality**: Many 'unspecified' outcomes indicate reporting challenges in original studies",
                "**Research Volume**: Cell values show how many studies report each treatment-outcome combination"
            ],
            "how_to_read": [
                "**Rows**: Different treatment categories (e.g., 'CBT', 'ACT', 'Psychotherapy')",
                "**Columns**: Different outcome directions (e.g., 'Improvement', 'No Change', 'Mixed Results')",
                "**Cell Numbers**: Count of studies reporting that treatment-outcome combination",
                "**Color Intensity**: Darker colors indicate more studies (stronger evidence base)"
            ],
            "clinical_insights": [
                "**Evidence-Based Practice**: Darker cells show treatment-outcome combinations with more research support",
                "**Treatment Selection**: Clinicians can see which treatments have stronger outcome evidence",
                "**Outcome Expectations**: Pattern shows realistic outcome distributions for different interventions",
                "**Research Gaps**: Light or empty cells indicate treatment-outcome combinations needing more study"
            ],
            "research_implications": [
                "**Study Design**: Future research should specify outcome measures more clearly",
                "**Treatment Comparison**: Heatmap reveals which treatments have been compared most often",
                "**Outcome Standardization**: Need for consistent outcome reporting across studies"
            ],
            "limitations": "High proportion of 'unspecified' outcomes suggests original studies often lack clear outcome measurement, limiting the ability to draw strong conclusions about treatment effectiveness."
        }
        
        return interpretation
    
    def interpret_sankey_flow(self) -> Dict[str, Any]:
        """Interpret the Sankey flow diagram."""
        interpretation = {
            "title": "Mental Health Treatment Pathways",
            "what_it_shows": "This interactive flow diagram traces the path from population groups → treatment types → outcomes, showing how different demographics connect to treatments and their results.",
            "visual_elements": {
                "Blue Nodes (👥)": "Population groups (e.g., Adults, Adolescents, Perinatal Female)",
                "Green Nodes (🏥)": "Treatment categories (e.g., CBT, ACT, Psychotherapy, Medication)",
                "Orange Nodes (📈)": "Outcome categories (e.g., Improvement, Mixed Results, Symptom Reduction)",
                "Flow Width": "Thicker flows = more studies, thinner flows = fewer studies"
            },
            "key_findings": [
                "**Treatment Pathways**: Visualizes which populations receive which treatments",
                "**Outcome Patterns**: Shows which treatments lead to which types of outcomes", 
                "**Research Volume**: Flow thickness indicates strength of evidence",
                "**Treatment Diversity**: Multiple treatment options represented across populations"
            ],
            "how_to_interact": [
                "**Hover**: Mouse over nodes and flows to see specific numbers",
                "**Follow Paths**: Trace from a population → through treatments → to outcomes",
                "**Compare Flows**: Thicker flows indicate more research evidence",
                "**Identify Gaps**: Missing connections show research opportunities"
            ],
            "clinical_applications": [
                "**Treatment Selection**: See which treatments are most used with specific populations",
                "**Outcome Prediction**: Understand likely outcomes for population-treatment combinations",
                "**Evidence Strength**: Thicker flows indicate more research support",
                "**Care Pathways**: Visualize typical treatment journeys for different groups"
            ],
            "research_insights": [
                "**Study Distribution**: Shows which population-treatment combinations have been studied most",
                "**Outcome Reporting**: Reveals patterns in how outcomes are measured and reported", 
                "**Research Gaps**: Thin or missing flows indicate understudied combinations",
                "**Treatment Innovation**: Can identify populations that might benefit from different treatment approaches"
            ],
            "interpretation_guide": "Start with a population group on the left, follow the flows to see what treatments they typically receive, then continue to see what outcomes are reported. Thicker flows indicate stronger evidence bases."
        }
        
        return interpretation
    
    def generate_all_interpretations(self) -> Dict[str, Dict[str, Any]]:
        """Generate interpretations for all plots."""
        return {
            "stratum_overview": self.interpret_stratum_overview(),
            "risk_factors": self.interpret_risk_factors(), 
            "symptoms_comparison": self.interpret_symptoms_comparison(),
            "treatment_outcomes": self.interpret_treatment_outcomes(),
            "sankey_flow": self.interpret_sankey_flow()
        }
    
    def embed_plot_as_base64(self, plot_filename: str) -> str:
        """Convert plot to base64 for embedding."""
        plot_path = f"{self.plots_dir}/{plot_filename}"
        if os.path.exists(plot_path):
            with open(plot_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded_string}"
        return ""


def main():
    """Generate plot interpretations."""
    tables_dir = "outputs/tables_fixed"
    plots_dir = "outputs/plots"
    
    interpreter = PlotInterpreter(tables_dir, plots_dir)
    interpretations = interpreter.generate_all_interpretations()
    
    # Print summary
    print("📊 PLOT INTERPRETATIONS GENERATED")
    print("="*50)
    for plot_name, interpretation in interpretations.items():
        print(f"✓ {plot_name}: {interpretation['title']}")
    
    return interpretations


if __name__ == "__main__":
    main()