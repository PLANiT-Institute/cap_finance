"""Retrospective one-month benchmark forecast diagnostics, not a TCaR fit.

Candidate design was informed by descriptive full-sample inspection; do not call
2020-2025 an untouched confirmatory holdout. Coefficients use pre-2020 rows only.
"""
import csv
import hashlib
import json
from pathlib import Path
from statistics import NormalDist
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
OUT=ROOT/'data/research_v2/price_model_audit'
KEYS=['brent','thermal_coal_au','henry_hub','europe_gas','japan_lng','iron_ore']
NORMAL=NormalDist()


def save(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def fit(y, dates, kind, end, penalty=0.):
    mask=dates<=end;mu=y[mask].mean(axis=0);scale=y[mask].std(axis=0,ddof=1)
    z=(y-mu)/scale;p={'iid':0,'ar1':1,'var4':4}[kind]
    ix=np.arange(p,len(y));ix=ix[dates[ix]<=end]
    assert max(dates[ix].tolist())<=end
    if kind=='iid':
        b=np.zeros((1,len(KEYS)));b[0]=z[ix].mean(axis=0)
        pred=np.tile(b[0],(len(ix),1));df=1.
    elif kind=='ar1':
        b=np.empty((2,len(KEYS)));pred=np.empty((len(ix),len(KEYS)))
        for j in range(len(KEYS)):
            x=np.column_stack([np.ones(len(ix)),z[ix-1,j]])
            b[:,j]=np.linalg.lstsq(x,z[ix,j],rcond=None)[0];pred[:,j]=x@b[:,j]
        df=2.
    else:
        x=np.column_stack([np.ones(len(ix))]+[z[ix-lag] for lag in range(1,p+1)])
        reg=np.eye(x.shape[1])*penalty;reg[0,0]=0
        inv=np.linalg.inv(x.T@x+reg);b=inv@x.T@z[ix];pred=x@b
        df=float(np.trace(inv@(x.T@x)))
    e=(z[ix]-pred)*scale
    # Residual scale correction is exact for unpenalized linear OLS under its
    # assumptions, approximate with ridge; predictive diagnostics remain essential.
    cov=e.T@e/(len(ix)-df)
    cov=.9*cov+.1*np.diag(np.diag(cov))
    assert np.linalg.eigvalsh(cov).min()>0
    return dict(kind=kind,p=p,mu=mu,scale=scale,b=b,cov=cov,
                n=len(ix),effective_df=df,penalty=penalty,end=end)


def predict(model,y,idx):
    p=model['p'];assert min(idx)>=p
    z=(y-model['mu'])/model['scale'];kind=model['kind'];b=model['b']
    if kind=='iid':pred=np.tile(b[0],(len(idx),1))
    elif kind=='ar1':pred=b[0]+z[idx-1]*b[1]
    else:
        x=np.column_stack([np.ones(len(idx))]+[z[idx-l] for l in range(1,p+1)])
        pred=x@b
    return pred*model['scale']+model['mu']


def ewma_covariances(model,y,idx,decay):
    """One-step plug-in covariance uses only earlier errors, never current y."""
    cov=model['cov'].copy();out=[];wanted=set(idx)
    for t in range(model['p'],max(idx)+1):
        current=.9*cov+.1*np.diag(np.diag(cov))
        if t in wanted:out.append(current.copy())
        e=y[t]-predict(model,y,np.array([t]))[0]
        cov=decay*cov+(1-decay)*np.outer(e,e)
    return np.array(out)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with SOURCE.open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    dates=np.array([r['period'] for r in raw]);y=np.array([[float(r[k]) for k in KEYS] for r in raw])
    assert dates[0]=='2010M02' and dates[-1]=='2025M12' and len(y)==191
    val=np.where((dates>='2018M01')&(dates<='2019M12'))[0]
    test=np.where((dates>='2020M01')&(dates<='2025M12'))[0]
    assert len(val)==24 and len(test)==72
    tuning=[]
    for penalty in [.1,1.,10.,100.]:
        m=fit(y,dates,'var4','2017M12',penalty);pred=predict(m,y,val)
        score=float(np.mean(((y[val]-pred)/m['scale'])**2))
        tuning.append(dict(penalty=penalty,training_end='2017M12',validation_start='2018M01',
            validation_end='2019M12',n_validation=24,standardized_MSE=score))
    chosen=min(tuning,key=lambda r:r['standardized_MSE'])['penalty']
    save('var_penalty_tuning.csv',tuning)
    ewma_tuning=[];mval=fit(y,dates,'ar1','2017M12')
    val_err=y[val]-predict(mval,y,val)
    for decay in [.85,.94,.97,.99]:
        covs=ewma_covariances(mval,y,val,decay)
        loss=[.5*(len(KEYS)*np.log(2*np.pi)+np.linalg.slogdet(c)[1]+e@np.linalg.solve(c,e)) for c,e in zip(covs,val_err)]
        ewma_tuning.append(dict(decay=decay,training_end='2017M12',validation_start='2018M01',
            validation_end='2019M12',average_joint_gaussian_NLL=float(np.mean(loss))))
    decay=min(ewma_tuning,key=lambda r:r['average_joint_gaussian_NLL'])['decay']
    save('ewma_decay_tuning.csv',ewma_tuning)
    metrics=[];predictions=[];models=[];aggregate=[]
    for kind in ['iid','ar1','var4','ar1_ewma']:
        m=fit(y,dates,'ar1' if kind=='ar1_ewma' else kind,'2019M12',chosen if kind=='var4' else 0.)
        pred=predict(m,y,test);err=y[test]-pred
        covs=ewma_covariances(m,y,test,decay) if kind=='ar1_ewma' else np.tile(m['cov'],(len(test),1,1))
        assert np.linalg.eigvalsh(covs).min()>0
        sd=np.sqrt(np.diagonal(covs,axis1=1,axis2=2))
        nll=np.array([.5*(len(KEYS)*np.log(2*np.pi)+np.linalg.slogdet(c)[1]+e@np.linalg.solve(c,e)) for c,e in zip(covs,err)])
        aggregate.append(dict(model=kind,average_joint_gaussian_NLL=float(nll.mean()),
            normalized_MSE=float(np.mean((err/m['scale'])**2)),n_test_months=len(test),
            covariance_shrinkage_to_diagonal=.1,training_rows=m['n'],effective_df=m['effective_df']))
        for j,k in enumerate(KEYS):
            q95=pred[:,j]+NORMAL.inv_cdf(.95)*sd[:,j]
            q05=pred[:,j]+NORMAL.inv_cdf(.05)*sd[:,j]
            q99=pred[:,j]+NORMAL.inv_cdf(.99)*sd[:,j]
            u=y[test,j]-q95
            metrics.append(dict(model=kind,series_id=k,n_test=len(test),
                upper95_exceedances=int(np.sum(y[test,j]>q95)),upper99_exceedances=int(np.sum(y[test,j]>q99)),
                central90_coverage=float(np.mean((y[test,j]>=q05)&(y[test,j]<=q95))),
                quantile95_pinball=float(np.mean(np.maximum(.95*u,-.05*u))),
                MSE=float(np.mean(err[:,j]**2)),median_plugin_forecast_SD=float(np.median(sd[:,j])),
                test_standardized_error_SD=float(np.std(err[:,j]/sd[:,j],ddof=1))))
            for n,t in enumerate(test):
                predictions.append(dict(model=kind,series_id=k,period=dates[t],observed_log_change=float(y[t,j]),
                    predicted_conditional_mean=float(pred[n,j]),q05=float(q05[n]),q95=float(q95[n]),q99=float(q99[n]),
                    previous_observation_period=dates[t-1],coefficient_training_end=m['end']))
        # Regression predictions must not depend on current/future observed returns.
        changed=y.copy();changed[test[0]:]+=10
        assert np.allclose(predict(m,y,test[:1]),predict(m,changed,test[:1]))
        if kind=='ar1_ewma':
            assert np.allclose(ewma_covariances(m,y,test[:1],decay),ewma_covariances(m,changed,test[:1],decay))
            m['ewma_decay']=decay
        m['label']=kind
        models.append({k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in m.items()})
    save('marginal_validation.csv',metrics);save('joint_validation.csv',aggregate);save('retrospective_predictions.csv',predictions)
    (OUT/'fitted_return_models.json').write_text(json.dumps(dict(series=KEYS,models=models),indent=2)+'\n')
    lags=[]
    for lag in range(7):
        a=y[:-lag,0] if lag else y[:,0];b=y[lag:,4]
        lags.append(dict(brent_lead_months=lag,n=len(a),correlation=float(np.corrcoef(a,b)[0,1]),
            role='full_sample_descriptive_not_causal_or_confirmatory_lag_selection'))
    save('brent_lng_lag_correlations.csv',lags)
    summary=dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        training_end='2019M12',retrospective_evaluation=['2020M01','2025M12'],
        untouched_confirmatory_holdout=False,
        design_caveat='Model candidates informed by full-sample descriptive inspection; fitting and penalty tuning exclude2020onward',
        selected_var4_penalty=chosen,selected_ewma_decay=decay,prediction_horizon='one month conditional on observed past',
        parameter_estimation_uncertainty_included=False,
        no_future_observation_test_passed=True,covariance_positive_definite=True,
        price_level_mean_reversion_estimated=False,GCAM_forecast_errors_observed=False,
        TCaR_calibrated=False,FIN_modified=False,
        limitations=['Benchmark definition changes','Only72retrospective months; no iid binomial significance claim',
        'No electricity/H2/carbon or company contracts','Ridge residual scale correction approximate',
        'One-month coverage does not validate24-year cost tails','EWMA conditional diagnostics do not validate exponential multi-period moments'])
    (OUT/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(selected_penalty=chosen,joint_scores=aggregate),indent=2))


if __name__=='__main__':main()
