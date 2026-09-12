# 🌾 Market-Aware Crop Recommendation System

Recommends the **top 3 crops** to grow based on soil and weather inputs, then ranks them by a **market score** (model confidence × current market price). Plug in your soil/weather numbers and it tells you both what will grow well *and* what's actually worth growing.

Uses a **Random Forest classifier** trained on 2,200 samples across 22 crops.

---

## 🗂️ Project Structure

```
market aware system/
│
├── data/
│   ├── Crop_recommendation.csv   # 2200-row training dataset (22 crops, 7 features)
│   └── market_prices.csv         # Current MSP/market prices per crop (₹/quintal)
│
├── train_model.py                # Trains the Random Forest and saves crop_model.pkl
├── recommender.py                # Core logic: prediction + market scoring
├── predict.py                    # CLI interface to run a single prediction
├── web.py                        # Streamlit web app (interactive UI)
├── crop_model.pkl                # Pre-trained model (ready to use, no retraining needed)
└── requirements.txt              # All Python dependencies (pinned versions)
```

---

## ⚙️ Setup (Do This Once)

### Prerequisites
- Python **3.9 or higher**
- `pip` (comes with Python)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yash6333/Market-Aware-Crop-Recommendation.git
cd Market-Aware-Crop-Recommendation
```

**2. Create a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

> ✅ The pre-trained model (`crop_model.pkl`) is already included. You do **not** need to retrain the model to run the system.

---

## 🚀 Running the System

### Option A — Web App (Recommended for most research tasks)
```bash
streamlit run web.py
```
Opens at `http://localhost:8501`. Provides:
- Manual input fields for all 7 soil/weather parameters
- **"Generate Sample Data"** button — loads a real row from the dataset
- **"Generate Interesting Scenario"** button — finds cases where the model is uncertain between crops (useful for studying decision boundaries)
- Bar chart comparing market scores across top 3 crops

### Option B — Command Line
```bash
python predict.py
```
Prompts you to enter values manually and prints the top 3 crops with probabilities, prices, and scores. Useful for batch scripting or quick tests.

---

## 📊 Input Parameters

| Parameter | Unit | Range | Description |
|-----------|------|--------|-------------|
| N | mg/kg | 0 – 140 | Soil Nitrogen content |
| P | mg/kg | 0 – 145 | Soil Phosphorus content |
| K | mg/kg | 0 – 205 | Soil Potassium content |
| Temperature | °C | -10 – 60 | Average ambient temperature |
| Humidity | % | 0 – 100 | Relative humidity |
| pH | — | 0 – 14 | Soil pH |
| Rainfall | mm | 0 – 300 | Annual rainfall |

---

## 📤 Output Format

For each prediction, the system returns the **top 3 crops** ranked by model confidence:

| Field | Description |
|-------|-------------|
| Crop | Crop name |
| Probability | Model confidence that this crop suits the input conditions (%) |
| Price (₹) | Market price per quintal from `market_prices.csv` |
| Score | `probability × price` — higher = better market opportunity |

**Best Crop** is selected as the one with the **highest market score** (not just highest probability). If price data is unavailable for a crop, it falls back to the highest-probability crop.

---

## 🌱 Dataset Details

### `Crop_recommendation.csv`
- **Source:** Kaggle Crop Recommendation Dataset
- **Size:** 2,200 rows × 8 columns
- **Features:** N, P, K, temperature, humidity, ph, rainfall
- **Target:** `label` (crop name)
- **Crops covered (22):** rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

### `market_prices.csv`
- **Contents:** MSP (Minimum Support Price) / approximate market price in ₹ per quintal for 21 of the 22 crops
- **Note:** `watermelon` does not have a price entry — the system handles this gracefully by showing it without a score
- **Modifiable:** You can update prices here to simulate different market conditions for your research

---

## 🤖 Model Details

| Property | Value |
|----------|-------|
| Algorithm | Random Forest Classifier |
| Library | scikit-learn 1.8.0 |
| Train/Test split | 80% / 20% |
| Random state | 42 (reproducible) |
| Accuracy | ~99% on held-out test set |
| Output | `predict_proba` — probability distribution over all 22 crops |

To **retrain the model** from scratch (e.g., after modifying the dataset):
```bash
python train_model.py
```
This overwrites `crop_model.pkl` with a freshly trained model and prints the test accuracy.

---

## 💡 Things Worth Knowing

- The **"Generate Interesting Scenario"** button in the web app is actually really useful — it finds cases where the model is unsure between crops (low confidence or small gap between top 2). Good starting point for exploring edge cases.
- The **best crop** is picked by market score, not raw probability. So if rice has 70% confidence at ₹3,249 and coffee has 50% at ₹19,800 — coffee wins. Keep that in mind when reading results.
- `watermelon` has no price entry in `market_prices.csv` — if it shows up in your top 3, it won't have a score. This is expected.
- You can run `python predict.py` if you just want a quick terminal output without opening the browser.

---

## 🛠️ Modifying Market Prices

To simulate different market conditions, open `data/market_prices.csv` and update the `price` column:

```csv
crop,price
rice,3249
maize,1902
...
```

Prices are in **₹ per quintal**. No code changes needed — the app reads this file on every run.

---

## 🐛 Troubleshooting

### `streamlit run web.py` doesn't work

This is the most common issue. Try these in order:

**1. Streamlit isn't installed / venv isn't active**
```bash
# Activate your venv first
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# Then install
pip install -r requirements.txt
```

**2. `streamlit` command not recognized even after installing**

This happens when pip installs it but it's not on your PATH. Use this instead:
```bash
python -m streamlit run web.py
```
This works 99% of the time when the normal command doesn't.

**3. On Windows — execution policy blocking the command**

If you get something like *"cannot be loaded because running scripts is disabled"*, run this in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned
```
Then try again.

**4. Port 8501 already in use**

Something else is already running on that port (maybe a previous session didn't close cleanly).
```bash
python -m streamlit run web.py --server.port 8502
```
Or just kill whatever is using 8501:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <pid_from_above> /F
```

**5. Browser doesn't open automatically**

Streamlit should print a URL like `http://localhost:8501`. Just open that manually in your browser if it doesn't pop up.

---

### Other common issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` for any package | Venv probably isn't active. Run `venv\Scripts\activate` then `pip install -r requirements.txt` |
| `FileNotFoundError: crop_model.pkl` | The model file is missing. Run `python train_model.py` to generate it |
| `FileNotFoundError: data/Crop_recommendation.csv` | Make sure you're running commands from inside the project folder, not somewhere else |
| App loads but "Recommend Crop" does nothing | Check the terminal where you ran streamlit — there's likely an error printed there |
| Scores show as `None` for some crops | That crop doesn't have a price in `market_prices.csv`. Totally fine, just means no score for that one |
| `ValueError: pH must be between 0 and 14` | Input validation — double check your inputs are in the valid ranges shown in the input table |
| Slow to load on first run | Normal — it's loading the dataset and model into memory. Should be fast after that |
| `pip install` taking forever | Try `pip install -r requirements.txt --no-cache-dir` |

---

## 📬 Questions?

If something's broken or you're not sure about something, just message me before editing shared files like `data/market_prices.csv` or `crop_model.pkl` — those affect everyone.
