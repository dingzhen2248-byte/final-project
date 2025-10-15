from sklearn.linear_model import LinearRegression

def pred_linear_regression(X_train, y_train, X_test):
    """
    Train a Linear Regression model and make predictions.

    Parameters:
    X_train (array-like): Training feature data.
    y_train (array-like): Training target data.
    X_test (array-like): Test feature data.

    Returns:
    array-like: Predictions for the test data.
    """
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return predictions
