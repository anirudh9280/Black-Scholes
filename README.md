# Black-Scholes Option Pricing Calculator

## Access the Live Application

Access the live application [here](https://blackscholesapp-e835e285f907.herokuapp.com/).

## Overview

This is a web application that calculates the Black-Scholes option price and the Greeks (Delta, Gamma, Theta, Vega, Rho) for European call and put options. The calculator allows users to input parameters such as stock price, exercise price, interest rate, time to maturity, volatility, and option type. It provides both numerical results and graphical representations of the option price and Greeks with respect to the underlying stock price.

### Features

- **Option Pricing:** Calculate the Black-Scholes price for European call and put options.
- **Greeks Calculation:** Compute the option Greeks—Delta, Gamma, Theta, Vega, and Rho.
- **Interactive Graphs:** Visualize how the option price and Greeks change with the underlying stock price.
- **User-Friendly Interface:** Input parameters are conveniently placed on the sidebar.
- **Dark Mode Support:** Toggle between light and dark themes for comfortable viewing.

### About the Black-Scholes Model

The Black-Scholes model provides a mathematical framework for evaluating the price of European options. It’s based on the assumption that the price of the underlying asset follows a geometric Brownian motion with constant drift and volatility.

### Key Assumptions

- The option is European and can only be exercised at expiration.
- Markets are efficient, and there are no transaction costs.
- The risk-free interest rate and volatility of the underlying asset are known and constant.
- The returns on the underlying asset are normally distributed.

### Mathematical Formulas

The Black-Scholes model is a mathematical model for pricing an options contract by determining the theoretical value for European-style options. The model incorporates the key factors that influence an option’s price.

### Black-Scholes Option Pricing Formula

For a European call option:

$$
C(S, t) = S N(d_1) - K e^{-r(T)} N(d_2)
$$

For a European put option:

$$
P(S, t) = K e^{-r(T)} N(-d_2) - S N(-d_1)
$$

Where:
$$
- \( S \) = Current stock price
- \( K \) = Exercise price (strike price)
- \( r \) = Risk-free interest rate
- \( T \) = Time to maturity (in years)
- \( \sigma \) = Volatility of the underlying asset
- \( N(\cdot) \) = Cumulative distribution function of the standard normal distribution

The variables \( d_1 \) and \( d_2 \) are calculated as:

d_1 = \frac{\ln\left(\frac{S}{K}\right) + \left( r + \frac{\sigma^2}{2} \right)(T)}{\sigma \sqrt{T}}

$$

$$
d_2 = d_1 - \sigma \sqrt{T}
$$

### Option Greeks

**Delta (\( \Delta \))**

Measures the sensitivity of the option price to a $1 change in the price of the underlying asset.

- **Call Option:**

$$
\Delta_{\text{call}} = N(d_1)
$$

- **Put Option:**

$$
\Delta_{\text{put}} = N(d_1) - 1
$$

**Gamma ( Γ )**

Measures the rate of change in Delta with respect to changes in the underlying asset price.

$$
\Gamma = \frac{N'(d_1)}{S \sigma \sqrt{T}}
$$

Where $( N'(d_1))$ is the probability density function of the standard normal distribution.

**Theta ($\Theta$)**

Measures the sensitivity of the option price to the passage of time (time decay).

- **Call Option:**

$$
\Theta_{\text{call}} = -\frac{S N'(d_1) \sigma}{2 \sqrt{T}} - r K e^{-r(T)} N(d_2)
$$

- **Put Option:**

$$
\Theta_{\text{put}} = -\frac{S N'(d_1) \sigma}{2 \sqrt{T}} + r K e^{-r(T)} N(-d_2)
$$

**Vega ($\nu$)**

Measures the sensitivity of the option price to changes in the volatility of the underlying asset.

$$
\nu = S \sqrt{T} N'(d_1)
$$

**Rho (\( \rho \))**

Measures the sensitivity of the option price to changes in the risk-free interest rate.

- **Call Option:**

$$
\rho_{\text{call}} = K (T) e^{-r(T)} N(d_2)
$$

- **Put Option:**

$$
\rho_{\text{put}} = -K (T) e^{-r(T)} N(-d_2)
$$

## Accessing the Application

The application is deployed on Heroku and can be accessed via the following link:

[https://blackscholesapp-e835e285f907.herokuapp.com/](https://blackscholesapp-e835e285f907.herokuapp.com/)

## Running the Project Locally

To run this project on your local machine, follow these steps:

### Prerequisites

- **Python 3.x:** Ensure that Python is installed on your system.
- **pip:** Python package installer should be available.
- **Virtual Environment (optional but recommended):** For isolating dependencies.

### Instructions

1. **Clone the Repository**

   Open your terminal and run:

git clone https://github.com/your-username/black-scholes-calculator.git
cd black-scholes-calculator

2. **Install Dependencies**
Install the required Python packages using pip:
pip install -r requirements.txt

3. **Run the App**
python main.py


## Disclaimer

This calculator is intended for educational purposes and should not be used as a sole resource for investment decisions. Always consult a financial professional before making investment choices.

## Acknowledgements

- **Libraries Used:**
- Flask: For the web application framework.
- NumPy: For numerical computations.
- SciPy: For statistical functions.
- Matplotlib: For plotting graphs.
- **Inspiration:** This project was inspired by the need for a simple, accessible tool to demonstrate the principles of options pricing using the Black-Scholes model.

Feel free to contribute to this project by opening issues or submitting pull requests on GitHub.
