<p align="center">
  <img src="https://img.shields.io/badge/Project-Traffic%20Simulation-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Built%20With-Streamlit-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Focus-Optimization-green?style=for-the-badge" />
</p>

# Traffic Intelligence System – Bottleneck Optimization Simulator


## 1. Project Overview

The Traffic Intelligence System is an interactive, data-driven simulation designed to model, analyze, and optimize traffic bottlenecks. Built to compare uncoordinated, free-flowing traffic (Baseline) against a strictly enforced alternate flow strategy (Zipper Merge), it demonstrates how structured decision-making improves the efficiency of urban mobility. The project focuses purely on optimization logic, throughput metrics, and dynamic grid visualization.

## 2. Features

- **Interactive Simulation**: Powered by a robust Streamlit dashboard.
- **Adjustable Parameters**: Dynamically tweak the scenario on the sidebar:
  - Incoming lanes
  - Outgoing lanes
  - Number of vehicles
  - Aggressive driver %
- **Real-time Visualization**: Watch traffic bottleneck physics mapped seamlessly.
- **Baseline vs Optimized Comparison**: Side-by-side run evaluations.
- **Metrics**:
  - Average wait time
  - Throughput
  - Queue length

## 3. Tech Stack

- **Python**: Core simulation logic and modeling.
- **Streamlit**: Interactive user interface and dashboard layout.
- **Matplotlib / NumPy**: High-performance rendering and data logic.

## 4. Project Structure

```
project/
├── app.py
├── simulation.py
├── requirements.txt
├── assets/
│   ├── blue_car.png
│   └── red_car.png
```

## 5. Installation & Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 6. How It Works

- Vehicles spawn identically across incoming lanes based on random behavior vectors.
- A physical bottleneck structure progressively reduces the available lanes.
- Two distinct strategies are tested:
  - **Baseline (uncontrolled)**: Models organic, uncoordinated traffic and aggressive clustering.
  - **Zipper merge (optimized)**: Imposes perfectly distributed mathematical flow logic.
- Target metrics are calculated and compared after evaluating the throughput logic.

## 7. Use Cases

- Traffic research
- Smart city planning
- Educational simulation
- AI-based optimization experiments

## 8. Future Improvements

- AI-based traffic control
- Reinforcement learning
- Real-time data integration
- Better visualization (curved lanes, animations)

## 9. Author

- **Dev_Decs**
