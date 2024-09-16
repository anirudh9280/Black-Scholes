import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for rendering plots to files

from flask import Flask, request, render_template_string, url_for
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Define all functions globally
def blackScholes(S, K, r, T, sigma, type="c"):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if type == "c":
        price = S * norm.cdf(d1, 0, 1) - K * np.exp(-r * T) * norm.cdf(d2, 0, 1)
    elif type == "p":
        price = K * np.exp(-r * T) * norm.cdf(-d2, 0, 1) - S * np.exp(-r * T) * norm.cdf(-d1, 0, 1)

    return price

def optionDelta(S, K, r, T, sigma, type="c"):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    return norm.cdf(d1, 0, 1) if type == "c" else -norm.cdf(-d1, 0, 1)

def optionGamma(S, K, r, T, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    return norm.pdf(d1, 0, 1) / (S * sigma * np.sqrt(T))

def optionTheta(S, K, r, T, sigma, type="c"):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type == "c":
        theta = -((S * norm.pdf(d1, 0, 1) * sigma) / (2 * np.sqrt(T))) - r * K * np.exp(-r*T) * norm.cdf(d2, 0, 1)
    else:
        theta = -((S * norm.pdf(d1, 0, 1) * sigma) / (2 * np.sqrt(T))) + r * K * np.exp(-r*T) * norm.cdf(-d2, 0, 1)
    return theta / 365

def optionVega(S, K, r, T, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    return S * np.sqrt(T) * norm.pdf(d1, 0, 1) * 0.01

def optionRho(S, K, r, T, sigma, type="c"):
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type == "c":
        return 0.01 * K * T * np.exp(-r*T) * norm.cdf(d2, 0, 1)
    else:
        return -0.01 * K * T * np.exp(-r*T) * norm.cdf(-d2, 0, 1)

# Function to generate plot image and return it as a base64 string
def generate_plot(spot_prices, values, ylabel):
    plt.figure(figsize=(6,4))
    plt.plot(spot_prices, values, label=ylabel)
    plt.xlabel('Underlying Asset Price')
    plt.ylabel(ylabel)
    plt.title(f'{ylabel} vs Underlying Asset Price')
    plt.grid(True)

    # Save it to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    
    # Convert the image to a base64 string
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()  # Close the figure to free up memory

    return image_base64

@app.route('/', methods=["GET", "POST"])
def index():
    # Default values
    S = 30.00
    K = 50.00
    r = 0.03
    T = 1.0  # Time in years
    sigma = 0.30
    option_type = "c"  # Default is Call

    if request.method == "POST":
        # Get data from form inputs
        S = float(request.form.get("S", 30.00))
        K = float(request.form.get("K", 50.00))
        r = float(request.form.get("r", 0.03))
        T = float(request.form.get("T", 1.0))
        sigma = float(request.form.get("sigma", 0.30))
        option_type = request.form.get("type", "c")

    # Generate values for spot prices
    spot_prices = np.linspace(10, 100, 100)  # 100 points between 10 and 100

    # Calculate Greeks for the range of spot prices
    deltas = [optionDelta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    gammas = [optionGamma(SP, K, r, T, sigma) for SP in spot_prices]
    thetas = [optionTheta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    vegas = [optionVega(SP, K, r, T, sigma) for SP in spot_prices]
    rhos = [optionRho(SP, K, r, T, sigma, option_type) for SP in spot_prices]

    # Generate plots for each Greek and convert them to base64
    delta_plot = generate_plot(spot_prices, deltas, 'Delta')
    gamma_plot = generate_plot(spot_prices, gammas, 'Gamma')
    theta_plot = generate_plot(spot_prices, thetas, 'Theta')
    vega_plot = generate_plot(spot_prices, vegas, 'Vega')
    rho_plot = generate_plot(spot_prices, rhos, 'Rho')

    # Render the template with the form, results, and graphs
    return render_template_string('''
    <html>
        <head>
            <title>Black-Scholes Option Price Calculator</title>
            <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles.css') }}">
        </head>
        <body>
            <div class="container">
                <div class="main-content">
                    <h1>Black-Scholes Option Price and Greeks Calculator</h1>
                    <h2>Results:</h2>
                    <h3>Greeks vs Underlying Asset Price:</h3>
                    <div class="graph-grid">
                        <div>
                            <h4>Delta</h4>
                            <img src="data:image/png;base64,{{delta_plot}}" alt="Delta plot">
                        </div>
                        <div>
                            <h4>Gamma</h4>
                            <img src="data:image/png;base64,{{gamma_plot}}" alt="Gamma plot">
                        </div>
                        <div>
                            <h4>Theta</h4>
                            <img src="data:image/png;base64,{{theta_plot}}" alt="Theta plot">
                        </div>
                        <div>
                            <h4>Vega</h4>
                            <img src="data:image/png;base64,{{vega_plot}}" alt="Vega plot">
                        </div>
                        <div>
                            <h4>Rho</h4>
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
                        <input type="number" step="0.01" id="T" name="T" value="{{T}}" required>

                        <label for="sigma">Volatility (sigma):</label>
                        <input type="number" step="0.01" id="sigma" name="sigma" value="{{sigma}}" required>

                        <label for="type">Option Type:</label>
                        <select id="type" name="type">
                            <option value="c" {% if option_type == "c" %}selected{% endif %}>Call</option>
                            <option value="p" {% if option_type == "p" %}selected{% endif %}>Put</option>
                        </select>

                        <button type="submit">Calculate</button>
                    </form>
                </div>
            </div>
        </body>
    </html>
    ''', S=S, K=K, r=r, T=T, sigma=sigma, option_type=option_type,
    delta_plot=delta_plot, gamma_plot=gamma_plot, theta_plot=theta_plot, 
    vega_plot=vega_plot, rho_plot=rho_plot)

if __name__ == "__main__":
    app.run(debug=True)
