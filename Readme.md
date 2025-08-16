# FX Microstructure Alpha

### High-Frequency Foreign Exchange Trading Project (EUR/USD)

This project explores **high-frequency microstructure patterns** in the FX market, starting with the **EUR/USD currency pair**.  
The goal is to build a **data pipeline, feature engineering framework, predictive models, and a backtesting engine** to evaluate whether short-term price moves can be predicted from **order flow and bid-ask dynamics**.

---

## 🚀 Project Objectives
1. Collect and process high-frequency FX tick data (EUR/USD).  
2. Engineer microstructure features (spread, imbalance, volatility, order flow).  
3. Model short-term price direction using statistical & ML techniques.  
4. Design and backtest intraday trading strategies with transaction cost modeling.  
5. Evaluate performance with realistic risk and execution assumptions.  
6. Test robustness across multiple currency pairs (GBP/USD, USD/JPY).  

---

## 📂 Repository Structure
fx-microstructure-alpha/
│
├── data/
│ ├── raw/ # Raw tick data (not tracked in Git)
│ └── processed/ # Cleaned / resampled data
│
├── notebooks/ # Jupyter notebooks for analysis & experiments
│
├── src/ # Core Python scripts
│ ├── data_download.py
│ ├── data_preprocess.py
│ ├── features.py
│ ├── models.py
│ ├── backtest.py
│ └── utils.py
│
├── reports/ # Final research report & figures
│ └── figs/
│
├── streamlit_app/ # (Optional) Interactive demo dashboard
│
├── requirements.txt # Python dependencies
├── README.md # Project overview
└── .gitignore # Ignore large files and venv

---

## 🛠️ Tech Stack
- **Languages**: Python  
- **Libraries**: Pandas, NumPy, Scikit-learn, XGBoost, Matplotlib, Seaborn, Streamlit  
- **Data Source**: [Dukascopy Tick Data](https://www.dukascopy.com)  
- **Tools**: VS Code, Jupyter, Git/GitHub  

---

## 📊 Methodology
1. **Data Pipeline** → Fetch tick data (EUR/USD) → preprocess → store in Parquet.  
2. **Feature Engineering** → Compute spread, microprice, order flow imbalance, volatility.  
3. **Modeling** → Logistic Regression, Gradient Boosting, LSTM.  
4. **Backtesting** → Simulate intraday strategies with transaction cost & slippage.  
5. **Evaluation** → Sharpe ratio, PnL distribution, drawdowns, alpha half-life.  
6. **Robustness** → Extend analysis to GBP/USD and USD/JPY.  

---

## 📈 Expected Outcomes
- A reproducible research framework for FX high-frequency trading.  
- Insights into which microstructure features predict short-term price moves.  
- Quant-style research report summarizing methodology and results.  
- (Optional) A **Streamlit dashboard** to replay trading signals and visualize PnL.  

---

## 📌 Status
🔄 **In Progress** – Currently setting up data pipeline and initial exploratory analysis for EUR/USD.  

---

## 🤝 Contributions
This is a self-contained research project. Suggestions, pull requests, and collaborations are welcome.  

---

## 📧 Contact
Author: Amol Wani
