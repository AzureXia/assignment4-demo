"""
Enhanced Visualization Module
Creates clear, professional plots with proper labels and categorization.
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

# Set enhanced style
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10


class EnhancedPlotter:
    """Creates enhanced plots with clear labels and categories."""
    
    def __init__(self, output_dir: str):
        """Initialize plotter with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_clear_stratum_overview(self, stratum_summary: pd.DataFrame):
        """Create clear overview explaining studies vs records."""
        logger.info("Creating enhanced stratum overview plot")
        
        if stratum_summary.empty:
            logger.warning("No stratum summary data available")
            return
        
        # Sort by unique studies count and take top 12 for readability
        top_strata = stratum_summary.nlargest(12, 'unique_studies')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
        
        # Plot 1: Studies per stratum (UNIQUE PAPERS)
        colors1 = plt.cm.Blues(np.linspace(0.4, 0.8, len(top_strata)))
        bars1 = ax1.barh(range(len(top_strata)), top_strata['unique_studies'], color=colors1)
        ax1.set_yticks(range(len(top_strata)))
        
        # Clean up stratum labels for better readability
        clean_labels = []
        for label in top_strata['stratum_id']:
            if len(str(label)) > 35:
                clean_label = str(label)[:35] + '...'
            else:
                clean_label = str(label)
            clean_labels.append(clean_label)
        
        ax1.set_yticklabels(clean_labels, fontsize=10)
        ax1.set_xlabel('Number of Unique Research Papers', fontweight='bold')
        ax1.set_title('Unique Studies per Population Group\n(Each paper counts once)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Plot 2: Total records per stratum (DATA POINTS)
        colors2 = plt.cm.Oranges(np.linspace(0.4, 0.8, len(top_strata)))
        bars2 = ax2.barh(range(len(top_strata)), top_strata['total_records'], color=colors2)
        ax2.set_yticks(range(len(top_strata)))
        ax2.set_yticklabels(clean_labels, fontsize=10)
        ax2.set_xlabel('Total Analysis Records', fontweight='bold')
        ax2.set_title('Total Data Records per Population Group\n(Multiple records per paper possible)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold', fontsize=10)
        
        plt.suptitle('Population Groups: Research Coverage Analysis', 
                    fontsize=16, fontweight='bold', y=0.95)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.savefig(f"{self.output_dir}/stratum_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved enhanced stratum overview to {self.output_dir}/stratum_overview.png")
    
    def create_clear_risk_factors_chart(self, risk_factors_df: pd.DataFrame, top_n: int = 8):
        """Create clear risk factors chart with proper categories."""
        logger.info(f"Creating clear risk factors chart")
        
        if risk_factors_df.empty:
            logger.warning("No risk factors data available")
            return
        
        # Get top strata by study count
        top_strata = risk_factors_df.groupby('stratum_id')['total_studies'].first().nlargest(6).index
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, stratum in enumerate(top_strata):
            if i >= 6:
                break
                
            stratum_data = risk_factors_df[risk_factors_df['stratum_id'] == stratum]
            top_factors = stratum_data.nlargest(top_n, 'percentage')
            
            if len(top_factors) == 0:
                axes[i].text(0.5, 0.5, 'No significant\nrisk factors', 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(f'{stratum}', fontsize=12, fontweight='bold')
                continue
            
            ax = axes[i]
            colors = plt.cm.Set3(np.linspace(0, 1, len(top_factors)))
            bars = ax.barh(range(len(top_factors)), top_factors['percentage'], color=colors)
            ax.set_yticks(range(len(top_factors)))
            
            # Clean risk factor names for display
            clean_factors = []
            for factor in top_factors['risk_factor']:
                if len(str(factor)) > 20:
                    clean_factor = str(factor).replace('_', ' ').title()[:20] + '...'
                else:
                    clean_factor = str(factor).replace('_', ' ').title()
                clean_factors.append(clean_factor)
            
            ax.set_yticklabels(clean_factors, fontsize=9)
            ax.set_xlabel('% of Studies', fontweight='bold')
            ax.set_title(f'Risk Factors: {stratum}', fontsize=11, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add percentage labels
            for j, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}%', ha='left', va='center', fontsize=9, fontweight='bold')
        
        # Hide unused subplots
        for i in range(len(top_strata), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Risk Factors by Population Group\n(Categorized and Cleaned)', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        plt.savefig(f"{self.output_dir}/top_risk_factors.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved clear risk factors chart to {self.output_dir}/top_risk_factors.png")
    
    def create_clear_symptoms_comparison(self, symptoms_df: pd.DataFrame, top_n: int = 8):
        """Create clear symptoms comparison with proper categories."""
        logger.info("Creating clear symptoms comparison chart")
        
        if symptoms_df.empty:
            logger.warning("No symptoms data available")
            return
        
        # Get top symptoms overall (cleaned)
        top_symptoms = symptoms_df.groupby('symptom')['study_count'].sum().nlargest(top_n).index
        
        # Get top strata
        top_strata = symptoms_df.groupby('stratum_id')['total_studies'].first().nlargest(6).index
        
        # Create comparison data
        comparison_data = []
        for stratum in top_strata:
            stratum_data = symptoms_df[symptoms_df['stratum_id'] == stratum]
            for symptom in top_symptoms:
                symptom_data = stratum_data[stratum_data['symptom'] == symptom]
                percentage = symptom_data['percentage'].sum() if not symptom_data.empty else 0
                comparison_data.append({
                    'stratum': stratum[:25] + '...' if len(stratum) > 25 else stratum,
                    'symptom': symptom.replace('_', ' ').title(),
                    'percentage': percentage
                })
        
        if not comparison_data:
            logger.warning("No symptom comparison data available")
            return
        
        comp_df = pd.DataFrame(comparison_data)
        heatmap_data = comp_df.pivot(index='stratum', columns='symptom', values='percentage')
        heatmap_data = heatmap_data.fillna(0)
        
        plt.figure(figsize=(14, 8))
        
        # Create heatmap with better colors
        sns.heatmap(heatmap_data, 
                   annot=True, 
                   fmt='.1f', 
                   cmap='YlOrRd', 
                   cbar_kws={'label': 'Percentage of Studies'},
                   linewidths=0.5,
                   square=False)
        
        plt.title('Symptom Categories Across Population Groups\n(Cleaned and Categorized)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Symptom Categories', fontweight='bold')
        plt.ylabel('Population Groups', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/symptoms_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved clear symptoms comparison to {self.output_dir}/symptoms_comparison.png")
    
    def create_enhanced_sankey(self, normalized_df: pd.DataFrame):
        """Create enhanced Sankey diagram with specific, meaningful flows."""
        logger.info("Creating enhanced Sankey diagram")
        
        if normalized_df.empty:
            logger.warning("No normalized data available")
            return
        
        # Filter for meaningful, specific entries only
        meaningful_df = normalized_df[
            (~normalized_df['age_group'].str.contains('unspecified|other|mixed', case=False, na=False)) &
            (~normalized_df['treatment_category'].str.contains('unspecified|other|various', case=False, na=False)) &
            (~normalized_df['outcome_direction'].str.contains('unspecified|unclear', case=False, na=False))
        ].copy()
        
        # Take a larger sample for more interesting flows
        if len(meaningful_df) > 150:
            meaningful_df = meaningful_df.sample(150, random_state=42)
        
        logger.info(f"Using {len(meaningful_df)} meaningful records for Sankey")
        
        # Clean up categories for better display
        meaningful_df['clean_age'] = meaningful_df['age_group'].str.title()
        meaningful_df['clean_treatment'] = meaningful_df['treatment_category'].apply(self.clean_treatment_for_sankey)
        meaningful_df['clean_outcome'] = meaningful_df['outcome_direction'].str.title()
        
        # Create nodes
        age_groups = meaningful_df['clean_age'].unique()
        treatments = meaningful_df['clean_treatment'].unique()  
        outcomes = meaningful_df['clean_outcome'].unique()
        
        # Create node labels and colors
        all_nodes = []
        node_colors = []
        
        # Age groups (blue tones)
        for ag in age_groups:
            all_nodes.append(f"👥 {ag}")
            node_colors.append("rgba(52, 152, 219, 0.8)")
        
        # Treatments (green tones)
        for tr in treatments:
            all_nodes.append(f"🏥 {tr}")
            node_colors.append("rgba(46, 204, 113, 0.8)")
        
        # Outcomes (orange tones)
        for oc in outcomes:
            all_nodes.append(f"📈 {oc}")
            node_colors.append("rgba(230, 126, 34, 0.8)")
        
        # Create flows with meaningful thresholds
        flows = []
        
        # Age -> Treatment flows
        for i, ag in enumerate(age_groups):
            for j, tr in enumerate(treatments):
                count = len(meaningful_df[(meaningful_df['clean_age'] == ag) & 
                                        (meaningful_df['clean_treatment'] == tr)])
                if count >= 2:  # Only show meaningful flows
                    flows.append({
                        'source': i,
                        'target': len(age_groups) + j,
                        'value': count
                    })
        
        # Treatment -> Outcome flows
        for i, tr in enumerate(treatments):
            for j, oc in enumerate(outcomes):
                count = len(meaningful_df[(meaningful_df['clean_treatment'] == tr) & 
                                        (meaningful_df['clean_outcome'] == oc)])
                if count >= 2:  # Only show meaningful flows
                    flows.append({
                        'source': len(age_groups) + i,
                        'target': len(age_groups) + len(treatments) + j,
                        'value': count
                    })
        
        if not flows:
            logger.warning("No meaningful flows found for Sankey diagram")
            return
        
        # Create enhanced Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="black", width=0.8),
                label=all_nodes,
                color=node_colors
            ),
            link=dict(
                source=[f['source'] for f in flows],
                target=[f['target'] for f in flows],
                value=[f['value'] for f in flows],
                color="rgba(128, 128, 128, 0.4)"
            )
        )])
        
        fig.update_layout(
            title=dict(
                text="Mental Health Treatment Pathways<br><sub>Population → Treatment → Outcome (Specific Studies Only)</sub>",
                font=dict(size=18, family="Arial Black")
            ),
            font_size=12,
            height=700,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        fig.write_html(f"{self.output_dir}/sankey_flow.html")
        logger.info(f"Saved enhanced Sankey diagram to {self.output_dir}/sankey_flow.html")
    
    def clean_treatment_for_sankey(self, treatment: str) -> str:
        """Clean treatment names specifically for Sankey display."""
        if pd.isna(treatment):
            return "Unspecified"
        
        treatment_clean = str(treatment).strip()
        
        # Map to cleaner names
        mapping = {
            'cognitive behavioral therapy': 'CBT',
            'acceptance and commitment therapy': 'ACT',
            'dialectical behavior therapy': 'DBT',
            'psychotherapy': 'Psychotherapy',
            'mindfulness': 'Mindfulness',
            'exercise': 'Exercise Therapy',
            'medication': 'Medication'
        }
        
        treatment_lower = treatment_clean.lower()
        for key, value in mapping.items():
            if key in treatment_lower:
                return value
        
        # If no mapping, clean it up
        if len(treatment_clean) > 15:
            return treatment_clean[:15] + "..."
        
        return treatment_clean.title()
    
    def create_treatment_outcomes_heatmap(self, treatment_outcomes_df: pd.DataFrame):
        """Create clear treatment outcomes heatmap."""
        logger.info("Creating enhanced treatment-outcomes heatmap")
        
        if treatment_outcomes_df.empty:
            logger.warning("No treatment outcomes data available")
            return
        
        # Create pivot table with cleaned names
        pivot_data = treatment_outcomes_df.groupby(['treatment_category', 'outcome_direction'])['count'].sum().reset_index()
        heatmap_data = pivot_data.pivot(index='treatment_category', columns='outcome_direction', values='count')
        heatmap_data = heatmap_data.fillna(0)
        
        # Clean up labels
        heatmap_data.index = [idx.replace('_', ' ').title() for idx in heatmap_data.index]
        heatmap_data.columns = [col.replace('_', ' ').title() for col in heatmap_data.columns]
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, 
                   annot=True, 
                   fmt='g', 
                   cmap='RdYlBu_r', 
                   cbar_kws={'label': 'Number of Studies'},
                   linewidths=0.5)
        
        plt.title('Treatment Categories vs Outcome Directions\n(All Population Groups Combined)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Outcome Direction', fontweight='bold')
        plt.ylabel('Treatment Category', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/treatment_outcomes_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved enhanced treatment outcomes heatmap to {self.output_dir}/treatment_outcomes_heatmap.png")
    
    def create_all_enhanced_visualizations(self, analysis_results: Dict[str, pd.DataFrame], normalized_df: pd.DataFrame):
        """Create all enhanced visualizations."""
        logger.info("Creating all enhanced visualizations")
        
        # Stratum overview
        if 'stratum_summary' in analysis_results:
            self.create_clear_stratum_overview(analysis_results['stratum_summary'])
        
        # Risk factors
        if 'risk_factors' in analysis_results:
            self.create_clear_risk_factors_chart(analysis_results['risk_factors'])
        
        # Treatment outcomes
        if 'treatment_outcomes' in analysis_results:
            self.create_treatment_outcomes_heatmap(analysis_results['treatment_outcomes'])
        
        # Symptoms comparison
        if 'symptoms' in analysis_results:
            self.create_clear_symptoms_comparison(analysis_results['symptoms'])
        
        # Enhanced Sankey diagram
        self.create_enhanced_sankey(normalized_df)
        
        logger.info("All enhanced visualizations completed")


def main():
    """Main function for testing enhanced visualization."""
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python enhanced_plots.py <tables_dir> <normalized_csv> <output_dir>")
        sys.exit(1)
    
    tables_dir = sys.argv[1]
    normalized_csv = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Load analysis results
    analysis_results = {}
    result_files = [
        'stratum_summary_by_stratum.csv',
        'risk_factors_by_stratum.csv',
        'treatments_by_stratum.csv',
        'treatment_outcomes_by_stratum.csv',
        'symptoms_by_stratum.csv'
    ]
    
    for file in result_files:
        file_path = f"{tables_dir}/{file}"
        if os.path.exists(file_path):
            key = file.replace('_by_stratum.csv', '')
            analysis_results[key] = pd.read_csv(file_path)
            print(f"Loaded {key}: {len(analysis_results[key])} rows")
    
    # Load normalized data
    normalized_df = pd.read_csv(normalized_csv)
    print(f"Loaded normalized data: {len(normalized_df)} rows")
    
    # Create enhanced visualizations
    plotter = EnhancedPlotter(output_dir)
    plotter.create_all_enhanced_visualizations(analysis_results, normalized_df)
    
    print(f"✨ Enhanced visualizations created in {output_dir}")


if __name__ == "__main__":
    main()