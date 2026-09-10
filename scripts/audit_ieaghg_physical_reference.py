"""Supplement a frozen IEAGHG experiment with original-PDF physical checks.

Does not replace its input package, regenerate its draws, or certify company data.
Run after visual review of the explicitly listed source pages.
"""
from pathlib import Path
import csv, hashlib, json, re, subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/research_v2/ieaghg_physical_reference'
PDF = ROOT/'tmp/pdfs/tcar_research_v2/ieaghg2013/report.pdf'
PAGES = [169,170,191,274,275,289,294,304,305,396,397,398,411,412,413]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frozen = ROOT/'data/research_v2/ieaghg_reference/package.json'
    package = json.loads(frozen.read_text())
    pages = subprocess.check_output(['pdftotext','-layout',str(PDF),'-']).decode().split('\f')
    old = pd.read_csv(frozen.parent/'source_observations.csv')
    oldchecks=[]
    for r in old.itertuples():
        v=r.value
        if r.item=='reference_ng_quantity_conflicting': token='2.9268'
        elif r.item=='reported_reference_ng_bill': token='33.203'
        else: token=f'{v:,.2f}'.rstrip('0').rstrip('.') if v%1 else f'{v:,.0f}'
        # Source includes .00 suffix for some integer costs; token occurrence
        # plus page-by-page visual column checks supports this transcription.
        passed=token.replace(',','') in pages[r.pdf_page-1].replace(',','')
        assert passed,(r.item,r.case,token)
        oldchecks.append(dict(item=r.item,case=r.case,pdf_page=r.pdf_page,
                              source_token=token,token_found=passed))
    obs=[]
    def add(case,item,value,unit,page,location):
        obs.append(dict(case=case,item=item,value=value,unit=unit,pdf_page=page,
                        location=location,status='selected_source_page_visually_reviewed'))
    for case,power,steam,pp,sp in [('REFERENCE',3398486,0,191,None),
            ('EOP_L1',14568197,2294279,396,397),('EOP_L2',15707234,6363123,411,412)]:
        add(case,'power_plant_ng',power,'GJ/year',pp,'Electricity production annual consumption')
        if sp:add(case,'steam_plant_ng',steam,'GJ/year',sp,'Steam production annual consumption')
    for case,annual,intensity,captured,oldint in [
            ('REFERENCE',8376554,2094.14,None,2090.14),
            ('EOP_L1',4182921,1045.73,4972525,1041.73),
            ('EOP_L2',3325694,831.42,6131267,827.42)]:
        add(case,'C7_emitted',annual,'t_CO2/year',275,'Volume II C-15 Table C-7 total')
        add(case,'C7_emitted_intensity',intensity,'kg_CO2/t_HRC',275,'Volume II C-15 Table C-7 total')
        add(case,'C7_ancillary_transport',16000,'t_CO2/year',275,'Unit 1300 trucks and rails')
        add(case,'D15_emitted_intensity',oldint,'kg_CO2/t_HRC',305,'Volume II D-28 CO2 avoidance table')
        if captured:add(case,'C7_captured',captured,'t_CO2/year',275,'Table C-7 total captured')
    for case,elec,steam,page in [('EOP_L1',607401683,15066752,398),('EOP_L2',785250547,18719740,413)]:
        add(case,'capture_internal_electricity',elec,'kWh/year',page,'Annex I Carbon Dioxide account')
        add(case,'capture_internal_steam',steam,'GJ/year',page,'Annex I Carbon Dioxide account')
    for r in obs:
        token=f"{r['value']:,.2f}".rstrip('0').rstrip('.') if r['value']%1 else f"{r['value']:,.0f}"
        assert token.replace(',','') in pages[r['pdf_page']-1].replace(',',''),r
    checks=[];ledger=[];qual=[]
    def check(name,case,a,b,tol):
        passed=abs(a-b)<=tol
        checks.append(dict(check=name,case=case,computed=a,reported=b,tolerance=tol,passed=passed))
        assert passed,(name,case,a,b)
    native=lambda c,k:next(r['value'] for r in obs if r['case']==c and r['item']==k)
    baseline=native('REFERENCE','C7_emitted')
    for case in ['REFERENCE','EOP_L1','EOP_L2']:
        g=native(case,'power_plant_ng')+(native(case,'steam_plant_ng') if case!='REFERENCE' else 0)
        prev=package['cases'][case]
        check('physical_vs_cost_implied_gas_GJ',case,g,prev['ng_GJ'],1.)
        actual=native(case,'C7_emitted');kg=native(case,'C7_emitted_intensity')
        oldkg=native(case,'D15_emitted_intensity')
        check('C7_vs_D15_intensity_offset_kg',case,kg-oldkg,4.,1e-9)
        check('C7_intensity_rounding_t',case,kg*4000,actual,20.)
        check('C7_less_transport_vs_D15_t',case,actual-16000,oldkg*4000,20.)
        avoided=baseline-actual
        captured=native(case,'C7_captured') if case!='REFERENCE' else 0
        r=dict(case=case,output_t_HRC_y=4e6,source_ng_GJ_y=g,
            cost_implied_ng_GJ_y=prev['ng_GJ'],ng_difference_GJ_y=g-prev['ng_GJ'],
            C7_emitted_t_CO2_y=actual,avoided_t_CO2_y=avoided,captured_t_CO2_y=captured,
            C7_avoided_fraction=avoided/baseline,
            D15_avoided_fraction=1-oldkg/native('REFERENCE','D15_emitted_intensity'),
            captured_over_baseline=captured/baseline,
            captured_less_avoided_t_CO2_y=captured-avoided,
            capture_to_avoided_ratio=captured/avoided if avoided else None,
            initial_capex_million_source_USD=prev['initial_capex_source_USD']/1e6,
            gross_opex_million_source_USD_y=prev['gross_opex_source_USD']/1e6)
        ledger.append(r)
        for target in [.50,.501,.55,.60,.604]:
            qual.append(dict(case=case,target=target,C7_eligible=r['C7_avoided_fraction']>=target,
                D15_eligible=r['D15_avoided_fraction']>=target,
                incorrect_capture_as_avoidance_eligible=r['captured_over_baseline']>=target))
    for t in [.50,.60]:
        q=[r for r in qual if r['target']==t]
        assert [r['case'] for r in q if r['C7_eligible']]==[r['case'] for r in q if r['D15_eligible']]
    pd.DataFrame(oldchecks).to_csv(OUT/'legacy_transcription_checks.csv',index=False)
    pd.DataFrame(obs).to_csv(OUT/'physical_source_observations.csv',index=False)
    pd.DataFrame(checks).to_csv(OUT/'arithmetic_checks.csv',index=False)
    pd.DataFrame(ledger).to_csv(OUT/'same_product_ledger.csv',index=False)
    pd.DataFrame(qual).to_csv(OUT/'emissions_qualification.csv',index=False)
    manifest=dict(source_pdf=str(PDF.relative_to(ROOT)),source_pdf_sha256=sha(PDF),
        source_url=package['source']['url'],source_physical_pages=642,
        selected_pages_visually_reviewed=PAGES,whole_report_validation_complete=False,
        legacy_observations_checked=len(oldchecks),new_observations=len(obs),arithmetic_checks=len(checks),
        qualification_rows=len(qual),original_50_60_percent_candidate_sets_unchanged=True,
        frozen_experiment_replaced=False,new_MC_runs=0,company_calibration=False,
        qualifications=['C7 columns incorrectly labelled OBF/MDEA; EOP order inferred from adjacent C6 and Annex I matching totals',
            'D15 excludes exactly 4 kg/t HRC relative to C7, matching ancillary transport row; boundary reconciliation inferred, not an explicit source erratum',
            'Captured minus avoided is an accounting residual, not a calibrated marginal gas emission factor',
            'Capture and compression are not verified permanent storage; no transport/storage tariff or leakage distribution adopted',
            'Original E35 versus prose gas inconsistency and electricity intensity unit label error remain held'],
        frozen_inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in [frozen,frozen.parent/'manifest.json',ROOT/'data/research_v2/ieaghg_paired/manifest.json']})
    manifest['artifact_sha256']={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.glob('*.csv'))}
    manifest['artifact_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ['qualifications','artifact_sha256','frozen_inputs_sha256']},ensure_ascii=False))

if __name__=='__main__':main()
