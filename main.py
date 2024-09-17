import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for non-GUI environments
from flask import Flask, request, render_template_string, url_for
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns 

app = Flask(__name__)

# Function to calculate d1 and d2
def getd1d2(S, K, r, T, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

# Black-Scholes formula
def blackScholes(S, K, r, T, sigma, option_type="call"):
    d1, d2 = getd1d2(S, K, r, T, sigma)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

# Delta
def delta(S, K, r, T, sigma, option_type="call"):
    d1, _ = getd1d2(S, K, r, T, sigma)
    if option_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

# Gamma
def gamma(S, K, r, T, sigma):
    d1, _ = getd1d2(S, K, r, T, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

# Theta
def theta(S, K, r, T, sigma, option_type="call"):
    d1, d2 = getd1d2(S, K, r, T, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    if option_type == "call":
        term2 = r * K * np.exp(-r * T) * norm.cdf(d2)
        theta = term1 - term2
    else:
        term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
        theta = term1 + term2
    return theta / 365  # Convert to per-day theta

# Vega
def vega(S, K, r, T, sigma):
    d1, _ = getd1d2(S, K, r, T, sigma)
    return S * np.sqrt(T) * norm.pdf(d1) * 0.01  # Vega per 1% change in volatility

# Rho
def rho(S, K, r, T, sigma, option_type="call"):
    _, d2 = getd1d2(S, K, r, T, sigma)
    if option_type == "call":
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) * 0.01
    else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) * 0.01
    return rho

# Function to generate plot image and return it as a base64 string
def generate_plot(spot_prices, values, ylabel):
    plt.figure(figsize=(5, 3))  # Adjusted graph size
    sns.set_style("darkgrid")
    plt.plot(spot_prices, values, color='#1f77b4', linestyle='--', marker='o', markersize=4)
    plt.xlabel('Underlying Asset Price')
    plt.ylabel(ylabel)
    plt.title(f'{ylabel} vs Underlying Asset Price')
    plt.grid(True, linestyle=':', linewidth=0.5)
    plt.tight_layout()


    # Save it to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)

    # Convert the image to a base64 string
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return image_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default values
    S = 30.00
    K = 50.00
    r = 0.03
    T = 1.0  # Time in years
    sigma = 0.30
    option_type = 'call'  # Default is Call

    if request.method == 'POST':
        # Get data from form inputs
        S = float(request.form.get('S', 30.00))
        K = float(request.form.get('K', 50.00))
        r = float(request.form.get('r', 0.03))
        T = float(request.form.get('T', 1.0))
        sigma = float(request.form.get('sigma', 0.30))
        option_type = request.form.get('type', 'call')

    # Calculate the Greeks and Option Price
    option_price = round(blackScholes(S, K, r, T, sigma, option_type), 4)
    delta_value = round(delta(S, K, r, T, sigma, option_type), 4)
    gamma_value = round(gamma(S, K, r, T, sigma), 4)
    theta_value = round(theta(S, K, r, T, sigma, option_type), 4)
    vega_value = round(vega(S, K, r, T, sigma), 4)
    rho_value = round(rho(S, K, r, T, sigma, option_type), 4)

    # Generate values for spot prices
    spot_prices = np.linspace(10, 100, 100)

    # Calculate Greeks and Option Price for plotting
    deltas = [delta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    gammas = [gamma(SP, K, r, T, sigma) for SP in spot_prices]
    thetas = [theta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    vegas = [vega(SP, K, r, T, sigma) for SP in spot_prices]
    rhos = [rho(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    prices = [blackScholes(SP, K, r, T, sigma, option_type) for SP in spot_prices]

    # Generate plots for each Greek and the option price
    delta_plot = generate_plot(spot_prices, deltas, 'Delta')
    gamma_plot = generate_plot(spot_prices, gammas, 'Gamma')
    theta_plot = generate_plot(spot_prices, thetas, 'Theta')
    vega_plot = generate_plot(spot_prices, vegas, 'Vega')
    rho_plot = generate_plot(spot_prices, rhos, 'Rho')
    price_plot = generate_plot(spot_prices, prices, 'Option Price')

    # Render the template with the form, results, and graphs
    return render_template_string('''
<!DOCTYPE html>
<html>
    <head>
        <title>Black-Scholes Option Price Calculator</title>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles.css') }}">
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const currentTheme = localStorage.getItem("theme");
                if (currentTheme === "dark") {
                    document.body.classList.add("dark-mode");
                    document.querySelectorAll("button, input, select, h1, h3, label").forEach(el => el.classList.add("dark-mode"));
                }
                document.getElementById("theme-toggle").addEventListener("click", function() {
                    document.body.classList.toggle("dark-mode");
                    document.querySelectorAll("button, input, select, h1, h3, label").forEach(el => el.classList.toggle("dark-mode"));
                    if (document.body.classList.contains("dark-mode")) {
                        localStorage.setItem("theme", "dark");
                    } else {
                        localStorage.setItem("theme", "light");
                    }
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <div class="main-content">
                <button id="theme-toggle">Toggle Dark/Light Mode</button>
                <h1>Black-Scholes Option Price and Greeks Calculator</h1>
                
                <!-- Display the calculated option price and Greeks -->
                <h3>{{ "Call Price" if option_type == "call" else "Put Price" }}: {{ option_price }}</h3>
                <h3>Delta: {{ delta_value }}</h3>
                <h3>Gamma: {{ gamma_value }}</h3>
                <h3>Theta: {{ theta_value }}</h3>
                <h3>Vega: {{ vega_value }}</h3>
                <h3>Rho: {{ rho_value }}</h3>
                
                <h3>Greeks and Option Price vs Stock Price:</h3>
                <div class="graph-grid">
                    <div>
                        <h4>Option Price</h4>
                        <img src="data:image/png;base64,{{price_plot}}" alt="Option Price plot">
                    </div>
                    <div>
                        <h4>Delta (Δ)</h4>
                        <img src="data:image/png;base64,{{delta_plot}}" alt="Delta plot">
                    </div>
                    <div>
                        <h4>Gamma (Γ)</h4>
                        <img src="data:image/png;base64,{{gamma_plot}}" alt="Gamma plot">
                    </div>
                    <div>
                        <h4>Theta (θ)</h4>
                        <img src="data:image/png;base64,{{theta_plot}}" alt="Theta plot">
                    </div>
                    <div>
                        <h4>Vega (ν)</h4>
                        <img src="data:image/png;base64,{{vega_plot}}" alt="Vega plot">
                    </div>
                    <div>
                        <h4>Rho (ρ)</h4>
                        <img src="data:image/png;base64,{{rho_plot}}" alt="Rho plot">
                    </div>
                </div>
            </div>
            <div class="sidebar">
                <form method="POST">
                    <h3>Input Parameters:</h3>
                    <label for="S">Underlying Asset Price (S):</label>
                    <input type="number" step="0.01" id="S" name="S" value="{{S}}" required>

                    <label for="K">Strike Price (K):</label>
                    <input type="number" step="0.01" id="K" name="K" value="{{K}}" required>

                    <label for="r">Risk-Free Rate (r):</label>
                    <input type="number" step="0.001" id="r" name="r" value="{{r}}" required>

                    <label for="T">Time to Expiry (T in years):</label>
                    <input type="number" step="any" id="T" name="T" value="{{T}}" required>

                    <label for="sigma">Volatility (σ):</label>
                    <input type="number" step="0.01" id="sigma" name="sigma" value="{{sigma}}" required>

                    <label for="type">Option Type:</label>
                    <select id="type" name="type">
                        <option value="call" {% if option_type == "call" %}selected{% endif %}>Call</option>
                        <option value="put" {% if option_type == "put" %}selected{% endif %}>Put</option>
                    </select>

                    <button type="submit">Calculate</button>
                </form>
            </div>
        </div>
    </body>
</html>
''', S=S, K=K, r=r, T=T, sigma=sigma, option_type=option_type,
     option_price=option_price, delta_value=delta_value, gamma_value=gamma_value,
     theta_value=theta_value, vega_value=vega_value, rho_value=rho_value,
     delta_plot=delta_plot, gamma_plot=gamma_plot, theta_plot=theta_plot,
     vega_plot=vega_plot, rho_plot=rho_plot, price_plot=price_plot)

if __name__ == "__main__":
    app.run(debug=True)
