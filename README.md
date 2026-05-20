# F1 2026 Bayesian Network Predictor 🏎️

**⚠️ Experimental Notice:** This is a university mini-project. It is highly experimental and uses a simplified probability model. The predictions and data groupings are designed to demonstrate how Bayesian Networks function, rather than being a perfect or delicate simulation of real-world F1 racing. 

## Overview
This project uses a Bayesian Network to predict the probability of a Formula 1 driver winning the 2026 championship. It combines historical 2025 performance data (as the Prior) with early 2026 race results (as the Evidence) to calculate the outcomes.

## Tech Stack
* **Data Extraction:** Python, Pandas, `fastf1` library
* **Environment:** Nix (Flakes), `uv`
* **Modeling Software:** Netica

## How to Run the Project

This project uses Nix and `uv` to keep the Python environment perfectly isolated and reproducible.

1. Open your terminal in the project folder and load the Nix shell:
    ```bash
   nix develop
    ```

2. Install the required Python packages:
    ```bash
    uv sync
    ```


3. Start Jupyter Lab to run the data extraction scripts:
    ```bash
    uv run jupyter lab
    ```



## The Data Pipeline

The Python script downloads raw race data and groups the continuous statistics into discrete states (using Z-scores to handle outliers). The network uses 4 main variables:

1. **Driver_Skill_25:** Based on 2025 points per finish (States: Elite, Good, Mid, Low).
2. **Team_Legacy_25:** Based on 2025 constructor standings (States: Top_Tier, Midfield, Backmarker).
3. **Expected_Race_Pace_26:** Based on average finish position in 2026 (States: P1_P3, P4_P10, Out_of_Points).
4. **Reliability_26:** Based on mechanical failures in 2026 (States: Solid, Fragile).

The final output is a cleaned dataset saved as `final.csv` and `dists.csv`.

## Netica Instructions

To build the probability tables in Netica:

1. Draw the network nodes and name them exactly as they appear in the CSV headers.
2. Link the parent nodes to the child nodes.
3. In the top menu, go to **Cases -> Learn -> Incorporate Case File...**
4. Select the `final.csv` file.
5. Netica will automatically learn the patterns and fill in the Conditional Probability Tables (CPTs).

