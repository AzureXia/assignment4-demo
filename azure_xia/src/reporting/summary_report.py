"""
User-Friendly Summary Report Generator
Explains what all the analysis files mean in plain English.
"""

import pandas as pd
import os
from typing import Dict, Any
import json


class SummaryReportGenerator:
    """Generates human-readable summaries of analysis results."""
    
    def __init__(self, tables_dir: str):
        """Initialize with tables directory."""
        self.tables_dir = tables_dir
        self.files = {
            'stratum_summary': 'stratum_summary_by_stratum.csv',
            'risk_factors': 'risk_factors_by_stratum.csv', 
            'symptoms': 'symptoms_by_stratum.csv',
            'treatments': 'treatments_by_stratum.csv',
            'outcomes': 'outcomes_by_stratum.csv',
            'treatment_outcomes': 'treatment_outcomes_by_stratum.csv'
        }
    
    def generate_executive_summary(self) -> str:
        """Generate a high-level executive summary."""
        summary = []
        summary.append("=" * 70)
        summary.append("📊 POPULATION-STRATUM ANALYSIS EXECUTIVE SUMMARY")
        summary.append("=" * 70)
        
        # Load stratum summary
        stratum_file = os.path.join(self.tables_dir, self.files['stratum_summary'])
        if os.path.exists(stratum_file):
            df = pd.read_csv(stratum_file)
            
            summary.append(f"\n🔍 OVERVIEW:")
            summary.append(f"   • {len(df)} distinct population groups identified")
            summary.append(f"   • {df['unique_studies'].sum()} total studies analyzed")
            summary.append(f"   • Time period: {df['year_range'].iloc[0] if not df.empty else 'Unknown'}")
            
            # Top populations
            top_3 = df.nlargest(3, 'unique_studies')
            summary.append(f"\n👥 LARGEST POPULATION GROUPS:")
            for i, (_, row) in enumerate(top_3.iterrows(), 1):
                group = row['stratum_id'].replace('|', ' + ')
                studies = row['unique_studies']
                summary.append(f"   {i}. {group}: {studies} studies")
            
            # Research gaps
            small_groups = df[df['unique_studies'] < 10]
            summary.append(f"\n⚠️  UNDERREPRESENTED GROUPS:")
            summary.append(f"   • {len(small_groups)} groups have <10 studies")
            summary.append(f"   • Need more research on: {', '.join(small_groups['stratum_id'].head(3).str.replace('|', ' + '))}")
        
        return "\n".join(summary)
    
    def explain_risk_factors(self) -> str:
        """Explain risk factors analysis."""
        explanation = []
        explanation.append("\n" + "=" * 50)
        explanation.append("🎯 RISK FACTORS ANALYSIS")
        explanation.append("=" * 50)
        explanation.append("Shows what causes or triggers depression/anxiety in different groups.")
        
        risk_file = os.path.join(self.tables_dir, self.files['risk_factors'])
        if os.path.exists(risk_file):
            df = pd.read_csv(risk_file)
            
            # Most common risk factors overall
            top_risks = df.groupby('risk_factor')['count'].sum().nlargest(5)
            explanation.append(f"\n📈 MOST COMMONLY CITED RISK FACTORS:")
            for risk, count in top_risks.items():
                if len(risk) > 60:
                    risk = risk[:60] + "..."
                explanation.append(f"   • {risk}: mentioned in {count} studies")
            
            # Population-specific insights
            explanation.append(f"\n🎯 POPULATION-SPECIFIC PATTERNS:")
            for group in ['male', 'female', 'adolescents', 'older_adults']:
                group_data = df[df['stratum_id'] == group]
                if not group_data.empty:
                    top_risk = group_data.nlargest(1, 'percentage')
                    if not top_risk.empty:
                        risk = top_risk.iloc[0]['risk_factor']
                        pct = top_risk.iloc[0]['percentage']
                        explanation.append(f"   • {group.title()}: {risk[:40]}... ({pct:.1f}% of studies)")
        
        return "\n".join(explanation)
    
    def explain_treatments(self) -> str:
        """Explain treatments analysis."""
        explanation = []
        explanation.append("\n" + "=" * 50)
        explanation.append("💊 TREATMENTS ANALYSIS")
        explanation.append("=" * 50)
        explanation.append("Shows what treatments are used for different population groups.")
        
        treat_file = os.path.join(self.tables_dir, self.files['treatments'])
        if os.path.exists(treat_file):
            df = pd.read_csv(treat_file)
            
            # Treatment categories overall
            categories = df[df['treatment_type'] == 'category'].groupby('treatment')['count'].sum().sort_values(ascending=False)
            explanation.append(f"\n📊 TREATMENT TYPES (% of studies):")
            total_studies = df['total_studies'].max() if not df.empty else 1
            for treatment, count in categories.head(5).items():
                pct = (count / total_studies) * 100
                explanation.append(f"   • {treatment.title()}: {pct:.1f}%")
            
            # Specific interventions
            names = df[df['treatment_type'] == 'name'].groupby('treatment')['count'].sum().nlargest(5)
            if not names.empty:
                explanation.append(f"\n🎯 SPECIFIC INTERVENTIONS:")
                for name, count in names.items():
                    explanation.append(f"   • {name}: {count} studies")
        
        return "\n".join(explanation)
    
    def explain_outcomes(self) -> str:
        """Explain outcomes analysis."""
        explanation = []
        explanation.append("\n" + "=" * 50)
        explanation.append("📈 OUTCOMES ANALYSIS")
        explanation.append("=" * 50)
        explanation.append("Shows whether treatments helped, harmed, or had no effect.")
        
        outcomes_file = os.path.join(self.tables_dir, self.files['outcomes'])
        if os.path.exists(outcomes_file):
            df = pd.read_csv(outcomes_file)
            
            # Overall outcomes
            overall = df.groupby('outcome_direction')['count'].sum().sort_values(ascending=False)
            explanation.append(f"\n📊 OVERALL TREATMENT OUTCOMES:")
            total = overall.sum()
            for outcome, count in overall.items():
                pct = (count / total) * 100
                emoji = {"benefit": "✅", "harm": "❌", "no_effect": "➖", "mixed": "⚖️", "unspecified": "❓"}.get(outcome, "📊")
                explanation.append(f"   {emoji} {outcome.replace('_', ' ').title()}: {pct:.1f}% ({count} reports)")
        
        return "\n".join(explanation)
    
    def explain_file_meanings(self) -> str:
        """Explain what each output file contains."""
        explanation = []
        explanation.append("\n" + "=" * 60)
        explanation.append("📁 WHAT EACH FILE CONTAINS")
        explanation.append("=" * 60)
        
        file_explanations = {
            'processed_data.csv': 'Original data with GPT fields split into columns',
            'normalized_data.csv': 'Data exploded by population groups (for analysis)',
            'stratum_summary_by_stratum.csv': '📊 Overview of each population group',
            'risk_factors_by_stratum.csv': '🎯 What causes problems in each group',
            'symptoms_by_stratum.csv': '🤒 What symptoms appear in each group', 
            'treatments_by_stratum.csv': '💊 What treatments are used for each group',
            'outcomes_by_stratum.csv': '📈 Whether treatments help/harm each group',
            'treatment_outcomes_by_stratum.csv': '🔗 Which treatments work for which groups'
        }
        
        for filename, description in file_explanations.items():
            filepath = os.path.join(self.tables_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                df = pd.read_csv(filepath)
                explanation.append(f"\n{description}")
                explanation.append(f"   File: {filename}")
                explanation.append(f"   Rows: {len(df)}, Size: {size//1024}KB")
        
        return "\n".join(explanation)
    
    def generate_key_insights(self) -> str:
        """Generate key actionable insights."""
        insights = []
        insights.append("\n" + "=" * 60)
        insights.append("💡 KEY INSIGHTS & RECOMMENDATIONS")
        insights.append("=" * 60)
        
        # Load data
        stratum_file = os.path.join(self.tables_dir, self.files['stratum_summary'])
        if os.path.exists(stratum_file):
            df = pd.read_csv(stratum_file)
            
            insights.append(f"\n🔬 RESEARCH PRIORITIES:")
            
            # Underrepresented groups
            small_groups = df[df['unique_studies'] < 5]
            if not small_groups.empty:
                insights.append(f"   • Increase research on: {', '.join(small_groups['stratum_id'].head(3))}")
            
            # Well-studied groups
            large_groups = df[df['unique_studies'] >= 20]
            if not large_groups.empty:
                insights.append(f"   • Well-studied populations: {', '.join(large_groups['stratum_id'].head(3))}")
            
            insights.append(f"\n🎯 CLINICAL IMPLICATIONS:")
            insights.append(f"   • Different populations may need different treatment approaches")
            insights.append(f"   • Risk factors vary significantly between groups")
            insights.append(f"   • Treatment effectiveness should be evaluated by population")
            
            insights.append(f"\n📊 DATA QUALITY:")
            total_studies = df['unique_studies'].sum()
            total_groups = len(df)
            avg_studies = total_studies / total_groups
            insights.append(f"   • Average {avg_studies:.1f} studies per population group")
            insights.append(f"   • {len(df[df['unique_studies'] >= 10])} groups have adequate sample sizes")
        
        return "\n".join(insights)
    
    def generate_full_report(self, output_path: str = None) -> str:
        """Generate complete user-friendly report."""
        report = []
        
        # Executive summary
        report.append(self.generate_executive_summary())
        
        # File explanations
        report.append(self.explain_file_meanings())
        
        # Detailed analyses
        report.append(self.explain_risk_factors())
        report.append(self.explain_treatments())
        report.append(self.explain_outcomes())
        
        # Key insights
        report.append(self.generate_key_insights())
        
        # Footer
        report.append("\n" + "=" * 70)
        report.append("📧 For questions about this analysis, refer to the README.md")
        report.append("=" * 70)
        
        full_report = "\n".join(report)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(full_report)
            print(f"📄 Report saved to: {output_path}")
        
        return full_report


def main():
    """Generate summary report."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python summary_report.py <tables_dir> [output_file]")
        sys.exit(1)
    
    tables_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    generator = SummaryReportGenerator(tables_dir)
    report = generator.generate_full_report(output_file)
    
    # Always print to console
    print(report)


if __name__ == "__main__":
    main()