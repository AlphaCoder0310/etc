#!/usr/bin/env python
# coding: utf-8

# install the Eikon Python package
# !pip install eikon
# 
# obtain your eikon app key
# obtain your App Key from the Eikon API settings
# 
# understanding symbol naming
# Refinitiv uses specific symbol formats (RICs) for different instruments. Ensure that the symbols you provided are in the correct RIC format.

# Python Script to Retrieve Historical Data

# In[5]:


import eikon as ek
import pandas as pd
from datetime import datetime, timedelta

# Step 1: Set Your Eikon App Key
# Replace 'YOUR_APP_KEY_HERE' with your actual Eikon App Key.
ek.set_app_key('YOUR_APP_KEY_HERE')

# Step 2: Define the List of Symbols
# Ensure that futures symbols are in the correct RIC format.
symbols = [
    '0700.HK',         # Tencent Holdings Limited
    'HSI.F',           # Hang Seng Index Futures (Example RIC, verify the exact one)
    'HSCE.F',          # Hang Seng China Enterprises Index Futures (Example RIC)
    'HSTECH.F'         # Hang Seng TECH Index Futures (Example RIC)
]

# **Note**: The futures RICs provided above (`HSI.F`, `HSCE.F`, `HSTECH.F`) are examples.
# Please verify and replace them with the correct RICs as per your Refinitiv Eikon subscription.

# Step 3: Define the Timeframe
# To get the past 60 trading days, it's safe to go back about 90 calendar days
# to account for weekends and holidays.
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# Step 4: Retrieve the Historical Data
try:
    # Fetch daily closing prices for the specified symbols
    df = ek.get_timeseries(
        symbols,
        fields=['CLOSE'],
        start_date=start_date,
        end_date=end_date,
        interval='daily'
    )
    
    # Reset index to have 'Date' as a column
    df.reset_index(inplace=True)
    
    # Sort data by Date just in case
    df.sort_values('Date', inplace=True)
    
    # Step 5: Filter the Last 60 Trading Days
    # Drop rows where all CLOSE values are NaN
    df.dropna(how='all', subset=symbols, inplace=True)
    
    # Get the last 60 available trading days
    df_last_60 = df.tail(60)
    
    # Optional: Pivot the data for better readability
    df_pivot = df_last_60.pivot(index='Date', columns=None, values=symbols)
    
    # Display the DataFrame
    print("Last 60 Trading Days of Closing Prices:")
    print(df_pivot)
    
    # Optional: Save to CSV
    # df_pivot.to_csv('historical_stock_prices.csv')
    
except ek.eikonError.EikonError as e:
    print("An error occurred while fetching data from Eikon API:")
    print(e)
    
except Exception as ex:
    print("An unexpected error occurred:")
    print(ex)    


# In[ ]:


import eikon as ek
import pandas as pd
from datetime import datetime, timedelta

# Initialize Eikon with your API key
ek.set_app_key('your_eikon_api_key')

# Define the instruments
instruments = ["0700.HK", "HSI", "HSCE", "HSTECH"]

# Define the fields to retrieve
fields = ["TR.OPENPRICE", "TR.ADJUSTEDCLOSE", "VOLUME"]  # Adjusted close, open, high, low

# Define the time range (last 60 trading days)
end_date = datetime.today().strftime('%Y-%m-%d')  # Today's date
start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')  # Approx. 60 trading days (allow for weekends and holidays)

# Retrieve data for each instrument
historical_data = {}

try:
    for instrument in instruments:
        print(f"Retrieving data for: {instrument}")
        # Use `get_timeseries` to fetch historical data
        data = ek.get_timeseries(
            instrument,
            fields=fields,
            start_date=start_date,
            end_date=end_date,
            interval="daily"
        )
        
        # Store the data in a dictionary with the instrument as the key
        historical_data[instrument] = data
        print(f"Data for {instrument} retrieved successfully!\n")
        
except ek.EikonError as e:
    print(f"Error retrieving data: {e}")

# Combine all data into a single DataFrame (optional)
combined_data = pd.concat(historical_data, axis=1)

# Save to CSV (optional)
combined_data.to_csv('adjusted_close_data.csv')

# Print a preview of the data
print(combined_data.head())


# In[33]:


import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Define the instruments (YFinance tickers)
instruments = {
    "0700.HK": "0700.HK",       # Tencent Holdings
    "HSI FUTURES": "^HSI",      # Hang Seng Index (Index proxy, not futures)
    "HSCE FUTURES": "^HSCE",    # Hang Seng China Enterprises Index
    "HSTECH FUTURES": "^HSTECH" # Hang Seng TECH Index
}

# Define the time range (last 60 trading days, approx. 90 calendar days)
end_date = datetime.today()
start_date = end_date - timedelta(days=360)

# Retrieve and process data for each instrument
historical_data = {}

for name, ticker in instruments.items():
    print(f"Retrieving data for: {name} ({ticker})")
    
    # Fetch the data using yfinance
    data = yf.download(
        ticker, 
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval="1d"  # Daily interval
    )
    
    if not data.empty:
        # Select the required fields: Open, Adj Close
        data = data[["Open", "Adj Close"]]
        
        # Calculate the T-1 close to T open log return
        data = data.copy()
        data[f"{name}_Log_Return"] = np.log(data["Open"] / data["Adj Close"].shift(1))
        
        # Add the instrument name to the column names for clarity
        data.columns = [f"{name}_{col}" if col != f"{name}_Log_Return" else col for col in data.columns]
        historical_data[name] = data
        print(f"Data for {name} retrieved and processed successfully!")
    else:
        print(f"No data found for {name}. Skipping.\n")

# Combine all data into a single DataFrame
if historical_data:
    combined_data = pd.concat(historical_data.values(), axis=1)
    # Drop rows with NaN values in any Log_Return column
    combined_data = combined_data.dropna(subset=["0700.HK_Log_Return", "HSI FUTURES_Log_Return", "HSCE FUTURES_Log_Return"])

    print("\nCombined Data:")
    print(combined_data.head())

    # Save the combined data to CSV (optional)
    combined_data.to_csv('historical_data_with_log_returns.csv')
    print("\nSaved combined data to 'historical_data_with_log_returns.csv'.")
else:
    print("No data retrieved for any instruments.")


# In[34]:


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
# Step 1: Separate the target variable and predictors
# Target variable
y = combined_data["0700.HK_Log_Return"]

# Predictors
X = combined_data[["HSI FUTURES_Log_Return", "HSCE FUTURES_Log_Return"]]

# Step 2: Standardize the data
scaler_X = StandardScaler()
scaler_y = StandardScaler()

# Fit and transform X (predictors)
X_scaled = scaler_X.fit_transform(X)

# Fit and transform y (target)
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))  # Reshape y to a 2D array

# Convert back to DataFrame for easier handling
X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
y_scaled = pd.Series(y_scaled.flatten(), index=y.index)


# In[35]:


# Step 3: Perform correlation analysis
correlation_matrix = X_scaled.corr()
print("Correlation Matrix:")
print(correlation_matrix)

# Optional: Format correlation as lower triangle
def lower_triangle_corr(matrix):
    mask = np.triu(np.ones_like(matrix, dtype=bool))
    lower_triangle = matrix.mask(mask)
    return lower_triangle

print("Lower Triangle Correlation:")
print(lower_triangle_corr(correlation_matrix))


# In[19]:


# # Format the correlation into a lower triangle
# import numpy as np

# def lower_triangle_corr(matrix):
#     mask = np.triu(np.ones_like(matrix, dtype=bool))
#     lower_triangle = matrix.mask(mask)
#     return lower_triangle

# lower_triangle = lower_triangle_corr(correlation_matrix)
# print(lower_triangle)


# In[ ]:


# # Step 4: Split the dataset
# X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.3, random_state=42)


# In[36]:


def successive_orthogonalization(X, y):
    """
    Perform linear regression by successive orthogonalization.
    
    Parameters:
        X (pd.DataFrame): Predictor variables (columns are predictors).
        y (pd.Series): Target variable.
        
    Returns:
        coefficients (dict): Regression coefficients for each predictor.
        z_vectors (list): List of orthogonalized predictors (z vectors).
    """
    # Ensure X and y are numpy arrays
    X = X.values
    y = y.values.reshape(-1, 1)  # Reshape y for matrix operations

    # Step A: Initialization
    n, p = X.shape
    z_vectors = []  # List to store orthogonalized predictors
    z_vectors.append(np.ones((n, 1)))  # z0 = 1 (intercept)

    # Step B: Orthogonalization Process
    for j in range(p):
        # Current predictor xj
        xj = X[:, j].reshape(-1, 1)

        # Regress xj on all previous z vectors
        projection = np.zeros_like(xj)
        for z in z_vectors:
            # Calculate projection of xj onto z
            blj_hat = (z.T @ xj) / (z.T @ z)  # <zl, xj> / <zl, zl>
            projection += blj_hat * z

        # Residual vector zj (xj minus its projections on previous z vectors)
        zj = xj - projection

        # Add zj to the list of z vectors
        z_vectors.append(zj)

    # Step C: Final Regression
    Z = np.hstack(z_vectors)  # Combine all z vectors into a single matrix
    coefficients = np.linalg.inv(Z.T @ Z) @ Z.T @ y  # Calculate regression coefficients

    # Format coefficients as a dictionary
    coef_dict = {f"z{i}": coeff[0] for i, coeff in enumerate(coefficients)}

    return coef_dict, z_vectors


# In[37]:


# Example Data
# Assuming X and y have already been standardized
X = pd.DataFrame({
    "HSI_Futures_Log_Return": X_scaled["HSI FUTURES_Log_Return"],
    "HSCE_Futures_Log_Return": X_scaled["HSCE FUTURES_Log_Return"]
})
y = y_scaled

# Perform orthogonalization linear regression
coefficients, z_vectors = successive_orthogonalization(X, y)

# Print the regression coefficients
print("Orthogonalized Regression C`oefficients:")
print(coefficients)


# - z0 is the intercept.
# - z1 is the unique contribution of HSI_Futures_Log_Return.
# - z2 is the unique contribution of HSCE_Futures_Log_Return.
# 
# Benefits of Orthogonalization
# - Isolates Unique Contributions:
#     - Each coefficient represents the contribution of a predictor after adjusting for others.
# - Handles Multicollinearity:
#     - By orthogonalizing predictors, the method reduces the impact of multicollinearity, which can destabilize traditional regression.
# - Efficient Computation:
#     - Successive orthogonalization simplifies the regression process by decorrelating inputs.
# - 	A. correlation issue: if xp is highly correlated with other prediction, the residual zp becomes very small
# 		a. residual vector: zp represents the portion of xp not explained by other predictors
# 		b. a small zp suggests xp is mostly redundant with other predictors

# In[51]:


def ridge_regression_with_orthogonalization(X, y, lambdas, k=10):
    """
    Perform ridge regression on orthogonalized predictors using k-fold cross-validation.
    Parameters:
    X (pd.DataFrame): Predictor variables.
    y (pd.Series): Target variable.
    lambdas (list): List of ridge penalty values (lambda) to test.
    k (int): Number of folds for cross-validation.
    Returns:
    ridge_coefficients (list): Ridge coefficients for each lambda.
    prediction_errors (list): Cross-validated prediction errors for each lambda.
    dfs (list): Effective degrees of freedom for each lambda.
    """
    n, p = X.shape # Number of observations and predictors

    # Step 1: Orthogonalize the predictors
    z_vectors = []  # Store orthogonalized predictors
    z_vectors.append(np.ones((n, 1)))  # Intercept (not penalized)

    # Orthogonalization process
    for j in range(p):
        xj = X.iloc[:, j].values.reshape(-1, 1)
        projection = np.zeros_like(xj)
        for z in z_vectors:
            blj_hat = (z.T @ xj) / (z.T @ z)  # Projection coefficient
            projection += blj_hat * z
        zj = xj - projection  # Residual vector
        z_vectors.append(zj)

    Z = np.hstack(z_vectors[1:])  # Combine orthogonalized predictors (exclude intercept)

    # Step 2: Ridge Regression with Cross-Validation
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    ridge_coefficients = []
    prediction_errors = []
    dfs = []

    for lmbda in lambdas:
        fold_errors = []
        fold_coefficients = []

        for train_idx, test_idx in kf.split(Z):
            Z_train, Z_test = Z[train_idx], Z[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Ridge regression (fit without intercept)
            ridge = Ridge(alpha=lmbda, fit_intercept=False)
            ridge.fit(Z_train, y_train)

            # Evaluate on the test set
            y_pred = ridge.predict(Z_test)
            fold_errors.append(mean_squared_error(y_test, y_pred))
            fold_coefficients.append(ridge.coef_)

        # Average prediction error and coefficients across folds
        avg_error = np.mean(fold_errors)
        avg_coefficients = np.mean(fold_coefficients, axis=0)

        # Compute effective degrees of freedom
        SVD = np.linalg.svd(Z, full_matrices=False)
        singular_values = SVD[1]  # Singular values of Z
        df_lambda = np.sum(singular_values**2 / (singular_values**2 + lmbda))

        prediction_errors.append(avg_error)
        ridge_coefficients.append(avg_coefficients)
        dfs.append(df_lambda)

    return ridge_coefficients, prediction_errors, dfs


# In[53]:


lambdas = np.logspace(-3, 3, 100) # Test lambdas from 0.001 to 1000
ridge_coefficients, prediction_errors, dfs = ridge_regression_with_orthogonalization(X, y, lambdas)


# In[56]:


plt.figure(figsize=(10, 6))
for i, coef in enumerate(np.array(ridge_coefficients).T):
    plt.plot(dfs, coef, label=f"z{i+1}")
    plt.xlabel("Effective Degrees of Freedom (df(lambda))")
    plt.ylabel("Ridge Coefficients")
    plt.title("Ridge Coefficients vs df(lambda)")
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()


# In[57]:


plt.figure(figsize=(10, 6))
plt.plot(dfs, prediction_errors, label="Prediction Error")
plt.xlabel("Effective Degrees of Freedom (df(lambda))")
plt.ylabel("Cross-Validated Prediction Error")
plt.title("Prediction Error Curve")
plt.legend(loc="best")
plt.grid(True)
plt.show()


# In[59]:


# Step 6: Find the optimal lambda and corresponding effective degrees of freedom
optimal_lambda_idx = np.argmin(prediction_errors)  # Index of minimum prediction error
optimal_lambda = lambdas[optimal_lambda_idx]       # Optimal lambda
optimal_df = dfs[optimal_lambda_idx]               # Effective degrees of freedom for optimal lambda

print(f"Optimal Lambda (ridge penalty): {optimal_lambda}")
print(f"Effective Degrees of Freedom for Optimal Lambda: {optimal_df}")

# Step 7: Ridge estimates for orthonormal inputs
# For orthonormal inputs, ridge estimates are scaled least squares estimates
ridge_coefficients_np = np.array(ridge_coefficients)  # Convert to numpy array
optimal_ridge_coefficients = ridge_coefficients_np[optimal_lambda_idx, :]
print(f"Ridge Coefficients for Optimal Lambda: {optimal_ridge_coefficients}")

# # Compute scaled ridge coefficients for orthonormal inputs
# # For simplicity, assume least squares estimates (beta_ls) are the ridge coefficients with lambda=0
# beta_ls = ridge_coefficients_np[0, :]  # Coefficients at lambda = 0
# ridge_scaled_coefficients = beta_ls / (1 + optimal_lambda)
# print(f"Scaled Ridge Coefficients (orthonormal inputs): {ridge_scaled_coefficients}")

# Step 8: Plot Prediction Error Curve with Optimal Lambda Highlighted
plt.figure(figsize=(10, 6))
plt.plot(dfs, prediction_errors, label="Prediction Error")
plt.axvline(optimal_df, color="red", linestyle="--", label=f"Optimal df(lambda) = {optimal_df:.2f}")
plt.xlabel("Effective Degrees of Freedom (df(lambda))")
plt.ylabel("Cross-Validated Prediction Error")
plt.title("Prediction Error Curve with Optimal Lambda Highlighted")
plt.legend(loc="best")
plt.grid(True)
plt.show()

# Step 9: Plot Ridge Coefficients with Optimal Lambda Highlighted
plt.figure(figsize=(10, 6))
for i, coef in enumerate(np.array(ridge_coefficients).T):
    plt.plot(dfs, coef, label=f"z{i+1}")
plt.axvline(optimal_df, color="red", linestyle="--", label=f"Optimal df(lambda) = {optimal_df:.2f}")
plt.xlabel("Effective Degrees of Freedom (df(lambda))")
plt.ylabel("Ridge Coefficients")
plt.title("Ridge Coefficients vs df(lambda) with Optimal Highlighted")
plt.legend(loc="best")
plt.grid(True)
plt.show()


# In[ ]:




