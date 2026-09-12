from __future__ import annotations
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, cohen_kappa_score

def classification(y_true,y_pred):
    return {'accuracy':float(accuracy_score(y_true,y_pred)),'macro_f1':float(f1_score(y_true,y_pred,average='macro',zero_division=0))}

def human_judge_agreement(human,judge):
    x=pd.Series(human,dtype=float); y=pd.Series(judge,dtype=float)
    return {'n':int(len(x)),'spearman':float(x.corr(y,method='spearman')),'weighted_kappa':float(cohen_kappa_score(x,y,weights='quadratic'))}
