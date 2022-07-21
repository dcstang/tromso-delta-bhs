from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
import progressbar
import numpy as np
import pandas as pd

def lasso_data_input(df, train_cols, outcome_col,
                     int_seed_number, test_set_ratio):

    X = df[train_cols].values
    y = df[outcome_col].values

    encoderPipe = Pipeline(steps=[
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan)),
    ])

    X = encoderPipe.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                        test_size=test_set_ratio, random_state=int_seed_number)

    return X_train, X_test, y_train, y_test

def lasso_callibration(X_train, y_train):

    trainPipe = Pipeline([
        ("imputer", SimpleImputer(missing_values=np.nan, strategy="most_frequent")),
        ("model", Lasso()),
    ])

    search = GridSearchCV(
        trainPipe,
        {'model__alpha':np.concatenate([np.linspace(0.01, 0.99, 50), np.arange(1,10,0.5)])},
        cv = 5, scoring="neg_mean_squared_error",verbose=1)

    search.fit(X_train,y_train)
    print(f"Gridsearch complete, best lambda: {search.best_params_}")

    coefficients = search.best_estimator_.named_steps['model'].coef_

    return coefficients

def lasso_stability(df, train_cols, outcome_col, test_set_ratio, n_iter=1):
    """
        Main function to run whole lasso pipeline, compiling all runs coefficients
        uses progressbar for ux
        returns a pandas DataFrame with number of columns as iterations
    """

    with progressbar.ProgressBar(max_value=n_iter+1) as bar:

        stabilityAnalysisDf = pd.DataFrame(
            {"variable":train_cols,
            1:np.zeros(len(train_cols))})

        for n in range(1,n_iter+1):    
            X_train, X_test, y_train, y_test = lasso_data_input(
                df=df, 
                train_cols=train_cols,
                outcome_col=outcome_col,
                int_seed_number=n,
                test_set_ratio=test_set_ratio
                )

            coefficients = lasso_callibration(X_train, y_train)
            stabilityAnalysisDf.loc[:,n] = coefficients
            bar.update(n)

        finalStabilityAnalysisDf = stabilityAnalysisDf.copy()
        finalStabilityAnalysisDf["pctSelected"] = finalStabilityAnalysisDf.loc[:,1:].gt(0).sum(axis=1).div(finalStabilityAnalysisDf.shape[1]-1).mul(100)
        finalStabilityAnalysisDf.sort_values(by="pctSelected", ascending=False, inplace=True)
        bar.update(n+1)

    return stabilityAnalysisDf

def callibrated_lasso(stabilityDf, df, outcome_col, selection_threshold=80,
                    random_seed=3000,test_set_ratio=0.3):

    selectedCols = stabilityDf[
        stabilityDf["pctSelected"]>= selection_threshold]["variable"].to_list()

    X_train, X_test, y_train, y_test = lasso_data_input(
                df=df, 
                train_cols=selectedCols,
                outcome_col=outcome_col,
                int_seed_number=random_seed,
                test_set_ratio=test_set_ratio
                )

    coefficients = lasso_callibration(X_train, y_train)
    outputDf = pd.DataFrame({
        "variable":selectedCols,
        "coef":coefficients
    })

    outputDf.sort_values(by="coef", ascending=False, inplace=True)

    return outputDf