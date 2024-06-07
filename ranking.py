
from sklearn.model_selection import GroupShuffleSplit
import pandas as pd
import xgboost as xgb
import numpy as np

df = pd.read_csv("Data/temp_result.csv")
df = df.drop(columns=['Finish Time'])
# print(df.dtypes)
gss = GroupShuffleSplit(test_size=.20, n_splits=1, random_state = 7).split(df, groups=df['Race ID'])
X_train_inds, X_test_inds = next(gss)

train_data = df.iloc[X_train_inds]
X_train = train_data.loc[:, ~train_data.columns.isin(['Race ID','Pla.'])]
y_train = train_data.loc[:, train_data.columns.isin(['Pla.'])]

# print(y_train)
groups = train_data.groupby('Race ID').size().to_frame('size')['size'].to_numpy()

test_data = df.iloc[X_test_inds]

#We need to keep the id for later predictions
X_test = test_data.loc[:, ~test_data.columns.isin(['Pla.'])]
y_test = test_data.loc[:, test_data.columns.isin(['Pla.'])]


model = xgb.XGBRanker(  
    tree_method='hist',
    booster='gbtree',
    objective='rank:pairwise',
    random_state=42, 
    learning_rate=0.05,
    colsample_bytree=0.9, 
    eta=0.05, 
    max_depth=6, 
    n_estimators=110, 
    subsample=0.75 
    )

model.fit(X_train, y_train, group=groups, verbose=True)

def predict(model, df):
    return model.predict(df.loc[:, ~df.columns.isin(['Race ID', 'Pla.'])])


predictions = (test_data.groupby('Race ID')
               .apply(lambda x: predict(model, x)))

cnt = 0
for i in range(0, 100):
    a = predictions.iloc[i]
    a = np.argsort(a)
    a = a + 1
    cnt += a[0] == 1

print(cnt)