"""
Improved Sankey Diagram with More Treatment Categories
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedSankeyGenerator:
    """Creates Sankey with more treatment diversity."""
    
    def __init__(self):
        """Initialize Sankey generator."""
        pass
    
    def create_comprehensive_sankey(self, normalized_df: pd.DataFrame, output_path: str):
        """Create Sankey with comprehensive treatment categories."""
        logger.info("Creating comprehensive Sankey diagram")
        
        if normalized_df.empty:
            logger.warning("No normalized data available")
            return
        
        # Filter for meaningful entries but keep more treatments
        meaningful_df = normalized_df[
            (~normalized_df['age_group'].str.contains('unspecified', case=False, na=False)) &
            (~normalized_df['treatment_category'].str.contains('unspecified', case=False, na=False))
        ].copy()
        
        # Take a good sample size
        if len(meaningful_df) > 100:
            meaningful_df = meaningful_df.sample(100, random_state=42)
        
        logger.info(f"Using {len(meaningful_df)} records for comprehensive Sankey")
        
        # Clean up categories but keep more diversity
        meaningful_df['clean_age'] = meaningful_df['age_group'].str.replace('_', ' ').str.title()
        meaningful_df['clean_treatment'] = meaningful_df['treatment_category'].apply(self.preserve_treatment_diversity)
        meaningful_df['clean_outcome'] = meaningful_df['outcome_direction'].str.replace('_', ' ').str.title()
        
        # Get unique categories
        age_groups = meaningful_df['clean_age'].unique()
        treatments = meaningful_df['clean_treatment'].unique()
        outcomes = meaningful_df['clean_outcome'].unique()
        
        logger.info(f"Categories: {len(age_groups)} ages, {len(treatments)} treatments, {len(outcomes)} outcomes")
        
        # Create node labels with emojis
        all_nodes = []
        node_colors = []
        
        # Age groups (blue spectrum)
        for ag in age_groups:
            all_nodes.append(f"👥 {ag}")
            node_colors.append("rgba(52, 152, 219, 0.8)")
        
        # Treatments (green spectrum) - more variety
        treatment_colors = [
            "rgba(46, 204, 113, 0.8)",   # Green
            "rgba(26, 188, 156, 0.8)",   # Turquoise
            "rgba(22, 160, 133, 0.8)",   # Dark turquoise
            "rgba(39, 174, 96, 0.8)",    # Emerald
            "rgba(34, 153, 84, 0.8)",    # Dark green
            "rgba(115, 198, 182, 0.8)",  # Light green
            "rgba(72, 201, 176, 0.8)",   # Mint
            "rgba(16, 172, 132, 0.8)"    # Sea green
        ]
        
        for i, tr in enumerate(treatments):
            all_nodes.append(f"🏥 {tr}")
            color_idx = i % len(treatment_colors)
            node_colors.append(treatment_colors[color_idx])
        
        # Outcomes (orange spectrum)
        for oc in outcomes:
            all_nodes.append(f"📈 {oc}")
            node_colors.append("rgba(230, 126, 34, 0.8)")
        
        # Create flows with lower threshold to show more diversity
        flows = []
        
        # Age -> Treatment flows
        for i, ag in enumerate(age_groups):
            for j, tr in enumerate(treatments):
                count = len(meaningful_df[(meaningful_df['clean_age'] == ag) & 
                                        (meaningful_df['clean_treatment'] == tr)])
                if count >= 1:  # Lower threshold to show more flows
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
                if count >= 1:  # Lower threshold to show more flows
                    flows.append({
                        'source': len(age_groups) + i,
                        'target': len(age_groups) + len(treatments) + j,
                        'value': count
                    })
        
        logger.info(f"Created {len(flows)} flows for Sankey")
        
        if not flows:
            logger.warning("No flows found for Sankey diagram")
            return
        
        # Create enhanced Sankey with more treatments
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
                value=[f['value'] for f in flows],
                color="rgba(128, 128, 128, 0.3)"
            )
        )])
        
        fig.update_layout(
            title=dict(
                text="Mental Health Treatment Pathways<br><sub>Population Groups → Treatment Types → Outcomes</sub>",
                font=dict(size=16, family="Arial")
            ),
            font_size=10,
            height=600,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        fig.write_html(output_path)
        logger.info(f"Saved comprehensive Sankey to {output_path}")
    
    def preserve_treatment_diversity(self, treatment: str) -> str:
        """Keep more treatment diversity while cleaning."""
        if pd.isna(treatment):
            return "Other"
        
        treatment_clean = str(treatment).strip().lower()
        
        # Keep more specific categories
        if 'cbt' in treatment_clean or 'cognitive behavioral' in treatment_clean:
            return 'CBT'
        elif 'act' in treatment_clean or 'acceptance and commitment' in treatment_clean:
            return 'ACT'
        elif 'dbt' in treatment_clean or 'dialectical behavior' in treatment_clean:
            return 'DBT'
        elif 'mindfulness' in treatment_clean:
            return 'Mindfulness'
        elif 'meditation' in treatment_clean:
            return 'Meditation'
        elif 'psychotherapy' in treatment_clean:
            return 'Psychotherapy'
        elif 'therapy' in treatment_clean and 'group' in treatment_clean:
            return 'Group Therapy'
        elif 'therapy' in treatment_clean:
            return 'Individual Therapy'
        elif 'counseling' in treatment_clean:
            return 'Counseling'
        elif 'medication' in treatment_clean:
            return 'Medication'
        elif 'pharmacotherapy' in treatment_clean:
            return 'Pharmacotherapy'
        elif 'exercise' in treatment_clean:
            return 'Exercise Therapy'
        elif 'behavioral' in treatment_clean:
            return 'Behavioral'
        elif 'support' in treatment_clean:
            return 'Support Groups'
        else:
            # Keep some of the original if it's not too long
            original = str(treatment).strip().title()
            if len(original) <= 15:
                return original
            return 'Other'


def main():
    """Generate improved Sankey."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python improved_sankey.py <normalized_csv> <output_html>")
        sys.exit(1)
    
    normalized_csv = sys.argv[1]
    output_html = sys.argv[2]
    
    # Load data
    normalized_df = pd.read_csv(normalized_csv)
    print(f"Loaded {len(normalized_df)} normalized records")
    
    # Create improved Sankey
    generator = ImprovedSankeyGenerator()
    generator.create_comprehensive_sankey(normalized_df, output_html)
    
    print(f"✨ Improved Sankey created: {output_html}")


if __name__ == "__main__":
    main()