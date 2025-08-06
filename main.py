from flask import Flask, render_template, request
import pickle

app = Flask(__name__)
model = pickle.load(open("demand_model.pkl", "rb"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    temp = float(request.form["temperature"])
    humidity = float(request.form["humidity"])
    hour = float(request.form["hour"])
    prediction = model.predict([[temp, humidity, hour]])[0]
    return render_template("index.html", prediction=round(prediction, 2))

@app.route("/supply-status", methods=["POST"])
def supply_status():
    supply = float(request.form["supply"])
    expected_demand = float(request.form["expected_demand"])

    if supply >= expected_demand:
        status = f"✅ Sufficient Supply (Surplus: {round(supply - expected_demand, 2)} kWh)"
    else:
        status = f"⚠️ Insufficient Supply (Deficit: {round(expected_demand - supply, 2)} kWh)"

    return render_template("index.html", supply_status=status)

@app.route("/balance-load", methods=["POST"])
def balance_load():
    try:
        total_supply = float(request.form["total_supply"])
        predicted_demand = float(request.form["predicted_demand"])

        if predicted_demand == 0:
            return render_template("index.html", load_result="❌ Predicted demand cannot be zero.")

        # Fixed proportions for each sector
        residential_share = 0.5
        industrial_share = 0.3
        agriculture_share = 0.2

        scaling_factor = min(1, total_supply / predicted_demand)

        # Adjust distribution based on available supply
        residential = round(residential_share * predicted_demand * scaling_factor, 2)
        industrial = round(industrial_share * predicted_demand * scaling_factor, 2)
        agriculture = round(agriculture_share * predicted_demand * scaling_factor, 2)

        result = (
            f"⚖️ Load Distribution:\n"
            f"🏠 Residential: {residential} kWh\n"
            f"🏭 Industrial: {industrial} kWh\n"
            f"🌾 Agriculture: {agriculture} kWh"
        )

        return render_template("index.html", load_result=result)

    except Exception as e:
        return render_template("index.html", load_result=f"❌ Error: {e}")

@app.route("/forecast-renewable", methods=["POST"])
def forecast_renewable():
    try:
        irradiance = float(request.form["irradiance"])
        wind_speed = float(request.form["wind_speed"])

        # Simple estimation formulas (can be replaced with ML model later)
        solar_output = irradiance * 0.2  # Assuming 20% efficiency
        wind_output = (wind_speed ** 3) * 0.005  # Simplified wind power formula

        total_output = round((solar_output + wind_output) / 1000, 2)  # Convert to kWh

        return render_template("index.html", renewable_forecast=total_output)

    except Exception as e:
        return render_template("index.html", renewable_forecast=f"❌ Error: {e}")

# ✅ Always keep this at the end
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)

