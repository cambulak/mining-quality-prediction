import os

# --- PATH AYARLARI ---
# Projenin ana dizinini bulur
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SRC_DIR, '..'))

DATA_PATH = os.path.join(ROOT_DIR, 'data', 'MiningProcess_Flotation_Plant_Database.csv')
MODEL_PATH = os.path.join(ROOT_DIR, 'models', 'final_xgboost_model.pkl')
DB_PATH = os.path.join(ROOT_DIR, 'monitoring.db')

# --- MODEL PARAMETRELERİ (Optuna'dan gelenler) ---
MODEL_PARAMS = {
    'n_estimators': 814,
    'max_depth': 3,
    'learning_rate': 0.044,
    'subsample': 0.707,
    'colsample_bytree': 0.687,
    'reg_alpha': 2.66,
    'reg_lambda': 8.34,
    'random_state': 42
}

# --- FEATURES ---
TARGET = 'Silica_Concentrate'
DATE_COL = 'date'