import json
from pathlib import Path
import pandas as pd
import streamlit as st
from .analyser import ReturnReasonAnalyser
from .workload import enforce_workload
ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Return Reason Analyser",layout="wide")
st.title("Structured Return-Reason Analyser")
st.caption("Evidence-backed root-cause triage for size-related fashion returns")
data=ROOT/"data/returns.csv"
if not data.exists(): st.warning("Run: python -m src.generate_data"); st.stop()
df=pd.read_csv(data); model=ReturnReasonAnalyser()
worker=st.sidebar.text_input("Worker ID","worker-01"); tasks=st.sidebar.number_input("Requested tasks",0,100,20)
a=enforce_workload(worker,tasks); st.sidebar.metric("Safe assigned",a.assigned)
if a.overflow: st.sidebar.error(f"{a.overflow} task(s) remain unassigned: safety cap is 25.")
tab1,tab2,tab3=st.tabs(["Analyse Return","Portfolio","Evaluation"])
with tab1:
    rid=st.selectbox("Return ID",df.return_id.tolist()); row=df[df.return_id==rid].iloc[0].to_dict(); o=model.predict(row)
    c1,c2,c3=st.columns(3); c1.metric("Root cause",o["predicted_label"]); c2.metric("Confidence",f'{o["confidence"]:.0%}'); c3.metric("High priority","YES" if o["high_priority"] else "NO")
    st.subheader("Evidence")
    for e in o["evidence"]: st.write("•",e)
    st.subheader("Five evidence streams"); st.json({k:row[k] for k in ["return_text","product_attribute","size_chart","listing_content","customer_action","inspection_finding"]})
with tab2:
    out=[{**r.to_dict(),**model.predict(r.to_dict())} for _,r in df.iterrows()]; odf=pd.DataFrame(out)
    st.dataframe(odf[["return_id","day_type","predicted_label","confidence","high_priority","evidence_count"]],use_container_width=True)
    st.subheader("High-priority actionable outputs"); st.dataframe(odf[odf.high_priority][["return_id","product_id","predicted_label","confidence","evidence"]],use_container_width=True)
with tab3:
    p=ROOT/"reports/evaluation.json"
    st.json(json.loads(p.read_text()) if p.exists() else {"status":"Run python -m src.evaluate first"})
