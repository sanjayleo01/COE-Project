KEYWORDS={
"SIZE_TOO_SMALL":["too tight","too small","smaller","tight"],
"SIZE_TOO_LARGE":["too loose","too large","too big","bigger","roomy"],
"SIZE_CHART_MISMATCH":["size chart","chart says","published","measurement","actual","measures"],
"LISTING_CONTENT_ERROR":["listing","description","model","photo","shown"],
"PRODUCT_SPEC_ERROR":["product spec","stored","attribute","specification"],
"CUSTOMER_ORDER_SELECTION":["ordered wrong","selected wrong","my mistake","different size"],
"QUALITY_DAMAGE":["tear","damaged","broken","stain","defect"],
}
def baseline_predict(row):
    text=" ".join(str(row.get(k,"") or "") for k in ["return_text","listing_content","customer_action","inspection_finding"]).lower()
    for label,kws in KEYWORDS.items():
        if any(k in text for k in kws): return label
    return "UNKNOWN_REVIEW"
