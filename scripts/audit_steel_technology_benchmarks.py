"""Primary-source benchmark extraction; no automatic transfer of cost scopes."""
import csv,json,re
from pathlib import Path
from audit_steel_case_data import ROOT,OUT,SOURCES,page

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sid='DIW_DP2082_PRIMARY';text=page(sid,11);rows=[]
    for label,values in [('Literature search',[299,254,592,886]),('Announced green steel projects',[800,467,751,1600])]:
        line=next(x for x in text.splitlines() if x.startswith(label))
        parsed=[int(x) for x in re.findall(r'(\d+)\(\d+\)',line)]
        assert parsed==values,(line,parsed)
        for route,value in zip(['DRP','EAF','DRP_EAF','DRP_EAF_ELECTROLYSER'],parsed):
            rows.append(dict(source_id=sid,source_url=SOURCES[sid]['url'],source_sha256=SOURCES[sid]['sha256'],
                             source_pdf_page=11,source_printed_page=9,sample=label,technology=route,
                             statistic='median',value=value,unit='EUR_2022_per_t_annual_DRI_or_steel_capacity',
                             transfer_limit='Sample medians; project and literature scope differ; not a confidence interval or universal engineering cost'))
    with (OUT/'verified_technology_benchmarks.csv').open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result=dict(verified_benchmarks=len(rows),dri_eaf_project_to_literature_ratio=751/592,
        eaf_project_to_literature_ratio=467/254,fin_dri_eaf_capex_kkrw_per_t=863,
        implied_kkrw_per_eur=863/592,price_year_conversion_to_2025_verified=False,
        normalization_or_project_scope_transfer_automated=False)
    (OUT/'technology_benchmark_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
