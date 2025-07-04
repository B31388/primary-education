# Assignment 2: Dashboard Redesign for Usability and Interactivity

## Author
- **Name**: Mugimba Kakure Jude
- **Access No.**: B31388
- **Reg. No.**: J25M19/034
- **Submission Date**: July 04, 2025

## Project Overview
This repository contains the deliverables for Assignment 2, focusing on redesigning a cluttered dashboard using F-pattern and Z-pattern layouts. The project targets education policymakers in Uganda, providing interactive visualizations of education access metrics (e.g., enrollment, literacy, dropout rates) across districts.

### Objectives
- Redesign a dashboard for improved visual hierarchy, layout logic, and usability.
- Implement two versions: F-pattern and Z-pattern layouts.
- Optimize for interactivity with filters, download options, and tooltips.

### Deliverables
- `f_pattern_v3.py`: F-pattern dashboard prototype.
- `z_pattern_v3.py`: Z-pattern dashboard prototype.
- `education_data_long.csv`: Dataset with education metrics.
- `uganda_districts.json`: GeoJSON file for district maps.

## Setup Instructions
1. **Prerequisites**:
   - Python 3.x
   - Libraries: `dash`, `dash-bootstrap-components`, `plotly`, `pandas`


2. **Installation**:
   - Clone the repository:
     ```bash
     git clone https://github.com/B31388/primary-education
     cd /workspaces/primary-education

     Run the Dashboards:
F-pattern: python f_pattern_v3.py (access at http://localhost:8050)
Z-pattern: python z_pattern_v3.py (access at http://localhost:8051)