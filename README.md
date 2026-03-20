# finops-dashboard
Interactive FinOps dashboard that visualizes cost drivers, savings opportunities, and action priorities from the FinOps Action Engine.
## Overview

Initial FinOps dashboard that surfaces KPIs, cost drivers, and actionable savings opportunities to support decision-making.
# FinOps Dashboard

A simple dashboard that visualizes FinOps action items, cost drivers, and savings opportunities.

## Features

- Total savings visibility  
- High-priority issue tracking  
- Cost driver breakdown  
- Action item table  

## Data Source

This dashboard consumes output from:

- finops-action-engine

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
