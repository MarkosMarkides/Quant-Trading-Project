# Quant-Trading-Project

Welcome to my Quantitative Trading Project! This repository encompasses a comprehensive workflow for developing, training, and backtesting machine learning models aimed at predicting and trading financial instruments, specifically the EUR/USD currency pair based on 5-minute candlestick data, and finally, live trading based on the model's predictions.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)


---

## Project Overview
This project aims to build a predictive model for trading the EUR/USD currency pair using machine learning techniques. The workflow includes:
- **Data Acquisition**: Fetching historical price data via the OANDA API.
- **Data Preprocessing**: Cleaning and transforming raw data into meaningful features.
- **Feature Engineering**: Creating technical indicators to enhance model performance.
- **Labeling**: Assigning target labels based on trading strategies.
- **Model Training**: Developing a machine learning model to predict future price movements.
- **Hyperparameter Tuning**: Optimizing model parameters using advanced search techniques.
- **Backtesting**: Simulating trades based on model predictions to evaluate performance.
- **Live Trading**: Deploying a bot that receives live streaming prices and executes trades based on the model’s real-time predictions.
---

## Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- Jupyter Notebook
- Git
  
Ensure you have an OANDA account (required for data collection).

---

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/quant-project.git
   cd quant-project
   
2. Create a Virtual Environment:
	Create and activate a virtual environment to isolate the project dependencies.
	
		```bash
	 	python3 -m venv .venv
	 
	On macOS/Linux:
		
		source .venv/bin/activate
	On Windows:
	
		.venv\Scripts\activate
3.	Install Required Libraries:
	Install all the dependencies listed in the requirements.txt file.
		
		pip install -r requirements.txt
 

## Usage
To utilize this project, you need an OANDA account in order to be able to fetch historical price data and enable live trading.
Place your API credentials in the defs.py file located in the constants folder:

	OANDA_API_KEY=your_api_key_here
	OANDA_ACCOUNT_ID=your_account_id_here
 
No OANDA Account?
If you don’t have an OANDA account or don’t want to go through the process of data collection, model training, and hyperparameter tuning (which can be time-consuming), you can simply review the pre-generated outputs available in the repository.

Running the Project:
To go through the entire process step by step, open the main.ipynb file and execute the cells one by one. This notebook contains the full workflow, from data collection to live trading.










