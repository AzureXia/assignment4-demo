#!/usr/bin/env python3
"""
Population-Stratum Analysis CLI
Main command-line interface for the mental health literature analysis system.
"""

import argparse
import sys
import logging
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prepare.gpt_output_splitter import GPTOutputSplitter
from prepare.normalize_labels import FieldNormalizer
from loaders.csv_loader import MentalHealthDataLoader
from analysis.aggregates import StratumAggregator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def split_fields_command(args):
    """Split GPT output fields."""
    logger.info(f"Splitting GPT output fields from {args.input}")
    
    import pandas as pd
    df = pd.read_csv(args.input)
    
    splitter = GPTOutputSplitter()
    processed_df = splitter.process_dataframe(df)
    splitter.save_processed_data(processed_df, args.output)
    
    print(f"✓ Field splitting complete. Output saved to {args.output}")


def load_data_command(args):
    """Load and validate data."""
    logger.info(f"Loading and validating data from {args.input}")
    
    loader = MentalHealthDataLoader()
    df = loader.load_data(args.input)
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


def normalize_command(args):
    """Normalize fields and convert to long format."""
    logger.info(f"Normalizing fields from {args.input}")
    
    import pandas as pd
    df = pd.read_csv(args.input)
    
    normalizer = FieldNormalizer()
    normalized_df = normalizer.explode_to_long_format(df)
    
    normalized_df.to_csv(args.output, index=False)
    print(f"✓ Normalization complete. Output saved to {args.output}")
    print(f"  Original rows: {len(df)}")
    print(f"  Normalized rows: {len(normalized_df)}")


def analyze_command(args):
    """Perform stratum aggregation analysis."""
    logger.info(f"Analyzing strata from {args.input}")
    
    import pandas as pd
    df = pd.read_csv(args.input)
    
    aggregator = StratumAggregator(min_stratum_size=args.min_size)
    results = aggregator.analyze_by_strata(df)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    aggregator.save_analysis_results(results, args.output_dir)
    
    print(f"✓ Analysis complete. Results saved to {args.output_dir}")
    print("\nAnalysis Summary:")
    for name, df_result in results.items():
        print(f"  {name}: {len(df_result)} rows")


def summary_command(args):
    """Generate user-friendly summary of results."""
    logger.info(f"Generating summary from {args.tables_dir}")
    
    try:
        from reporting.summary_report import SummaryReportGenerator
        
        generator = SummaryReportGenerator(args.tables_dir)
        output_file = f"{args.output_dir}/analysis_summary.txt" if hasattr(args, 'output_dir') and args.output_dir else None
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        report = generator.generate_full_report(output_file)
        print(report)
        
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")
        return


def report_command(args):
    """Generate comprehensive assignment report."""
    logger.info(f"Generating assignment report from {args.tables_dir}")
    
    try:
        from reporting.assignment_report import AssignmentReportGenerator
        
        generator = AssignmentReportGenerator(args.tables_dir, args.plots_dir)
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Generate comprehensive JSON report
        json_path = f"{args.output_dir}/assignment_report.json"
        report = generator.create_comprehensive_report(json_path)
        print(f"📄 Comprehensive report saved to: {json_path}")
        
        # Generate presentation outline
        slides = generator.create_presentation_outline()
        slides_path = f"{args.output_dir}/presentation_outline.json"
        with open(slides_path, 'w') as f:
            json.dump(slides, f, indent=2)
        print(f"🎯 Presentation outline saved to: {slides_path}")
        
        # Display summary
        print("\n" + "="*60)
        print("📊 ASSIGNMENT 4 REPORT SUMMARY")
        print("="*60)
        print(f"Project: {report['executive_summary']['project_title']}")
        print(f"Student: {report['executive_summary']['student']}")
        print(f"Date: {report['executive_summary']['date']}")
        print(f"\nKey Results:")
        for key, value in report['executive_summary']['key_results'].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nAssignment Requirements:")
        for req, data in report['assignment_requirements'].items():
            if isinstance(data, dict) and 'status' in data:
                print(f"  • {req.replace('_', ' ').title()}: {data['status']}")
        
        print(f"\n✅ All reports generated in: {args.output_dir}")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return


def narratives_command(args):
    """Generate LLM-powered narratives and insights."""
    logger.info(f"Generating narratives from {args.tables_dir}")
    
    try:
        from reporting.narratives import StratumNarrativeGenerator
        import pandas as pd
        
        # Load stratum summary
        summary_path = f"{args.tables_dir}/stratum_summary_by_stratum.csv"
        if not os.path.exists(summary_path):
            print(f"❌ Stratum summary not found: {summary_path}")
            return
        
        df = pd.read_csv(summary_path)
        generator = StratumNarrativeGenerator()
        
        if not generator.client:
            print("❌ Amplify client not available. Check your .env file.")
            return
        
        print("✓ Generating LLM-powered insights...")
        
        # Generate insights for top strata
        top_strata = df.nlargest(3, 'unique_studies')
        insights = []
        
        for _, row in top_strata.iterrows():
            stratum_data = row.to_dict()
            insight = generator.generate_stratum_insights(stratum_data)
            insights.append(insight)
            
            print(f"\n{'='*60}")
            print(f"STRATUM: {insight['stratum_id']}")
            print(f"({'Studies: ' + str(stratum_data.get('unique_studies', 0))})")
            print('='*60)
            print(insight['insight'])
        
        # Generate comparative analysis
        print(f"\n{'='*60}")
        print("COMPARATIVE INSIGHTS")
        print('='*60)
        comparison = generator.generate_comparative_insights(df)
        print(comparison)
        
        # Save insights
        os.makedirs(args.output_dir, exist_ok=True)
        insights_path = f"{args.output_dir}/llm_insights.json"
        
        with open(insights_path, 'w') as f:
            json.dump({
                'individual_insights': insights,
                'comparative_analysis': comparison,
                'generated_at': pd.Timestamp.now().isoformat()
            }, f, indent=2)
        
        print(f"\n✓ Insights saved to {insights_path}")
        
    except ImportError as e:
        print(f"⚠️  Required modules not available: {e}")
        return
    except Exception as e:
        print(f"❌ Narrative generation failed: {e}")
        return


def visualize_command(args):
    """Create visualizations."""
    logger.info(f"Creating visualizations from {args.tables_dir}")
    
    try:
        from viz.basic_plots import BasicPlotter
        import pandas as pd
        
        # Load analysis results
        analysis_results = {}
        result_files = [
            'stratum_summary_by_stratum.csv',
            'risk_factors_by_stratum.csv',
            'treatment_outcomes_by_stratum.csv',
            'symptoms_by_stratum.csv'
        ]
        
        for file in result_files:
            file_path = f"{args.tables_dir}/{file}"
            if os.path.exists(file_path):
                key = file.replace('_by_stratum.csv', '')
                analysis_results[key] = pd.read_csv(file_path)
        
        # Load normalized data
        normalized_df = pd.read_csv(args.normalized_csv)
        
        # Create visualizations
        os.makedirs(args.output_dir, exist_ok=True)
        plotter = BasicPlotter(args.output_dir)
        plotter.create_all_visualizations(analysis_results, normalized_df)
        
        print(f"✓ Visualizations created in {args.output_dir}")
        
    except ImportError as e:
        print(f"⚠️  Visualization libraries not available: {e}")
        print("Run: pip install matplotlib seaborn plotly")
        return


def pipeline_command(args):
    """Run the complete analysis pipeline."""
    logger.info("Starting complete analysis pipeline")
    
    # Create output directories
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/plots", exist_ok=True)
    
    try:
        # Step 1: Split fields
        print("Step 1: Splitting GPT output fields...")
        split_args = argparse.Namespace(
            input=args.input,
            output="outputs/tables/processed_data.csv"
        )
        split_fields_command(split_args)
        
        # Step 2: Normalize
        print("\nStep 2: Normalizing fields...")
        norm_args = argparse.Namespace(
            input="outputs/tables/processed_data.csv",
            output="outputs/tables/normalized_data.csv"
        )
        normalize_command(norm_args)
        
        # Step 3: Analyze
        print("\nStep 3: Performing stratum analysis...")
        analyze_args = argparse.Namespace(
            input="outputs/tables/normalized_data.csv",
            output_dir="outputs/tables",
            min_size=3
        )
        analyze_command(analyze_args)
        
        # Step 4: Visualize (if libraries available)
        print("\nStep 4: Creating visualizations...")
        viz_args = argparse.Namespace(
            tables_dir="outputs/tables",
            normalized_csv="outputs/tables/normalized_data.csv",
            output_dir="outputs/plots"
        )
        visualize_command(viz_args)
        
        print("\n" + "="*60)
        print("🎉 PIPELINE COMPLETE!")
        print("="*60)
        print("Results available in:")
        print("  • outputs/tables/ - Analysis tables")
        print("  • outputs/plots/ - Visualizations")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        print(f"❌ Pipeline failed: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Population-Stratum Analysis for Mental Health Literature",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python cli.py pipeline data/step3_extracted.csv
  
  # Individual steps
  python cli.py split data/step3_extracted.csv outputs/processed.csv
  python cli.py normalize outputs/processed.csv outputs/normalized.csv
  python cli.py analyze outputs/normalized.csv outputs/tables/
  python cli.py visualize outputs/tables/ outputs/normalized.csv outputs/plots/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Split command
    split_parser = subparsers.add_parser('split', help='Split GPT output fields')
    split_parser.add_argument('input', help='Input CSV with gpt_output column')
    split_parser.add_argument('output', help='Output CSV with split fields')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load and validate data')
    load_parser.add_argument('input', help='Input CSV file')
    
    # Normalize command
    norm_parser = subparsers.add_parser('normalize', help='Normalize fields')
    norm_parser.add_argument('input', help='Input CSV with extracted fields')
    norm_parser.add_argument('output', help='Output CSV in long format')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Perform stratum analysis')
    analyze_parser.add_argument('input', help='Input normalized CSV')
    analyze_parser.add_argument('output_dir', help='Output directory for analysis results')
    analyze_parser.add_argument('--min-size', type=int, default=3, help='Minimum stratum size (default: 3)')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Create visualizations')
    viz_parser.add_argument('tables_dir', help='Directory with analysis tables')
    viz_parser.add_argument('normalized_csv', help='Normalized data CSV')
    viz_parser.add_argument('output_dir', help='Output directory for plots')
    
    # Summary command  
    summary_parser = subparsers.add_parser('summary', help='Generate user-friendly summary')
    summary_parser.add_argument('tables_dir', help='Directory with analysis tables')
    summary_parser.add_argument('--output-dir', help='Output directory for summary file (optional)')
    
    # Assignment report command
    report_parser = subparsers.add_parser('report', help='Generate assignment report')
    report_parser.add_argument('tables_dir', help='Directory with analysis tables')
    report_parser.add_argument('plots_dir', help='Directory with plots')
    report_parser.add_argument('--output-dir', default='outputs/report', help='Output directory for reports')
    
    # Narratives command
    narr_parser = subparsers.add_parser('narratives', help='Generate LLM insights')
    narr_parser.add_argument('tables_dir', help='Directory with analysis tables')
    narr_parser.add_argument('output_dir', help='Output directory for insights')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Run complete pipeline')
    pipeline_parser.add_argument('input', help='Input CSV with gpt_output column')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'split': split_fields_command,
        'load': load_data_command,
        'normalize': normalize_command,
        'analyze': analyze_command,
        'visualize': visualize_command,
        'summary': summary_command,
        'report': report_command,
        'narratives': narratives_command,
        'pipeline': pipeline_command
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()