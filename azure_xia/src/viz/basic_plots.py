"""
Basic Visualization Module
Creates essential plots for population-stratum analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
plt.style.use('default')
sns.set_palette("husl")


class BasicPlotter:
    """Creates basic plots for stratum analysis."""
    
    def __init__(self, output_dir: str):
        """Initialize plotter with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_stratum_overview(self, stratum_summary: pd.DataFrame):
        """Create overview of all strata."""
        logger.info("Creating stratum overview plot")
        
        if stratum_summary.empty:
            logger.warning("No stratum summary data available")
            return
        
        # Sort by unique studies count
        stratum_summary = stratum_summary.sort_values('unique_studies', ascending=True)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
        
        # Studies per stratum
        ax1.barh(range(len(stratum_summary)), stratum_summary['unique_studies'])
        ax1.set_yticks(range(len(stratum_summary)))
        ax1.set_yticklabels(stratum_summary['stratum_id'], fontsize=8)
        ax1.set_xlabel('Number of Unique Studies')
        ax1.set_title('Studies per Population Stratum')
        ax1.grid(axis='x', alpha=0.3)
        
        # Records per stratum
        ax2.barh(range(len(stratum_summary)), stratum_summary['total_records'])
        ax2.set_yticks(range(len(stratum_summary)))
        ax2.set_yticklabels(stratum_summary['stratum_id'], fontsize=8)
        ax2.set_xlabel('Number of Records')
        ax2.set_title('Records per Population Stratum')
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/stratum_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved stratum overview to {self.output_dir}/stratum_overview.png")
    
    def create_top_risk_factors_chart(self, risk_factors_df: pd.DataFrame, top_n: int = 10):
        """Create bar chart of top risk factors by stratum."""
        logger.info(f"Creating top {top_n} risk factors chart")
        
        if risk_factors_df.empty:
            logger.warning("No risk factors data available")
            return
        
        # Get top strata by study count
        top_strata = risk_factors_df.groupby('stratum_id')['total_studies'].first().nlargest(5).index
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, stratum in enumerate(top_strata):
            if i >= 6:
                break
                
            stratum_data = risk_factors_df[risk_factors_df['stratum_id'] == stratum]
            top_factors = stratum_data.nlargest(top_n, 'percentage')
            
            ax = axes[i]
            bars = ax.barh(range(len(top_factors)), top_factors['percentage'])
            ax.set_yticks(range(len(top_factors)))
            ax.set_yticklabels([f[:30] + '...' if len(f) > 30 else f for f in top_factors['risk_factor']], fontsize=8)
            ax.set_xlabel('Percentage of Studies')
            ax.set_title(f'Top Risk Factors\n{stratum}', fontsize=10)
            ax.grid(axis='x', alpha=0.3)
            
            # Add percentage labels
            for j, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}%', ha='left', va='center', fontsize=8)
        
        # Hide unused subplots
        for i in range(len(top_strata), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/top_risk_factors.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved top risk factors chart to {self.output_dir}/top_risk_factors.png")
    
    def create_treatment_outcomes_heatmap(self, treatment_outcomes_df: pd.DataFrame):
        """Create heatmap of treatment outcomes."""
        logger.info("Creating treatment-outcomes heatmap")
        
        if treatment_outcomes_df.empty:
            logger.warning("No treatment outcomes data available")
            return
        
        # Create pivot table
        pivot_data = treatment_outcomes_df.groupby(['treatment_category', 'outcome_direction'])['count'].sum().reset_index()
        heatmap_data = pivot_data.pivot(index='treatment_category', columns='outcome_direction', values='count')
        heatmap_data = heatmap_data.fillna(0)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd', cbar_kws={'label': 'Study Count'})
        plt.title('Treatment Categories vs Outcome Directions\n(All Strata Combined)')
        plt.xlabel('Outcome Direction')
        plt.ylabel('Treatment Category')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/treatment_outcomes_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved treatment outcomes heatmap to {self.output_dir}/treatment_outcomes_heatmap.png")
    
    def create_symptoms_comparison(self, symptoms_df: pd.DataFrame, top_n: int = 8):
        """Create comparison of symptoms across strata."""
        logger.info("Creating symptoms comparison chart")
        
        if symptoms_df.empty:
            logger.warning("No symptoms data available")
            return
        
        # Get top symptoms overall
        top_symptoms = symptoms_df.groupby('symptom')['count'].sum().nlargest(top_n).index
        
        # Get top strata
        top_strata = symptoms_df.groupby('stratum_id')['total_studies'].first().nlargest(5).index
        
        # Create comparison data
        comparison_data = []
        for stratum in top_strata:
            stratum_data = symptoms_df[symptoms_df['stratum_id'] == stratum]
            for symptom in top_symptoms:
                symptom_data = stratum_data[stratum_data['symptom'] == symptom]
                percentage = symptom_data['percentage'].sum() if not symptom_data.empty else 0
                comparison_data.append({
                    'stratum': stratum,
                    'symptom': symptom,
                    'percentage': percentage
                })
        
        if not comparison_data:
            logger.warning("No comparison data available")
            return
        
        comp_df = pd.DataFrame(comparison_data)
        heatmap_data = comp_df.pivot(index='stratum', columns='symptom', values='percentage')
        heatmap_data = heatmap_data.fillna(0)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='Blues', cbar_kws={'label': 'Percentage'})
        plt.title('Symptom Prevalence Across Population Strata')
        plt.xlabel('Symptoms')
        plt.ylabel('Population Strata')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/symptoms_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved symptoms comparison to {self.output_dir}/symptoms_comparison.png")
    
    def create_interactive_sankey(self, normalized_df: pd.DataFrame):
        """Create interactive Sankey diagram for population -> treatment -> outcome flow."""
        logger.info("Creating interactive Sankey diagram")
        
        if normalized_df.empty:
            logger.warning("No normalized data available")
            return
        
        # Simplify for visualization
        df_sample = normalized_df.sample(min(200, len(normalized_df)))  # Sample for performance
        
        # Create nodes
        age_groups = df_sample['age_group'].unique()
        treatments = df_sample['treatment_category'].unique()
        outcomes = df_sample['outcome_direction'].unique()
        
        # Create node labels and indices
        all_nodes = []
        node_colors = []
        
        # Age groups (blue)
        for ag in age_groups:
            all_nodes.append(f"Age: {ag}")
            node_colors.append("lightblue")
        
        # Treatments (green)
        for tr in treatments:
            all_nodes.append(f"Treatment: {tr}")
            node_colors.append("lightgreen")
        
        # Outcomes (orange)
        for oc in outcomes:
            all_nodes.append(f"Outcome: {oc}")
            node_colors.append("lightsalmon")
        
        # Create flows
        flows = []
        
        # Age -> Treatment flows
        for i, ag in enumerate(age_groups):
            for j, tr in enumerate(treatments):
                count = len(df_sample[(df_sample['age_group'] == ag) & 
                                    (df_sample['treatment_category'] == tr)])
                if count > 0:
                    flows.append({
                        'source': i,
                        'target': len(age_groups) + j,
                        'value': count
                    })
        
        # Treatment -> Outcome flows
        for i, tr in enumerate(treatments):
            for j, oc in enumerate(outcomes):
                count = len(df_sample[(df_sample['treatment_category'] == tr) & 
                                    (df_sample['outcome_direction'] == oc)])
                if count > 0:
                    flows.append({
                        'source': len(age_groups) + i,
                        'target': len(age_groups) + len(treatments) + j,
                        'value': count
                    })
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=node_colors
            ),
            link=dict(
                source=[f['source'] for f in flows],
                target=[f['target'] for f in flows],
                value=[f['value'] for f in flows]
            )
        )])
        
        fig.update_layout(
            title_text="Population → Treatment → Outcome Flow",
            font_size=10,
            height=600
        )
        
        fig.write_html(f"{self.output_dir}/sankey_flow.html")
        logger.info(f"Saved Sankey diagram to {self.output_dir}/sankey_flow.html")
    
    def create_all_visualizations(self, analysis_results: Dict[str, pd.DataFrame], normalized_df: pd.DataFrame):
        """Create all visualizations."""
        logger.info("Creating all visualizations")
        
        # Stratum overview
        if 'stratum_summary' in analysis_results:
            self.create_stratum_overview(analysis_results['stratum_summary'])
        
        # Risk factors
        if 'risk_factors' in analysis_results:
            self.create_top_risk_factors_chart(analysis_results['risk_factors'])
        
        # Treatment outcomes
        if 'treatment_outcomes' in analysis_results:
            self.create_treatment_outcomes_heatmap(analysis_results['treatment_outcomes'])
        
        # Symptoms comparison
        if 'symptoms' in analysis_results:
            self.create_symptoms_comparison(analysis_results['symptoms'])
        
        # Sankey diagram
        self.create_interactive_sankey(normalized_df)
        
        logger.info("All visualizations completed")


def main():
    """Main function for testing visualization."""
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python basic_plots.py <tables_dir> <normalized_csv> <output_dir>")
        sys.exit(1)
    
    tables_dir = sys.argv[1]
    normalized_csv = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Load analysis results
    analysis_results = {}
    result_files = [
        'stratum_summary_by_stratum.csv',
        'risk_factors_by_stratum.csv',
        'treatment_outcomes_by_stratum.csv',
        'symptoms_by_stratum.csv'
    ]
    
    for file in result_files:
        file_path = f"{tables_dir}/{file}"
        if os.path.exists(file_path):
            key = file.replace('_by_stratum.csv', '')
            analysis_results[key] = pd.read_csv(file_path)
    
    # Load normalized data
    normalized_df = pd.read_csv(normalized_csv)
    
    # Create visualizations
    plotter = BasicPlotter(output_dir)
    plotter.create_all_visualizations(analysis_results, normalized_df)
    
    print(f"Visualizations created in {output_dir}")


if __name__ == "__main__":
    main()