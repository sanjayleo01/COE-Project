import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import CONFIDENCE_THRESHOLD,HIGH_PRIORITY_THRESHOLD,MIN_EVIDENCE_HIGH_PRIORITY
from .baseline import KEYWORDS

PROTOTYPES={
"SIZE_TOO_SMALL":"too tight smaller than expected chest waist garment fit small",
"SIZE_TOO_LARGE":"too loose bigger than expected garment fit large roomy",
"SIZE_CHART_MISMATCH":"size chart published measurement actual garment does not match",
"LISTING_CONTENT_ERROR":"listing description model fit photos content misleading incorrect fit",
"PRODUCT_SPEC_ERROR":"product specification attribute stored measurement incorrect",
"CUSTOMER_ORDER_SELECTION":"customer selected ordered wrong size needed different size product matches",
"QUALITY_DAMAGE":"tear damaged broken stain defect quality problem",
}
class ReturnReasonAnalyser:
    def __init__(self):
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words="english")
        self.labels=list(PROTOTYPES)
        self.proto=self.vectorizer.fit_transform(PROTOTYPES.values())
    def _text(self,row):
        return " ".join(str(row.get(k,"") or "") for k in ["return_text","product_attribute","size_chart","fit_type","listing_content","customer_action","inspection_finding"]).lower()
    def predict(self,row):
        ret=str(row.get("return_text","") or "").lower()
        action=str(row.get("customer_action","") or "").lower()
        listing=str(row.get("listing_content","") or "").lower()
        ins=str(row.get("inspection_finding","") or "").lower()
        full=self._text(row)
        sem=cosine_similarity(self.vectorizer.transform([full]),self.proto)[0]
        score={l:0.18*float(sem[i]) for i,l in enumerate(self.labels)}
        sources=defaultdict(set); evidence=defaultdict(list)
        def add(label,amount,*src):
            score[label]+=amount; sources[label].update(src)
        if any(x in ins for x in ["tear","damaged","broken","stain","defect"]):
            add("QUALITY_DAMAGE",0.96,"inspection_finding"); evidence["QUALITY_DAMAGE"].append("inspection confirms physical damage")
        if any(x in action for x in ["wrong size","selected wrong","my mistake","different size"]):
            add("CUSTOMER_ORDER_SELECTION",0.88,"customer_action"); evidence["CUSTOMER_ORDER_SELECTION"].append("customer action explicitly indicates wrong-size selection")
        if any(x in listing for x in ["listing says","model page","misleading","regular fit","slim"]) and (any(x in ret for x in ["listing","model","shown","fit"]) or "compared" in action):
            add("LISTING_CONTENT_ERROR",0.88,"listing_content","return_text"); evidence["LISTING_CONTENT_ERROR"].append("listing content is implicated by customer evidence")
        chart=re.findall(r"(\\d+)",str(row.get("size_chart",""))); actual=re.findall(r"(\\d+)",str(row.get("product_attribute","")))
        if chart and actual and chart[0]!=actual[0]:
            c,a=int(chart[0]),int(actual[0])
            add("SIZE_CHART_MISMATCH",0.90,"size_chart","product_attribute"); evidence["SIZE_CHART_MISMATCH"].append(f"published measurement {c} differs from actual measurement {a}")
            if any(x in (ret+" "+full) for x in ["stored","product spec","attribute","specification"]):
                add("PRODUCT_SPEC_ERROR",0.94,"product_attribute","return_text"); evidence["PRODUCT_SPEC_ERROR"].append("stored product attribute is explicitly implicated")
            elif a<c and (any(x in ret for x in ["small","smaller","tight"]) or "measured" in ins):
                add("SIZE_TOO_SMALL",0.86,"size_chart","product_attribute"); evidence["SIZE_TOO_SMALL"].append("actual measurement is smaller than published measurement")
            elif a>c and (any(x in ret for x in ["large","larger","big","bigger","loose","roomy"]) or "measured" in ins):
                add("SIZE_TOO_LARGE",0.86,"size_chart","product_attribute"); evidence["SIZE_TOO_LARGE"].append("actual measurement is larger than published measurement")
            if "listing says" in ret and "measures" in ret:
                add("PRODUCT_SPEC_ERROR",0.98,"return_text","product_attribute","size_chart"); evidence["PRODUCT_SPEC_ERROR"].append("return text explicitly contrasts listing value with actual item")
        if any(x in ret for x in ["too tight","too small","smaller","tight","not enough room"]):
            add("SIZE_TOO_SMALL",0.78,"return_text"); evidence["SIZE_TOO_SMALL"].append("return text reports smaller/tighter fit")
        if any(x in ret for x in ["too loose","too large","too big","bigger","roomy"]):
            add("SIZE_TOO_LARGE",0.78,"return_text"); evidence["SIZE_TOO_LARGE"].append("return text reports larger/looser fit")
        if ("regular fit" in listing and "slim" in listing) or "model page" in ret:
            add("LISTING_CONTENT_ERROR",0.93,"listing_content","return_text"); evidence["LISTING_CONTENT_ERROR"].append("listing/model fit presentation conflicts with product fit")
        if any(x in ins for x in ["tear","damaged","broken","stain","defect"]):
            best_damage_score=score["QUALITY_DAMAGE"]
            for lab in score:
                if lab!="QUALITY_DAMAGE": score[lab]=min(score[lab],best_damage_score*0.70)
        best=max(score,key=score.get); confidence=min(0.99,float(score[best]))
        if not ret.strip(): confidence*=0.92
        if not ins.strip(): confidence*=0.97
        evidence_count=len(sources[best]); evidence_count=max(evidence_count,1 if evidence[best] else 0)
        label=best if confidence>=CONFIDENCE_THRESHOLD and evidence_count>0 else "UNKNOWN_REVIEW"
        high=label!="UNKNOWN_REVIEW" and confidence>=HIGH_PRIORITY_THRESHOLD and evidence_count>=MIN_EVIDENCE_HIGH_PRIORITY
        src=[]
        names=[("return_text","return text"),("product_attribute","product attributes"),("size_chart","size chart"),("listing_content","listing content"),("customer_action","customer action"),("inspection_finding","inspection findings")]
        for f,n in names:
            v=str(row.get(f,"") or "").strip()
            if v and f in sources[best]: src.append(f"{n}: {v}")
        return {"predicted_label":label,"confidence":round(confidence,4),"high_priority":bool(high),"evidence_count":int(evidence_count),"evidence":src+evidence[best]}
