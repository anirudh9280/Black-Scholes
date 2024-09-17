import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for non-GUI environments
from flask import Flask, request, render_template_string, url_for, make_response
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Black-Scholes formula
def blackScholes(S, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    try:
        if option_type == "call":
            price = S * norm.cdf(d1, 0, 1) - K * np.exp(-r * T) * norm.cdf(d2, 0, 1)
        elif option_type == "put":
            price = K * np.exp(-r * T) * norm.cdf(-d2, 0, 1) - S * norm.cdf(-d1, 0, 1)
        return price
    except:
        return None

# Delta
def delta(S, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    try:
        if option_type == "call":
            delta = norm.cdf(d1, 0, 1)
        elif option_type == "put":
            delta = -norm.cdf(-d1, 0, 1)
        return delta
    except:
        return None

# Gamma
def gamma(S, K, r, T, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    try:
        gamma = norm.pdf(d1, 0, 1) / (S * sigma * np.sqrt(T))
        return gamma
    except:
        return None

# Theta
def theta(S, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    try:
        if option_type == "call":
            theta = -((S * norm.pdf(d1, 0, 1) * sigma) / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * norm.cdf(d2, 0, 1)
        elif option_type == "put":
            theta = -((S * norm.pdf(d1, 0, 1) * sigma) / (2 * np.sqrt(T))) + r * K * np.exp(-r * T) * norm.cdf(-d2, 0, 1)
        return theta / 365  # Convert to per-day theta
    except:
        return None

# Vega
def vega(S, K, r, T, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    try:
        vega = S * np.sqrt(T) * norm.pdf(d1, 0, 1) * 0.01  # Vega per 1% change in volatility
        return vega
    except:
        return None

# Rho
def rho(S, K, r, T, sigma, option_type="call"):
    d2 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T)) - sigma * np.sqrt(T)
    try:
        if option_type == "call":
            rho = 0.01 * K * T * np.exp(-r * T) * norm.cdf(d2, 0, 1)
        elif option_type == "put":
            rho = -0.01 * K * T * np.exp(-r * T) * norm.cdf(-d2, 0, 1)
        return rho
    except:
        return None

# Function to generate plot image and return it as a base64 string
def generate_plot(spot_prices, values, ylabel, theme):
    buf = io.BytesIO()
    # Choose colors based on theme
    if theme == 'dark':
        line_color = '#ff9f80'  # Light coral for dark background
        bg_color = '#2e2e2e'    # Dark background
        grid_color = '#555555'
        text_color = '#f0f0f0'
    else:
        line_color = '#ff6f61'  # Coral for light background
        bg_color = '#ffffff'    # Light background
        grid_color = '#cccccc'
        text_color = '#333333'

    plt.figure(figsize=(5, 3), facecolor=bg_color)
    plt.plot(spot_prices, values, color=line_color, linewidth=2)
    plt.fill_between(spot_prices, values, color=line_color, alpha=0.3)
    plt.xlabel('Stock Price', color=text_color)
    plt.ylabel(ylabel, color=text_color)
    plt.title(f'{ylabel} vs Stock Price', color=text_color)
    plt.grid(True, linestyle='--', linewidth=0.5, color=grid_color)
    plt.tight_layout()
    plt.style.use('classic')
    ax = plt.gca()
    ax.set_facecolor(bg_color)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)
    plt.savefig(buf, format='png', dpi=100, facecolor=bg_color)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return image_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    # Updated default values
    S = 30.00
    K = 50.00
    r = 0.03
    T_days = 250  # Time in days
    sigma = 0.30
    option_type = 'call'  # Default is Call

    theme = request.cookies.get('theme', 'dark')  # Default theme is now dark

    if request.method == 'POST':
        # Get data from form inputs
        S = float(request.form.get('S', S))
        K = float(request.form.get('K', K))
        r = float(request.form.get('r', r))
        T_days = float(request.form.get('T', T_days))
        sigma = float(request.form.get('sigma', sigma))
        option_type = request.form.get('type', option_type)

    T = T_days / 365  # Convert days to years

    # Calculate the Greeks and Option Price
    option_price = round(blackScholes(S, K, r, T, sigma, option_type), 4)
    delta_value = round(delta(S, K, r, T, sigma, option_type), 4)
    gamma_value = round(gamma(S, K, r, T, sigma), 4)
    theta_value = round(theta(S, K, r, T, sigma, option_type), 4)
    vega_value = round(vega(S, K, r, T, sigma), 4)
    rho_value = round(rho(S, K, r, T, sigma, option_type), 4)

    # Generate values for spot prices
    spot_prices = np.linspace(0.01, S + 50, 100)

    # Calculate Greeks and Option Price for plotting
    prices = [blackScholes(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    deltas = [delta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    gammas = [gamma(SP, K, r, T, sigma) for SP in spot_prices]
    thetas = [theta(SP, K, r, T, sigma, option_type) for SP in spot_prices]
    vegas = [vega(SP, K, r, T, sigma) for SP in spot_prices]
    rhos = [rho(SP, K, r, T, sigma, option_type) for SP in spot_prices]

    # Generate plots for each Greek and the option price
    price_plot = generate_plot(spot_prices, prices, 'Option Price', theme)
    delta_plot = generate_plot(spot_prices, deltas, 'Delta', theme)
    gamma_plot = generate_plot(spot_prices, gammas, 'Gamma', theme)
    theta_plot = generate_plot(spot_prices, thetas, 'Theta', theme)
    vega_plot = generate_plot(spot_prices, vegas, 'Vega', theme)
    rho_plot = generate_plot(spot_prices, rhos, 'Rho', theme)

    # Render the template with the form, results, and graphs
    response = make_response(render_template_string('''
<!DOCTYPE html>
<html>
    <head>
        <title>Black-Scholes Option Price Calculator</title>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles.css') }}">
        <script>
            function setTheme(theme) {
                document.body.classList.toggle("dark-mode", theme === "dark");
                document.querySelectorAll("button, input, select, h1, h3, label").forEach(el => el.classList.toggle("dark-mode", theme === "dark"));
                document.getElementById("theme-toggle-icon").textContent = theme === "dark" ? "☀️" : "🌙";
                localStorage.setItem("theme", theme);
                document.cookie = "theme=" + theme + "; path=/";
            }

            document.addEventListener("DOMContentLoaded", function() {
                const currentTheme = localStorage.getItem("theme") || "dark";  // Default theme is now dark
                setTheme(currentTheme);

                document.getElementById("theme-toggle").addEventListener("click", function() {
                    const newTheme = document.body.classList.contains("dark-mode") ? "light" : "dark";
                    setTheme(newTheme);
                    // Reload the page to update images
                    location.reload();
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <div class="main-content">
                <button id="theme-toggle">
                    <span id="theme-toggle-icon">🌙</span>
                </button>
                <div class="center">
                    <h1>Black-Scholes Option Price and Greeks Calculator</h1>
                    <!-- Display the calculated option price and Greeks -->
                    <h3>{{ option_type.capitalize() }} Price: {{ option_price }}</h3>
                    <h3>Delta: {{ delta_value }}</h3>
                    <h3>Gamma: {{ gamma_value }}</h3>
                    <h3>Theta: {{ theta_value }}</h3>
                    <h3>Vega: {{ vega_value }}</h3>
                    <h3>Rho: {{ rho_value }}</h3>
                </div>
                <h3 class="center">Greeks and Option Price vs Stock Price:</h3>
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
                    <label for="S">Stock Price (S):</label>
                    <input type="number" step="0.01" id="S" name="S" value="{{S}}" required>

                    <label for="K">Strike Price (K):</label>
                    <input type="number" step="0.01" id="K" name="K" value="{{K}}" required>

                    <label for="r">Interest Rate (r):</label>
                    <input type="number" step="0.001" id="r" name="r" value="{{r}}" required>

                    <label for="T">Time to Expiry Date (in days):</label>
                    <input type="number" step="1" id="T" name="T" value="{{T_days}}" required>

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
''', S=S, K=K, r=r, T_days=T_days, sigma=sigma, option_type=option_type,
     option_price=option_price, delta_value=delta_value, gamma_value=gamma_value,
     theta_value=theta_value, vega_value=vega_value, rho_value=rho_value,
     delta_plot=delta_plot, gamma_plot=gamma_plot, theta_plot=theta_plot,
     vega_plot=vega_plot, rho_plot=rho_plot, price_plot=price_plot))

    return response

if __name__ == "__main__":
    app.run(debug=True)
