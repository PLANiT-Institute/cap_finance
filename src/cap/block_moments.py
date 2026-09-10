"""Exact monthly level covariance for the declared finite-support block model.

These are moments of a specified resampling distribution, not empirical evidence
that future prices follow it. Blocks are independent; within-block months share
one historical start. A final partial block uses the full-block start support.
"""
import numpy as np


def _lme(x, axis=0):
    top=np.max(x,axis=axis,keepdims=True)
    return np.squeeze(top,axis=axis)+np.log(np.mean(np.exp(x-top),axis=axis))


def block_level_covariance(returns, months, block_length):
    r=np.asarray(returns,dtype=float)
    if r.ndim!=1 or not len(r) or not np.isfinite(r).all():
        raise ValueError('A finite nonempty single-factor return history is required')
    if any(isinstance(x,bool) or not isinstance(x,(int,np.integer)) for x in (months,block_length)):
        raise ValueError('Horizon and block length must be integers')
    if months<1 or not 1<=block_length<=len(r):
        raise ValueError('Invalid horizon or block length')
    r=r-r.mean()
    starts=np.arange(len(r)-block_length+1)
    partial=np.cumsum(r[starts[:,None]+np.arange(block_length)],axis=1)
    first=_lme(partial)
    pair=_lme(partial[:,:,None]+partial[:,None,:])
    b,k=np.divmod(np.arange(months),block_length)
    anchor=b*first[-1]+first[k]
    cov=np.empty((months,months))
    for m in range(months):
        n=np.arange(m,months)
        same=b[n]==b[m]
        joint=np.where(same,
            b[m]*pair[-1,-1]+pair[k[m],k[n]],
            b[m]*pair[-1,-1]+pair[k[m],-1]+(b[n]-b[m]-1)*first[-1]+first[k[n]])
        value=np.expm1(joint-anchor[m]-anchor[n])
        cov[m,n]=value
        cov[n,m]=value
    if not np.isfinite(cov).all():
        raise ValueError('Second moment overflow; shorten horizon or review distribution')
    return cov


def gaussian_level_covariance(returns, months):
    r=np.asarray(returns,dtype=float)
    if r.ndim!=1 or len(r)<2 or not np.isfinite(r).all():
        raise ValueError('At least two finite single-factor returns required')
    if isinstance(months,bool) or not isinstance(months,(int,np.integer)) or months<1:
        raise ValueError('Positive integer horizon required')
    h=np.arange(1,months+1)
    cov=np.expm1(np.var(r,ddof=1)*np.minimum(h[:,None],h[None,:]))
    if not np.isfinite(cov).all():
        raise ValueError('Gaussian second moment overflow')
    return cov


def weighted_sum_variance(weights,covariance):
    w=np.asarray(weights,dtype=float);c=np.asarray(covariance,dtype=float)
    if w.ndim!=1 or not len(w) or c.shape!=(len(w),len(w)) or not np.isfinite(w).all() or not np.isfinite(c).all():
        raise ValueError('Finite weights and square aligned covariance required')
    if not np.allclose(c,c.T,rtol=1e-12,atol=1e-12):
        raise ValueError('Covariance must be symmetric')
    value=float(w@c@w)
    scale=float(np.abs(w)@np.abs(c)@np.abs(w))
    if value < -1e-12*max(1.,scale):
        raise ValueError('Negative weighted variance')
    return max(0.,value)
