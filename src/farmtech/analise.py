"""Modelagem da base da Fase 5, com separação por cenário climático."""
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from .config import ROOT, SEED

CROP='Crop';TARGET='Yield'
NUMERIC=['Precipitation (mm day-1)','Specific Humidity at 2 Meters (g/kg)',
         'Relative Humidity at 2 Meters (%)','Temperature at 2 Meters (C)']
MODEL_FILE=ROOT/'models/produtividade.joblib'
REPORT_FILE=ROOT/'results/produtividade.json'

class CropMeanRegressor(RegressorMixin,BaseEstimator):
    """Baseline que considera a escala própria de cada cultura, sem clima."""
    def fit(self,X,y):
        self.means_=pd.DataFrame({'crop':X[CROP].to_numpy(),'yield':np.asarray(y)}).groupby('crop')['yield'].mean().to_dict()
        self.overall_=float(np.mean(y));return self
    def predict(self,X):
        return X[CROP].map(self.means_).fillna(self.overall_).to_numpy()

def dataset():
    frame=pd.read_csv(ROOT/'data/crop_yield.csv')
    if set(frame.columns)!={CROP,TARGET,*NUMERIC}:raise ValueError('Colunas inesperadas na base.')
    if frame.isna().any().any() or not np.isfinite(frame[NUMERIC+[TARGET]]).all().all():raise ValueError('A base contém valores inválidos.')
    return frame

def train():
    df=dataset();X=df[[CROP]+NUMERIC];y=df[TARGET]
    groups=pd.factorize(pd.MultiIndex.from_frame(df[NUMERIC]))[0]
    train_idx,test_idx=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(X,y,groups))
    assert not set(groups[train_idx])&set(groups[test_idx])
    preprocess=ColumnTransformer([('crop',OneHotEncoder(handle_unknown='error',sparse_output=False),[CROP]),
                                  ('clima',StandardScaler(),NUMERIC)])
    algorithms={'Baseline média':DummyRegressor(),'Média por cultura':CropMeanRegressor(),'Regressão linear':LinearRegression(),
                'Árvore':DecisionTreeRegressor(max_depth=5,random_state=SEED),
                'Random Forest':RandomForestRegressor(n_estimators=150,max_depth=8,min_samples_leaf=2,random_state=SEED,n_jobs=2),
                'KNN':KNeighborsRegressor(n_neighbors=5),'SVR':SVR(C=10000,epsilon=100)}
    rows=[];trained={}
    for name,estimator in algorithms.items():
        model=estimator if isinstance(estimator,CropMeanRegressor) else make_pipeline(clone(preprocess),estimator)
        scores=-cross_val_score(model,X.iloc[train_idx],y.iloc[train_idx],groups=groups[train_idx],
                                cv=GroupKFold(n_splits=5),scoring='neg_mean_absolute_error')
        model.fit(X.iloc[train_idx],y.iloc[train_idx]);trained[name]=model
        pred=model.predict(X.iloc[test_idx])
        rows.append({'modelo':name,'cv_mae':float(scores.mean()),'cv_mae_desvio':float(scores.std()),
                     'teste_mae':float(mean_absolute_error(y.iloc[test_idx],pred)),
                     'teste_rmse':float(np.sqrt(mean_squared_error(y.iloc[test_idx],pred))),
                     'teste_r2':float(r2_score(y.iloc[test_idx],pred))})
    selected=min(rows,key=lambda row:row['cv_mae'])['modelo']
    # Checkpoint mantém somente os grupos de treino; teste continua reservado.
    joblib.dump(trained[selected],MODEL_FILE)
    pd.DataFrame(rows).to_csv(ROOT/'results/comparacao_modelos.csv',index=False)
    test_rows=df.iloc[test_idx].copy();test_rows['previsto']=trained[selected].predict(X.iloc[test_idx])
    test_rows.to_csv(ROOT/'results/predicoes_teste.csv',index=False)
    per_crop=[{'cultura':crop,'n':len(group),'mae':float(mean_absolute_error(group[TARGET],group['previsto']))} for crop,group in test_rows.groupby(CROP)]
    pd.DataFrame(per_crop).to_csv(ROOT/'results/erro_por_cultura.csv',index=False)
    climates=df[NUMERIC].drop_duplicates().copy()
    scaled=StandardScaler().fit_transform(climates)
    climates['perfil']=KMeans(n_clusters=3,n_init=20,random_state=SEED).fit_predict(scaled)
    climates['outlier']=IsolationForest(contamination=.1,random_state=SEED).fit_predict(scaled)==-1
    climates.to_csv(ROOT/'results/perfis_climaticos.csv',index=False)
    report={'seed':SEED,'rows':len(df),'unique_climate_groups':len(set(groups)),
            'train_rows':len(train_idx),'test_rows':len(test_idx),'train_groups':sorted(set(map(int,groups[train_idx]))),
            'test_groups':sorted(set(map(int,groups[test_idx]))),'group_overlap':0,
            'selected_model':selected,'selection':'menor MAE médio de validação cruzada GroupKFold, somente treino',
            'unit':'escala original de Yield; unidade não confirmada',
            'precipitation_unit':'rótulo original mm day-1; valores requerem confirmação da escala temporal',
            'data_sha256':hashlib.sha256((ROOT/'data/crop_yield.csv').read_bytes()).hexdigest(),
            'model_sha256':hashlib.sha256(MODEL_FILE.read_bytes()).hexdigest(),
            'metrics':rows,'test_metrics_by_crop':per_crop,'limitations':['156 registros e apenas 39 cenários climáticos','R² agregado é influenciado pela diferença de escala entre culturas; comparar também com média por cultura','Unidades e origem detalhada da base não confirmadas','Não converter leituras do solo em variáveis climáticas; não equivale a recomendação agronômica']}
    REPORT_FILE.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return report

def predict(crop,values):
    if not MODEL_FILE.exists():raise ValueError('Execute o treinamento primeiro.')
    df=dataset()
    if crop not in set(df[CROP]):raise ValueError('Cultura fora da base de treinamento.')
    if len(values)!=len(NUMERIC) or not np.isfinite(values).all():raise ValueError('Valores climáticos inválidos.')
    # Marca extrapolação antes de exibir a estimativa.
    outside=[c for c,v in zip(NUMERIC,values) if not df[c].min()<=v<=df[c].max()]
    record=pd.DataFrame([[crop,*values]],columns=[CROP]+NUMERIC)
    value=float(joblib.load(MODEL_FILE).predict(record)[0])
    return {'estimativa':value,'unidade':'escala original de Yield','fora_da_faixa':outside}
