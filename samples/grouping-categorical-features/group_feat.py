from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

class GroupCatFeatures():
    def __init__(self,method='top_n',threshold=0.05,n=10,column_index = None,column_name='',task='classification'):
        # Input variables
       # self.feature_types = feature_types
        self.method = method
        self.threshold = threshold
        self.n = n
        self.column_index=column_index
        self.column_name=column_name
        self.task=task
    
    def group_perc(self,X,threshold):
        X_ = pd.DataFrame(X.copy(),columns=self.column_name)
        X_res = pd.DataFrame(X.copy(),columns=self.column_name)
        total_rows = X_.shape[0]
        class_correspondency = {}
        for col in X_res.columns:
            X_['perc_rows'] = X_.groupby(col)[col].transform(lambda x: len(x)/total_rows)        
            under_threshold = X_['perc_rows'] < threshold
            X_res[col + '....grouped'] = X_res[col]
            X_res.loc[under_threshold,col + '....grouped'] = 'other'
            X_dict = X_res.loc[:,[col,str(col) + '....grouped']]
            X_dict = X_dict.drop_duplicates().sort_values(by=col)
            class_correspondency.update(X_dict.to_dict(orient='list'))
            X_res.loc[:,col] = X_res[col + '....grouped']
            X_res.drop(columns=col + '....grouped',inplace=True)
        return X_res,class_correspondency  

    def group_top_n(self,X,n):
        X_ = pd.DataFrame(X.copy(),columns=self.column_name)
        X_res = pd.DataFrame(X.copy(),columns=self.column_name)
        class_correspondency = {}
        for col in X_res.columns:
            s = X_[col].value_counts().head(n)
            idx_top_n = ~X_[col].isin(s.index)
            X_res[col + '....grouped'] = X_res[col]
            X_res.loc[idx_top_n,col + '....grouped'] = 'other'
            X_dict = X_res.loc[:,[col,str(col) + '....grouped']]
            X_dict = X_dict.drop_duplicates().sort_values(by=col)
            class_correspondency.update(X_dict.to_dict(orient='list'))
            X_res.loc[:,col] = X_res[col + '....grouped']
            X_res.drop(columns=col + '....grouped',inplace=True)
        return X_res,class_correspondency    
    
    def kmeans_fit(self,X,n):
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(X)
        return kmeans 
    
    def group_kmeans(self,X,y,n):
        X_ = pd.DataFrame(X,columns=self.column_name)
        X_res = pd.DataFrame(X.copy(),columns=self.column_name)
        total_target=[]
        class_correspondency = {}
        total_rows = X_.shape[0]
        for col in X_res.columns:
            for j in range(y.shape[1]):
                X_['y_'+ str(j)]=y[:,j]
                total_target.append(sum(y[:,j]))
                if self.task=="classification":
                    X_['Kmeans___agg_target'+ str(j)] = X_.groupby(col)['y_'+ str(j)].transform(lambda x: sum(x)/total_target[j])
                else:
                    X_['Kmeans___agg_target'+ str(j)] = X_.groupby(col)['y_'+ str(j)].transform(lambda x: sum(x)/len(x))                    
                X_['Kmeans_perc_rows'+ str(j)] = X_.groupby(col)['y_'+ str(j)].transform(lambda x: len(x)/total_rows) 
            X_kmeans = X_.filter(regex='^Kmeans___',axis=1)
            kmeans = self.kmeans_fit(X_kmeans,n)
            X_res[col + '....grouped'] = np.char.add(['grupo_']*total_rows,kmeans.predict(X_kmeans).astype('str').tolist())
            X_dict = X_res.loc[:,[col,str(col) + '....grouped']]
            X_dict = X_dict.drop_duplicates().sort_values(by=col)
            class_correspondency.update(X_dict.to_dict(orient='list'))
            X_res.loc[:,col] = X_res[col + '....grouped']
            X_res.drop(columns=col + '....grouped',inplace=True)           
        return X_res,class_correspondency    

    def fit_transform(self,X,y):
        X_cat = X.copy()
        X_cat = X_cat[:,self.column_index]
        if self.method=='percent':
            X_res,class_correspondency= self.group_perc(X_cat,self.threshold)
        if self.method=='top_n':
            X_res,class_correspondency= self.group_top_n(X_cat,self.n)
        if self.method=='kmeans':
            X_res,class_correspondency= self.group_kmeans(X_cat,y,self.n)
        columns_tocopy= np.setdiff1d(range(X.shape[1]),self.column_index)
        X_res = np.concatenate((X_res,X[:,columns_tocopy]),axis=1)
        return X_res,class_correspondency  
    