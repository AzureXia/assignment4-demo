"""
Final Visualization Module with Clean Labels
Fixes truncated text and removes redundant categories.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set professional style
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11


class FinalPlotter:
    """Creates final plots with clean, readable labels."""
    
    def __init__(self, output_dir: str):
        """Initialize plotter."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_risk_factor_name(self, text: str) -> str:
        """Clean risk factor names - remove redundant triggers/risk factors."""
        if pd.isna(text):
            return "Unspecified"
        
        text_clean = str(text).strip()
        
        # Remove common prefixes and suffixes
        patterns_to_remove = [
            r'^/Triggers/Risk Factors\*\*:\s*',
            r'^Triggers/Risk Factors\*\*:\s*', 
            r'^/Triggers\*\*:\s*',
            r'^Triggers\*\*:\s*',
            r'^Risk Factors\*\*:\s*',
            r'^/Risk Factors\*\*:\s*',
            r'^\*\*\s*',
            r'\*\*$',
            r'^,\s*',
            r'^\"\s*',
            r'\s*\"$'
        ]
        
        for pattern in patterns_to_remove:
            text_clean = re.sub(pattern, '', text_clean, flags=re.IGNORECASE)
        
        text_clean = text_clean.strip()
        
        # If still too long or generic, categorize
        if len(text_clean) > 50 or text_clean.lower() in ['', 'triggers', 'risk factors', 'various', 'multiple']:
            # Try to extract key concepts
            if 'stress' in text_clean.lower():
                return 'Stress-related factors'
            elif 'anxiety' in text_clean.lower():
                return 'Anxiety-related factors'
            elif 'depression' in text_clean.lower():
                return 'Depression-related factors'
            elif 'social' in text_clean.lower():
                return 'Social factors'
            elif 'trauma' in text_clean.lower():
                return 'Trauma-related factors'
            elif 'family' in text_clean.lower() or 'parent' in text_clean.lower():
                return 'Family factors'
            elif 'economic' in text_clean.lower() or 'financial' in text_clean.lower():
                return 'Economic factors'
            else:
                return 'Other factors'
        
        # Limit to reasonable length for display
        if len(text_clean) > 35:
            text_clean = text_clean[:35] + '...'
        
        return text_clean if text_clean else "Unspecified"
    
    def clean_symptom_name(self, text: str) -> str:
        """Clean symptom names for better display."""
        if pd.isna(text):
            return "Unspecified"
        
        text_clean = str(text).strip()
        
        # If it's too long (abstract snippet), try to extract key concepts
        if len(text_clean) > 60:
            # Look for key symptom terms
            if 'depression' in text_clean.lower() or 'depressive' in text_clean.lower():
                return 'Depressive symptoms'
            elif 'anxiety' in text_clean.lower() or 'anxious' in text_clean.lower():
                return 'Anxiety symptoms'
            elif 'mood' in text_clean.lower():
                return 'Mood symptoms'
            elif 'cognitive' in text_clean.lower() or 'memory' in text_clean.lower():
                return 'Cognitive symptoms'
            elif 'behavioral' in text_clean.lower() or 'behavior' in text_clean.lower():
                return 'Behavioral symptoms'
            elif 'physical' in text_clean.lower() or 'somatic' in text_clean.lower():
                return 'Physical symptoms'
            elif 'sleep' in text_clean.lower():
                return 'Sleep symptoms'
            elif 'fatigue' in text_clean.lower() or 'energy' in text_clean.lower():
                return 'Fatigue/Energy symptoms'
            else:
                return 'Other symptoms'
        
        # If reasonable length, clean it up
        if len(text_clean) > 30:
            text_clean = text_clean[:30] + '...'
        
        return text_clean if text_clean else "Unspecified"
    
    def create_final_stratum_overview(self, stratum_summary: pd.DataFrame):
        """Create stratum overview with clear labels."""
        logger.info("Creating final stratum overview")
        
        if stratum_summary.empty:
            return
        
        # Take top 15 for better readability
        top_strata = stratum_summary.nlargest(15, 'unique_studies')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
        
        # Clean stratum labels for better display
        clean_labels = []
        for label in top_strata['stratum_id']:
            clean_label = str(label).replace('_', ' ').title()
            if len(clean_label) > 25:
                clean_label = clean_label[:25] + '...'
            clean_labels.append(clean_label)
        
        # Plot 1: Unique Studies
        colors1 = plt.cm.Blues(np.linspace(0.4, 0.9, len(top_strata)))
        bars1 = ax1.barh(range(len(top_strata)), top_strata['unique_studies'], color=colors1)
        ax1.set_yticks(range(len(top_strata)))
        ax1.set_yticklabels(clean_labels, fontsize=11)
        ax1.set_xlabel('Number of Unique Research Papers', fontweight='bold', fontsize=12)
        ax1.set_title('Unique Studies per Population Group\n(Each paper counted once)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Plot 2: Total Records
        colors2 = plt.cm.Oranges(np.linspace(0.4, 0.9, len(top_strata)))
        bars2 = ax2.barh(range(len(top_strata)), top_strata['total_records'], color=colors2)
        ax2.set_yticks(range(len(top_strata)))
        ax2.set_yticklabels(clean_labels, fontsize=11)
        ax2.set_xlabel('Total Analysis Records', fontweight='bold', fontsize=12)
        ax2.set_title('Total Data Records per Population Group\n(Multiple records per paper possible)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold', fontsize=10)
        
        plt.suptitle('Population Groups Research Coverage Analysis', 
                    fontsize=18, fontweight='bold', y=0.95)
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        plt.savefig(f"{self.output_dir}/stratum_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Final stratum overview saved")
    
    def create_final_risk_factors_chart(self, risk_factors_df: pd.DataFrame):
        """Create risk factors chart with cleaned categories."""
        logger.info("Creating final risk factors chart")
        
        if risk_factors_df.empty:
            return
        
        # Clean risk factor names
        risk_factors_df = risk_factors_df.copy()
        risk_factors_df['clean_risk_factor'] = risk_factors_df['risk_factor'].apply(self.clean_risk_factor_name)
        
        # Filter out unspecified
        meaningful_factors = risk_factors_df[risk_factors_df['clean_risk_factor'] != 'Unspecified']
        
        if meaningful_factors.empty:
            return
        
        # Get top strata
        top_strata = meaningful_factors.groupby('stratum_id')['total_studies'].first().nlargest(6).index
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()
        
        for i, stratum in enumerate(top_strata):
            if i >= 6:
                break
                
            stratum_data = meaningful_factors[meaningful_factors['stratum_id'] == stratum]
            top_factors = stratum_data.nlargest(6, 'percentage')
            
            if len(top_factors) == 0:
                axes[i].text(0.5, 0.5, 'No significant\nrisk factors', 
                           ha='center', va='center', transform=axes[i].transAxes, fontsize=12)
                axes[i].set_title(f'{stratum}'.replace('_', ' ').title(), fontsize=13, fontweight='bold')
                continue
            
            ax = axes[i]
            colors = plt.cm.Set3(np.linspace(0, 1, len(top_factors)))
            bars = ax.barh(range(len(top_factors)), top_factors['percentage'], color=colors)
            ax.set_yticks(range(len(top_factors)))
            ax.set_yticklabels(top_factors['clean_risk_factor'], fontsize=10)
            ax.set_xlabel('Percentage of Studies', fontweight='bold', fontsize=11)
            ax.set_title(f'{stratum}'.replace('_', ' ').title(), fontsize=13, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add percentage labels
            for j, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}%', ha='left', va='center', fontsize=9, fontweight='bold')
        
        # Hide unused subplots
        for i in range(len(top_strata), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Risk Factors by Population Group', fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.savefig(f"{self.output_dir}/top_risk_factors.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Final risk factors chart saved")
    
    def create_final_symptoms_comparison(self, symptoms_df: pd.DataFrame):
        """Create symptoms comparison with clean labels."""
        logger.info("Creating final symptoms comparison")
        
        if symptoms_df.empty:
            return
        
        # Clean symptom names
        symptoms_df = symptoms_df.copy()
        symptoms_df['clean_symptom'] = symptoms_df['symptom'].apply(self.clean_symptom_name)
        
        # Filter meaningful symptoms
        meaningful_symptoms = symptoms_df[symptoms_df['clean_symptom'] != 'Unspecified']
        
        if meaningful_symptoms.empty:
            return
        
        # Get top symptoms and strata
        top_symptoms = meaningful_symptoms.groupby('clean_symptom')['count'].sum().nlargest(8).index
        top_strata = meaningful_symptoms.groupby('stratum_id')['total_studies'].first().nlargest(8).index
        
        # Create comparison data
        comparison_data = []
        for stratum in top_strata:
            stratum_clean = stratum.replace('_', ' ').title()
            if len(stratum_clean) > 20:
                stratum_clean = stratum_clean[:20] + '...'
            
            stratum_data = meaningful_symptoms[meaningful_symptoms['stratum_id'] == stratum]
            for symptom in top_symptoms:
                symptom_data = stratum_data[stratum_data['clean_symptom'] == symptom]
                percentage = symptom_data['percentage'].sum() if not symptom_data.empty else 0
                comparison_data.append({
                    'stratum': stratum_clean,
                    'symptom': symptom,
                    'percentage': percentage
                })
        
        if not comparison_data:
            return
        
        comp_df = pd.DataFrame(comparison_data)
        heatmap_data = comp_df.pivot(index='stratum', columns='symptom', values='percentage')
        heatmap_data = heatmap_data.fillna(0)
        
        plt.figure(figsize=(14, 8))
        
        sns.heatmap(heatmap_data, 
                   annot=True, 
                   fmt='.1f', 
                   cmap='YlOrRd', 
                   cbar_kws={'label': 'Percentage of Studies'},
                   linewidths=0.5)
        
        plt.title('Symptom Categories Across Population Groups', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Symptom Categories', fontweight='bold', fontsize=12)
        plt.ylabel('Population Groups', fontweight='bold', fontsize=12)
        plt.xticks(rotation=35, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/symptoms_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Final symptoms comparison saved")
    
    def create_all_final_plots(self, analysis_results: Dict[str, pd.DataFrame], normalized_df: pd.DataFrame):
        """Create all final plots with clean labels."""
        logger.info("Creating all final visualizations")
        
        if 'stratum_summary' in analysis_results:
            self.create_final_stratum_overview(analysis_results['stratum_summary'])
        
        if 'risk_factors' in analysis_results:
            self.create_final_risk_factors_chart(analysis_results['risk_factors'])
        
        if 'symptoms' in analysis_results:
            self.create_final_symptoms_comparison(analysis_results['symptoms'])
        
        logger.info("All final plots completed")


def main():
    """Test final plotting."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python final_plots.py <tables_dir> <output_dir>")
        sys.exit(1)
    
    tables_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Load analysis results
    analysis_results = {}
    result_files = [
        'stratum_summary_by_stratum.csv',
        'risk_factors_by_stratum.csv', 
        'symptoms_by_stratum.csv'
    ]
    
    for file in result_files:
        file_path = f"{tables_dir}/{file}"
        if os.path.exists(file_path):
            key = file.replace('_by_stratum.csv', '')
            analysis_results[key] = pd.read_csv(file_path)
            print(f"Loaded {key}: {len(analysis_results[key])} rows")
    
    # Create final plots
    plotter = FinalPlotter(output_dir)
    plotter.create_all_final_plots(analysis_results, pd.DataFrame())
    
    print(f"✅ Final clean plots created in {output_dir}")


if __name__ == "__main__":
    main()