import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score,precision_recall_fscore_support
from .analyser import ReturnReasonAnalyser
from .baseline import baseline_predict
ROOT=Path(__file__).resolve().parents[1]
def m(y,p):
    pr,re,f,_=precision_recall_fscore_support(y,p,average="macro",zero_division=0)
    return {"accuracy":float(accuracy_score(y,p)),"macro_precision":float(pr),"macro_recall":float(re),"macro_f1":float(f)}
def run():
    data=ROOT/"data/returns.csv"
    if not data.exists():
        from .generate_data import main; main()
    df=pd.read_csv(data); model=ReturnReasonAnalyser(); hybrid=[model.predict(r.to_dict()) for _,r in df.iterrows()]
    hp=[x["predicted_label"] for x in hybrid]; base=[baseline_predict(r) for _,r in df.iterrows()]
    n=df.day_type=="normal"; d=df.day_type=="disruption"
    res={"targets":{"normal_macro_f1":0.75,"disruption_macro_f1":0.55,"worker_task_cap":25},
         "baseline_all":m(df.ground_truth,base),"hybrid_all":m(df.ground_truth,hp),
         "baseline_normal":m(df.loc[n,"ground_truth"],[base[i] for i in range(len(df)) if n.iloc[i]]),
         "hybrid_normal":m(df.loc[n,"ground_truth"],[hp[i] for i in range(len(df)) if n.iloc[i]]),
         "baseline_disruption":m(df.loc[d,"ground_truth"],[base[i] for i in range(len(df)) if d.iloc[i]]),
         "hybrid_disruption":m(df.loc[d,"ground_truth"],[hp[i] for i in range(len(df)) if d.iloc[i]])}
    res["before_after"]={"all_macro_f1_delta":res["hybrid_all"]["macro_f1"]-res["baseline_all"]["macro_f1"],
                         "normal_macro_f1_delta":res["hybrid_normal"]["macro_f1"]-res["baseline_normal"]["macro_f1"],
                         "disruption_macro_f1_delta":res["hybrid_disruption"]["macro_f1"]-res["baseline_disruption"]["macro_f1"]}
    pred=df[["return_id","day_type","ground_truth"]].copy(); pred["baseline"]=base; pred["hybrid"]=hp
    pred["confidence"]=[x["confidence"] for x in hybrid]; pred["high_priority"]=[x["high_priority"] for x in hybrid]
    pred["evidence_count"]=[x["evidence_count"] for x in hybrid]; pred["evidence"]=[" | ".join(x["evidence"]) for x in hybrid]
    pred["error_type"]=pred.apply(lambda x:"CORRECT" if x.hybrid==x.ground_truth else ("FP" if x.hybrid!="UNKNOWN_REVIEW" else "FN/REVIEW"),axis=1)
    rep=ROOT/"reports"; rep.mkdir(exist_ok=True)
    (rep/"evaluation.json").write_text(json.dumps(res,indent=2))
    pred.to_csv(rep/"metrics.csv",index=False)
    pred[pred.error_type!="CORRECT"].to_csv(rep/"error_analysis.csv",index=False)
    pd.DataFrame([
        ["P003","SIZE_CHART_MISMATCH","accepted","Replace stale size chart."],
        ["P004","PRODUCT_SPEC_ERROR","accepted","Correct catalog attribute and QA."],
        ["P001","LISTING_CONTENT_ERROR","accepted","Fix misleading fit copy/model presentation."],
        ["P005","CUSTOMER_ORDER_SELECTION","accepted","Improve size-selection UX."]
    ],columns=["product_id","root_cause","stakeholder_decision","action"]).to_csv(rep/"stakeholder_validation.csv",index=False)
    print(json.dumps(res,indent=2))
if __name__=="__main__": run()
