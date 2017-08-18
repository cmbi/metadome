'''
Module Description:
 This module specifies metrics that can be used for various evaluations
 
@author: Laurens van de wiel
'''

import numpy as np
from sklearn.metrics import mean_squared_error, explained_variance_score, mean_absolute_error, roc_curve, auc, confusion_matrix,  accuracy_score, precision_score, recall_score, f1_score

def MedianAbsoluteDeviation(data, axis=None):
    """Computes the median absolute deviation (MAD): a robust measure 
    of the variability of a univariate sample of quantitative data. It 
    can also refer to the population parameter that is estimated by the
    MAD calculated from a sample."""
    return np.median(np.absolute(data - np.median(data, axis)), axis)

def MedianAbsoluteDeviation_permutation(data, permuted_data, axis=None):
    """Computes the median absolute deviation (MAD) using a custom 
    data sample, useful for permutations in order to calculate 
    significance"""
    return np.median(np.absolute(data - np.median(permuted_data, axis)), axis)

def NormalisedRootMeanSquaredError(y_true, y_pred, y_min, y_max):
    '''A non-dimensional form of the RMSE, useful for comparing RMSE scores with different units.'''
    RMSE = RootMeanSquaredError(y_true, y_pred)
    NRMSE = RMSE / (y_max - y_min)
    
    return NRMSE

def MeanSquaredError(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)

def RootMeanSquaredError(y_true, y_pred):
    return np.sqrt(MeanSquaredError(y_true, y_pred))

def MeanAbsoluteError(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def ExplainedVarianceScore(y_true, y_pred):
    return explained_variance_score(y_true, y_pred)

def Accuracy(y_true, y_pred):
    return accuracy_score(y_true, y_pred)

def ConfusionMatrix(yTrue, yPred):
    cfm = confusion_matrix(yTrue, yPred)
    return cfm
   
def AreaUnderTheCurve(yTrue, yPred):
    fpr, tpr, _ = roc_curve(yTrue, yPred)
    AUC = auc(fpr, tpr)
    return AUC, fpr, tpr

def WeightedPrecision(yTrue, yPred):
    '''Calculate metrics for each label, and find their average, weighted by support (the number of true instances for each label). This alters 'macro' to account for label imbalance'''
    p = precision_score(yTrue, yPred, average='weighted')
    return p

def MicroPrecision(yTrue, yPred):
    '''Calculate metrics globally by counting the total true positives, false negatives and false positives.'''
    p = precision_score(yTrue, yPred, average='micro')
    return p

def MacroPrecision(yTrue, yPred):
    '''Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account.'''
    p = precision_score(yTrue, yPred, average='macro')
    return p

def PrecisionPerClass(yTrue, yPred):
    '''the scores for each class are returned'''
    p = precision_score(yTrue, yPred, average=None)
    return p

def WeightedRecall(yTrue, yPred):
    '''Calculate metrics for each label, and find their average, weighted by support (the number of true instances for each label). This alters 'macro' to account for label imbalance'''
    r = recall_score(yTrue, yPred, average='weighted')
    return r

def MicroRecall(yTrue, yPred):
    '''Calculate metrics globally by counting the total true positives, false negatives and false positives.'''
    r = recall_score(yTrue, yPred, average='micro')
    return r

def MacroRecall(yTrue, yPred):
    '''Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account.'''
    r = recall_score(yTrue, yPred, average='macro')
    return r

def RecallPerClass(yTrue, yPred):
    '''the scores for each class are returned'''
    r = recall_score(yTrue, yPred, average=None)
    return r

def WeightedF1Score(yTrue, yPred):
    '''Calculate metrics for each label, and find their average, weighted by support (the number of true instances for each label). This alters 'macro' to account for label imbalance'''
    f1 = f1_score(yTrue, yPred, average='weighted')
    return f1

def MicroF1Score(yTrue, yPred):
    '''Calculate metrics globally by counting the total true positives, false negatives and false positives.'''
    f1 = f1_score(yTrue, yPred, average='micro')
    return f1

def MacroF1Score(yTrue, yPred):
    '''Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account.'''
    f1 = f1_score(yTrue, yPred, average='macro')
    return f1

def F1ScorePerClass(yTrue, yPred):
    '''the scores for each class are returned'''
    f1 = f1_score(yTrue, yPred, average=None)
    return f1

def DatasetMetrics(X, y):
    '''Implements standard measures over a full dataset'''
    # Metrics over full set
    Y_MEAN = np.mean(y)
    Y_STD = np.std(y)
    Y_VARIANCE = np.var(y)
    
    return Y_MEAN, Y_STD, Y_VARIANCE

