import pandas as pd
import joblib

# load the trained model we saved earlier
model = joblib.load("crop_model.pkl")

# read the price list and turn it into a simple dict for fast lookups
prices = pd.read_csv("data/market_prices.csv")
price_dict = dict(zip(prices["crop"], prices["price"]))


def recommend_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Given soil and weather conditions, returns the top 3 crops
    ranked by market score (how likely the crop grows × its market price),
    plus the single best pick.
    """

    # basic sanity checks before we touch the model
    if not (0 <= ph <= 14):
        raise ValueError(f"pH must be between 0 and 14 (got {ph})")
    if not (0 <= humidity <= 100):
        raise ValueError(f"Humidity must be between 0 and 100% (got {humidity})")
    if rainfall < 0:
        raise ValueError(f"Rainfall can't be negative (got {rainfall})")
    if not (-20 <= temperature <= 60):
        raise ValueError(f"Temperature looks off — expected -20 to 60°C (got {temperature})")
    if N < 0:
        raise ValueError(f"Nitrogen can't be negative (got {N})")
    if P < 0:
        raise ValueError(f"Phosphorus can't be negative (got {P})")
    if K < 0:
        raise ValueError(f"Potassium can't be negative (got {K})")

    # wrap the inputs into a DataFrame so sklearn is happy
    sample = pd.DataFrame(
        [[N, P, K, temperature, humidity, ph, rainfall]],
        columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    )

    # ask the model how confident it is about each crop
    probs = model.predict_proba(sample)[0]

    # grab the 3 crops the model is most confident about
    top3 = probs.argsort()[-3:][::-1]

    results = []

    for i in top3:
        crop = model.classes_[i]
        prob = round(probs[i] * 100, 1)
        price = price_dict.get(crop, None)

        # score = probability × price — higher means better market opportunity
        if price is not None:
            score = round(probs[i] * price, 2)
        else:
            score = None  # no price data, can't score this one

        results.append((crop, prob, price, score))

    # pick the crop with the highest market score;
    # if none have prices, just go with whatever the model is most confident about
    scored = [r for r in results if r[3] is not None]
    best_crop = max(scored, key=lambda x: x[3])[0] if scored else (results[0][0] if results else None)

    return results, best_crop