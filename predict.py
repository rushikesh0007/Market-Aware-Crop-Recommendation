from recommender import recommend_crop

print("=== Market-Aware Crop Recommendation ===\n")
print("Enter the soil and weather details for your field:\n")

N           = float(input("Nitrogen (N): "))
P           = float(input("Phosphorus (P): "))
K           = float(input("Potassium (K): "))
temperature = float(input("Temperature (°C): "))
humidity    = float(input("Humidity (%): "))
ph          = float(input("pH: "))
rainfall    = float(input("Rainfall (mm): "))

results, best_crop = recommend_crop(N, P, K, temperature, humidity, ph, rainfall)

print("\nTop 3 recommended crops:")
for crop, prob, price, score in results:
    price_str = f"₹{price}" if price is not None else "price unavailable"
    score_str = f"score {score}" if score is not None else "no score"
    print(f"  {crop} — {prob}% probability — {price_str} — {score_str}")

print(f"\nBest crop to grow: {best_crop}")