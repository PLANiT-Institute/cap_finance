"""Explicit two-state payment-timing illustration, with no probability weights."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap.fx_settlement import PathValues, FXQuotes, PricePath
from cap.invoice_fin import InvoiceTerms, simulate_cost_with_invoices, paired_incremental_cost
from cap.commodity_ledger import CommodityFlow
from cap.plancost import PlanProfile
from cap import config as C


def main():
    out=ROOT/'data/research_v2/invoice_fin_bridge';out.mkdir(parents=True,exist_ok=True)
    dates=('2027-01-01','2027-07-01','2028-01-01','2029-01-01');annual=(dates[0],dates[2])
    ids=('A','B');sample='unweighted_arithmetic_payment_timing_example'
    def paths(x,calendar=dates):
        return PathValues(np.broadcast_to(x,(2,len(calendar))),ids,calendar,sample)
    rates=np.array([[1000,1200,1400,1600],[1800,1500,1200,900]])
    prices=np.array([[10,15,20,25],[20,25,10,15]])
    fx=FXQuotes('USD',{'USD':paths(1),'KRW':paths(rates)})
    discount=np.array([1,1.1**-.5,1/1.1,1/1.1**2])
    z=np.zeros(2)
    profile=PlanProfile(z,z,z,z,z,{}, {},z,0.,0,0,
        additional_commodity_flows=(CommodityFlow('purchase','feedstock',np.full(2,2.),
                                              'tonne','purchased','Toy annual quantities'),),
        profile_years=(2027,2028),embedded_price_basis={})
    cfg=C.load(discount_rate=.1,carbon_accounting_mode='gross_obligation_proxy')
    cfg['years']=dict(start=2027,end=2028)
    px={k:z for k in ['elec','re','h2','gas','coal','co2']}
    sh={k:paths(1,annual) for k in ['elec','h2','capex']}
    def evaluate(paydates):
        terms={'purchase':InvoiceTerms(PricePath('USD','tonne',paths(prices),None),
                                        annual,paydates,'Explicit toy timing')}
        return simulate_cost_with_invoices(profile,px,sh,{'subsidy':{}},cfg,
            terms=terms,fx=fx,discount_factors=paths(discount),real_base_year=None,
            basis_evidence='Nominal illustrative KRW; exact half-year convention for July')
    baseline=evaluate(annual);later=evaluate((dates[1],dates[3]))
    base=2*prices[:,0]*rates[:,0]+2*prices[:,2]*rates[:,2]/1.1
    delayed=2*prices[:,0]*rates[:,1]/np.sqrt(1.1)+2*prices[:,2]*rates[:,3]/1.1**2
    np.testing.assert_allclose(baseline.npv_krw_billion*1e9,base,rtol=1e-14)
    np.testing.assert_allclose(later.npv_krw_billion*1e9,delayed,rtol=1e-14)
    delta=paired_incremental_cost(later,baseline)*1e9
    np.testing.assert_allclose(delta,delayed-base,rtol=1e-13)
    pd.DataFrame([dict(state=state,date=d,KRW_per_USD=rates[i,j],USD_per_t=prices[i,j],
        discount_factor=discount[j],price_date=d in annual,
        baseline_payment=d in annual,later_payment=d in (dates[1],dates[3]))
        for i,state in enumerate(ids) for j,d in enumerate(dates)]).to_csv(out/'timing_example_inputs.csv',index=False)
    pd.DataFrame(dict(state=ids,baseline_npv_KRW=base,later_npv_KRW=delayed,
                      incremental_npv_KRW=delta)).to_csv(out/'timing_example_costs.csv',index=False)
    font=ROOT/'tmp/pdfs/methodology/Heading.ttf'
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                         'axes.unicode_minus':False,'font.size':10})
    fig,ax=plt.subplots(1,2,figsize=(10.5,4.5),layout='constrained')
    colors=['#227f91','#b65e38']
    for i,state in enumerate(ids):
        ax[0].plot([0,.5,1,2],rates[i],marker='o',color=colors[i],label=f'경로 {state}')
    ax[0].set(xticks=[0,.5,1,2],xticklabels=['2027.1','2027.7','2028.1','2029.1'],
              ylabel='가정한 명목환율 (KRW/USD)',title='같은 청구액도 지급일에 따라 환산액이 달라진다')
    ax[0].legend(frameon=False)
    bars=ax[1].bar(ids,delta/1000,color=colors,width=.5)
    ax[1].axhline(0,color='#58636c',lw=1)
    ax[1].set(ylabel='지급 지연 - 즉시 지급의 현재가치 (천 KRW)',title='물량이 같아도 증분 비용은 0이 아니다',
              ylim=(-28,11),xlabel='두 개의 산술 경로: 실현확률 미부여')
    for bar,value in zip(bars,delta/1000):
        ax[1].text(bar.get_x()+bar.get_width()/2,value+(1 if value>=0 else -1),
                   f'{value:+.3f}',ha='center',va='bottom' if value>=0 else 'top')
    for axis in ax:
        axis.spines[['top','right']].set_visible(False);axis.grid(axis='y',alpha=.15);axis.set_axisbelow(True)
    fig.suptitle('임의 예시 | 매년 2톤, 가격은 2027.1 / 2028.1 확정, 지급만 2027.7 / 2029.1로 이동\n연 할인율 10%·금융비용 제외: 실제 계약이나 지급 지연의 권고가 아님',fontsize=10)
    fig.savefig(out/'payment_timing.png',dpi=190);plt.close(fig)
    print(pd.read_csv(out/'timing_example_costs.csv').to_string(index=False))


if __name__=='__main__':main()
