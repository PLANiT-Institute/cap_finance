import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rng=np.random.default_rng(3)
fig,ax=plt.subplots(figsize=(7,5.2),dpi=160)
# feasible plan cloud
n=90
x=rng.uniform(1.5,8.5,n); y=rng.uniform(1.2,8.0,n)
# keep points above frontier curve y_f(x)
xf=np.linspace(1.6,7.5,200); yf=0.9+9.0/(xf+0.6)**1.3*1.2
keep=y > 0.9+9.0/(x+0.6)**1.3*1.2 + 0.25
ax.scatter(x[keep],y[keep],s=14,color="#b8c2cc",alpha=.8,zorder=2,label="feasible plans (same carbon budget)")
ax.plot(xf,yf,color="#1f3a5f",lw=2.6,zorder=3,label="efficient frontier")
# frontier points along
fx=np.array([2.0,2.8,3.8,5.2,7.0]); fy=0.9+9.0/(fx+0.6)**1.3*1.2
ax.scatter(fx,fy,s=38,color="#1f3a5f",zorder=4)
# disclosed plan
dx,dy=6.0,5.3
ax.scatter([dx],[dy],s=170,marker="*",color="#c0392b",zorder=6,label="disclosed plan")
# projections
xg=3.0; yg=0.9+9.0/(dx+0.6)**1.3*1.2   # y on frontier at dx
# horizontal gap: to frontier point at same y
xh=xf[np.argmin(np.abs(yf-dy))]
ax.annotate("",xy=(xh,dy),xytext=(dx,dy),arrowprops=dict(arrowstyle="<->",color="#c0392b",lw=1.6))
ax.text((xh+dx)/2,dy+0.25,"cost gap",ha="center",color="#c0392b",fontsize=10)
ax.annotate("",xy=(dx,yg),xytext=(dx,dy),arrowprops=dict(arrowstyle="<->",color="#c0392b",lw=1.6))
ax.text(dx+0.15,(yg+dy)/2,"risk gap",va="center",color="#c0392b",fontsize=10)
ax.text(4.3,1.0,"contract choice varies\n(PPA share, fixed-price EPC)\ntechnology schedule fixed",fontsize=8.5,color="#1f3a5f",style="italic")
ax.set_xlabel("Expected incremental cost, P50  (tn KRW)")
ax.set_ylabel("Tail cost-at-risk, TCaR = P90 − P50  (tn KRW)")
ax.set_xlim(1,9.3); ax.set_ylim(0.5,8.6)
ax.set_xticks([]); ax.set_yticks([])
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.legend(loc="upper right",frameon=False,fontsize=9)
ax.set_title("CAP efficient frontier — sketch",loc="left",fontsize=12,color="#1f3a5f")
fig.tight_layout(); fig.savefig("cap_frontier_sketch.png"); fig.savefig("cap_frontier_sketch.svg")
