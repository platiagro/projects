import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class Correlation(BaseEstimator, TransformerMixin):
    """Feature selector that removes correlated features.
    
    This feature selection algorithm looks only at features(X) and 
    and removes those with high correlation.
    
    Attributes:
        categorical_indexes: a np.ndarray of categoricals indexes.
        cutoff: float of cutoff.
        drop_indexes: list of indexes to be droped.
    """

    def __init__(self, categorical_indexes: np.ndarray, cutoff: float):
        """Inits Correlation class.
        
        Args:
            categorical_indexes: categorical indexes of X.
            cutoff: cutoff value.
        """
        self.categorical_indexes = categorical_indexes
        self.cutoff = cutoff
    
    def transform(self, X) -> np.ndarray:
        """Reduce X to the selected features.
        
        Args:
            X: the input samples.
            
        Returns:
            np.ndarray: the input samples without only the selected features.
        """
        if not self.drop_indexes:
            return X

        return np.delete(X, np.unique(self.drop_indexes), axis=1)
    
    def get_support(self) -> np.ndarray:
        """Returns a list of indexes to be removed.

        Returns:
            np.ndarray: indexes removed by the model.
        """
        return np.unique(self.drop_indexes).astype(int)
    
    def fit(self, X: np.ndarray, y=None) -> np.ndarray:
        """Fit the model. Learn correlated features from X.

        Args:
            X: the imput sample.
        
        Returns:
            self
        """
        # get only numerical values from X
        X_numerical = np.delete(X, self.categorical_indexes, axis=1)

        # check the shape of input
        if np.ma.size(X_numerical, axis=0) <= 1 \
        or np.ma.size(X_numerical, axis=1) <= 1:
            self.drop_indexes = []
            return self

        # correlation matrix
        corr_matrix = np.abs(np.corrcoef(X_numerical.astype(float), rowvar=False))

        # mean correlation for each column
        mean_corr = np.mean(corr_matrix, axis=1)

        # pairwise correlations above cutoff
        above_cutoff = np.argwhere(np.triu(corr_matrix, k=1) > self.cutoff)

        # for each pairwise correlation above cutoff
        # remove the feature with the highest mean correlation 
        self.drop_indexes = [
            above_cutoff[i, np.argmax(pair)] 
            for i, pair in enumerate(mean_corr[above_cutoff])]

        return self
