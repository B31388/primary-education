# QUESTION 4: Dashboard design for Usability and Interactivity

## Author
- **Name**: Mugimba Kakure Jude
- **Access No.**: B31388
- **Reg. No.**: J25M19/034
- **Submission Date**: July, 2025

## Project Overview
This repository contains deliverables addressing Question 4: visualizing geographic disparities in education access across Uganda using geospatial data. The project dashboard with F-pattern and Z-pattern layouts, revealing that areas like Bushenyi (380% pressure, 36% completion, correlation -0.6351) show low completion despite economic/infrastructure strengths, indicating strain.

### Deliverables
- `f_pattern_v3.py`: F-pattern dashboard with dual choropleth maps.
- `z_pattern_v3.py`: Z-pattern dashboard with dual choropleth maps.
- `education_data_long.csv`: Dataset with education metrics.
- `uganda_districts.json`: GeoJSON file for district maps.
- `Question_4_Report.tex`: LaTeX source for design documentation.

## Setup Instructions
1. **Prerequisites**: Python 3.x, `dash`, `dash-bootstrap-components`, `plotly`, `pandas`, LaTeX.
2. **Installation**:
   ```bash
   git clone https://github.com/mugimbajude/primary-education.git
   cd primary-education
   pip install dash dash-bootstrap-components plotly pandas