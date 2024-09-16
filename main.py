from flask import Flask, request, render_template_string
import numpy as np
from scipy.stats import norm

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

    # Calculate Option Price and Greeks
    option_price = blackScholes(S, K, r, T, sigma, option_type)
    delta = optionDelta(S, K, r, T, sigma, option_type)
    gamma = optionGamma(S, K, r, T, sigma)
    theta = optionTheta(S, K, r, T, sigma, option_type)
    vega = optionVega(S, K, r, T, sigma)
    rho = optionRho(S, K, r, T, sigma, option_type)

    # Render the template with the form and calculated results
    return render_template_string('''
    <html>
        <head>
            <title>Black-Scholes Option Price Calculator</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0 auto;
                    max-width: 800px;
                    padding: 20px;
                    background-color: #f4f4f4;
                }
                input, select {
                    width: 100%;
                    padding: 10px;
                    margin: 8px 0;
                    display: inline-block;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                button {
                    width: 100%;
                    background-color: #4CAF50;
                    color: white;
                    padding: 14px 20px;
                    margin: 8px 0;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>Black-Scholes Option Price and Greeks Calculator</h1>
            <form method="POST">
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

            <h2>Results:</h2>
            <p>Option Price: {{option_price}}</p>
            <p>Delta: {{delta}}</p>
            <p>Gamma: {{gamma}}</p>
            <p>Theta: {{theta}}</p>
            <p>Vega: {{vega}}</p>
            <p>Rho: {{rho}}</p>
        </body>
    </html>
    ''', S=S, K=K, r=r, T=T, sigma=sigma, option_type=option_type, 
    option_price=round(option_price, 4), delta=round(delta, 4), 
    gamma=round(gamma, 4), theta=round(theta, 4), vega=round(vega, 4), rho=round(rho, 4))

if __name__ == "__main__":
    app.run(debug=True)
