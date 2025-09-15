# Population-Stratum Analysis for Mental Health Literature

**Assignment 4: Automated Document Analysis**  
**Student:** Azure Xia  
**Course:** Amplify API Development  

## Overview

This system performs automated population stratification analysis on mental health literature, discovering how treatment patterns vary across demographic groups. The system processes 215+ research studies to identify population-specific research gaps and treatment effectiveness patterns.

## 🚀 Quick Start - View the Demo

### **Option 1: Instant Demo (No Setup Required)**
1. **Download** the `STANDALONE_DEMO.html` file
2. **Double-click** to open in any web browser
3. **View** the complete analysis results immediately

### **Option 2: GitHub Pages (Live Website)**
Visit the live demo at: `https://yourusername.github.io/repository-name/assignment4/azure_xia/STANDALONE_DEMO.html`

### **Option 3: Full Interactive Version (Setup Required)**
For the complete version with interactive plots:
1. Clone this repository: `git clone [your-repo-url]`
2. Navigate to folder: `cd assignment4/azure_xia/`
3. Install dependencies: `pip install -r requirements.txt`
4. Run analysis: `python run.py`
5. Open: `FINAL_DEMO_WITH_PLOTS.html` in your browser

## Key Features

- **Hierarchical Population Classification**: 51 distinct strata from combinations of age, sex, clinical conditions, and settings
- **Cross-Document Analysis**: Pattern identification across large study collections
- **Automated Visualization**: Five different chart types with embedded interpretations
- **Real-Time Processing**: Complete analysis pipeline in under 30 seconds
- **Clinical Translation**: Research findings presented in actionable format

## Project Structure

```
assignment4/azure_xia/
├── README.md                           # This file
├── LIVE_DEMO_SCRIPT.md                # Step-by-step demonstration guide
├── FINAL_DEMO_WITH_PLOTS.html         # Complete demo with visualizations
├── FINAL_DEMO_SIMPLE.html             # Clean demo without plots
├── FINAL_PRESENTATION.html            # Interactive presentation slides
├── 
├── data/                               # Input data
│   └── step3_extracted.csv            # GPT-processed study data
├── 
├── src/                                # Source code
│   ├── cli.py                         # Main command-line interface
│   │
│   ├── prepare/                       # Data preparation modules
│   │   ├── gpt_output_splitter.py     # Split GPT output into fields
│   │   ├── normalize_labels.py        # Population normalization (original)
│   │   └── fixed_normalize_labels.py  # Improved hierarchical classification
│   │
│   ├── loaders/                       # Data loading utilities
│   │   └── csv_loader.py              # Mental health data loader
│   │
│   ├── analysis/                      # Statistical analysis
│   │   ├── aggregates.py              # Stratum aggregation (original)
│   │   ├── improved_aggregates.py     # Quality-filtered analysis
│   │   └── enhanced_aggregates.py     # Enhanced with clear categories
│   │
│   ├── viz/                           # Visualization generation
│   │   ├── basic_plots.py             # Original plotting functions
│   │   ├── enhanced_plots.py          # Improved with clear labels
│   │   └── improved_sankey.py         # Enhanced Sankey diagrams
│   │
│   └── reporting/                     # Report generation
│       ├── summary_report.py          # User-friendly summaries
│       ├── assignment_report.py       # Comprehensive assignment reports
│       ├── narratives.py              # LLM-powered insights (requires API)
│       ├── slides_generator.py        # HTML presentation slides
│       ├── demo_website.py            # Interactive demo websites
│       ├── comprehensive_demo.py      # Single-file demo with plots
│       └── plot_interpretations.py    # Detailed plot explanations
├── 
├── outputs/                           # Generated results
│   ├── tables/                        # Analysis results (CSV)
│   │   ├── processed_data.csv         # Split GPT fields
│   │   ├── normalized_data.csv        # Long-format data (original)
│   │   ├── normalized_data_fixed.csv  # Improved hierarchical data
│   │   ├── stratum_summary_by_stratum.csv
│   │   ├── risk_factors_by_stratum.csv
│   │   ├── treatments_by_stratum.csv
│   │   ├── symptoms_by_stratum.csv
│   │   └── treatment_outcomes_by_stratum.csv
│   │
│   ├── plots/                         # Visualizations
│   │   ├── stratum_overview.png       # Population coverage analysis
│   │   ├── top_risk_factors.png       # Risk factors by population
│   │   ├── symptoms_comparison.png    # Symptom heatmap
│   │   ├── treatment_outcomes_heatmap.png
│   │   └── sankey_flow.html           # Interactive treatment pathways
│   │
│   ├── report/                        # Comprehensive reports
│   │   ├── assignment_report.json     # Detailed assignment analysis
│   │   └── presentation_outline.json  # Slide structure
│   │
│   └── [various other output directories]
└── 
└── .env.example                       # Environment template for API keys
```

## Workflow

### 1. Data Processing Pipeline
```bash
# Complete automated pipeline
python3 src/cli.py pipeline data/step3_extracted.csv
```

**Pipeline Steps:**
1. **Field Splitting**: Extract population, treatments, outcomes from GPT output
2. **Population Normalization**: Create hierarchical demographic categories
3. **Statistical Aggregation**: Calculate frequencies within each population stratum
4. **Visualization Generation**: Create charts and interactive diagrams
5. **Report Generation**: Produce summaries and comprehensive analysis

### 2. Individual Commands
```bash
# Split GPT output fields
python3 src/cli.py split data/step3_extracted.csv outputs/processed.csv

# Create population hierarchy
python3 src/cli.py normalize outputs/processed.csv outputs/normalized.csv

# Perform stratum analysis
python3 src/cli.py analyze outputs/normalized.csv outputs/tables/

# Generate visualizations
python3 src/cli.py visualize outputs/tables/ outputs/normalized.csv outputs/plots/

# Create user-friendly summary
python3 src/cli.py summary outputs/tables/

# Generate assignment report
python3 src/cli.py report outputs/tables/ outputs/plots/
```

### 3. Advanced Features
```bash
# Generate LLM insights (requires Amplify API)
python3 src/cli.py narratives outputs/tables/ outputs/insights/

# Create presentation slides
python3 src/reporting/slides_generator.py outputs/report/presentation_outline.json slides.html

# Generate demo website
python3 src/reporting/comprehensive_demo.py outputs/tables/ outputs/plots/ demo.html
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Required packages: pandas, numpy, matplotlib, seaborn, plotly
- Optional: requests, python-dotenv, tenacity (for API features)

### Quick Start
```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn plotly

# Optional packages for advanced features
pip install requests python-dotenv tenacity kaleido

# Run complete analysis
cd assignment4/azure_xia
python3 src/cli.py pipeline data/step3_extracted.csv

# View results
open outputs/plots/stratum_overview.png
open outputs/plots/sankey_flow.html
open FINAL_DEMO_WITH_PLOTS.html
```

### API Configuration (Optional)
For LLM-powered insights, create `.env` file:
```
AMPLIFY_API_KEY=your_api_key_here
AMPLIFY_BASE_URL=https://api.anthropic.com
```

## Key Results

- **Population Strata**: 51 hierarchical groups from age × sex × conditions × settings
- **Research Coverage**: 21 well-studied groups, 30 understudied groups
- **Time Period**: 2020-2024 literature (215 studies)
- **Processing Speed**: Complete analysis in ~30 seconds
- **Visualization Types**: 5 different charts with detailed interpretations

## Clinical Applications

- **Research Priorities**: Identify understudied populations for targeted funding
- **Treatment Selection**: Evidence-based guidance for population-specific interventions
- **Risk Assessment**: Population-typical risk factor profiles for screening
- **Outcome Prediction**: Expected results based on population-treatment combinations

## Technical Innovation

- **Hierarchical Classification**: Age, sex, clinical conditions, and care settings
- **Cross-Document Pattern Discovery**: Beyond individual document analysis
- **Real-Time Visualization**: Automated chart generation with embedded interpretations
- **Clinical Translation**: Research findings in actionable clinical format
- **Extensible Architecture**: Modular design for new analysis types

## Demonstration

### Live Demo
1. **Open demo website**: `open FINAL_DEMO_WITH_PLOTS.html`
2. **Run live pipeline**: `python3 src/cli.py pipeline data/step3_extracted.csv`
3. **Show visualizations**: `open outputs/plots/sankey_flow.html`

### Presentation
- **Interactive slides**: `open FINAL_PRESENTATION.html` (use arrow keys)
- **Demo script**: See `LIVE_DEMO_SCRIPT.md` for step-by-step guide

## Files for Class Demonstration

1. **`FINAL_DEMO_WITH_PLOTS.html`** - Final report demo with complete visualizations and detailed interpretations
2. **`LIVE_DEMO_SCRIPT.md`** - 5-7 minute demonstration guide
3. **`FINAL_PRESENTATION.html`** - Interactive slides with keyboard navigation
4. **`outputs/plots/`** - All visualizations with clear labels and interpretations

## Making the Demo Website Publicly Accessible

### Method 1: GitHub Pages (Recommended)
```bash
# Push to GitHub repository
git add FINAL_DEMO_WITH_PLOTS.html
git commit -m "Add final demo report"
git push origin main

# Enable GitHub Pages
# 1. Go to repository Settings on GitHub
# 2. Scroll to "Pages" section
# 3. Select "Deploy from a branch" 
# 4. Choose "main" branch and "/ (root)" folder
# 5. Website will be available at: https://username.github.io/repository-name/FINAL_DEMO_WITH_PLOTS.html
```

### Method 2: Local Server Sharing
```bash
# Start local HTTP server
cd /Users/jacinda/amplify-api-course/assignment4/azure_xia
python3 -m http.server 8000

# Share with others using:
# - Your IP address: http://YOUR_IP:8000/FINAL_DEMO_WITH_PLOTS.html  
# - Or use ngrok for external access: ngrok http 8000
```

### Method 3: File Sharing Platforms
```bash
# Upload FINAL_DEMO_WITH_PLOTS.html to:
# - Google Drive (set sharing to "Anyone with link can view")
# - Dropbox (create shareable link)
# - OneDrive (create shareable link)
# Users can download and open in any web browser
```

### Method 4: Cloud Hosting Services
```bash
# Deploy to platforms like:
# - Netlify: Drag and drop FINAL_DEMO_WITH_PLOTS.html
# - Vercel: Upload via web interface
# - Firebase Hosting: Deploy with Firebase CLI
# All provide free hosting with public URLs
```

## Contact & Support

**Student**: Azure Xia  
**Assignment**: 4 - Automated Document Analysis  
**Course**: Amplify API Development  
**Date**: September 2025