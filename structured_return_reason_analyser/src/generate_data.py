import random
from pathlib import Path
import pandas as pd
SEED=28
random.seed(SEED)
ROWS=[
("R001","P001","M","Too tight around chest; smaller than the size chart.","chest 40","chest 40","Slim fit","Fits true to size","customer tried on","measured chest 37; no damage","SIZE_TOO_SMALL","normal"),
("R002","P002","L","Very loose and much bigger than expected.","chest 44","chest 44","Relaxed fit","Runs slightly large","customer tried on","measured chest 47; no damage","SIZE_TOO_LARGE","normal"),
("R003","P003","32","Waist is not 32 as shown. Actual jeans measure 34.","waist 32","waist 34","Regular fit","True to size","customer tried on","measured waist 34; tag 32","SIZE_CHART_MISMATCH","normal"),
("R004","P004","L","Listing says chest 42 but item measures 40.","chest 42","chest 40","Regular fit","Fits true to size","customer compared with chart","inspection confirms 40; no damage","PRODUCT_SPEC_ERROR","normal"),
("R005","P005","34","I selected the wrong size; my mistake.","waist 34","waist 34","Regular fit","True to size","customer selected wrong size","inspection matches 34; no damage","CUSTOMER_ORDER_SELECTION","normal"),
("R006","P006","M","The tee has a tear near the sleeve.","chest 44","chest 44","Oversized","Oversized by design","customer noticed tear","inspection confirms tear","QUALITY_DAMAGE","normal"),
("R007","P001","M","The model page makes this look regular, but it is slim.","chest 40","chest 40","Slim fit","Listing says regular fit; product is slim","customer compared model photos","listing says regular fit; product is slim","LISTING_CONTENT_ERROR","normal"),
("D001","P001","M","","chest 40","chest 40","Slim fit","Fits true to size","customer tried on","measured chest 37; no damage","SIZE_TOO_SMALL","disruption"),
("D002","P002","L","way too loose","chest 44","chest 44","Relaxed fit","Runs slightly large","customer tried on","inspection unavailable","SIZE_TOO_LARGE","disruption"),
("D003","P003","32","chart says 32, actual 34","waist 32","waist 34","Regular fit","True to size","customer tried on","measurement unavailable","SIZE_CHART_MISMATCH","disruption"),
("D004","P006","M","too small but item has a large tear","chest 42","chest 40","Regular fit","Fits true to size","customer tried on","tear confirmed; chest 40","QUALITY_DAMAGE","disruption"),
("R008","P001","M","Chest feels smaller than expected.","chest 40","chest 40","Slim fit","Fits true to size","tried on","measured chest 37; no damage","SIZE_TOO_SMALL","normal"),
("R009","P002","L","Too roomy; bigger than the listed fit.","chest 44","chest 44","Relaxed fit","Runs slightly large","tried on","measured chest 47; no damage","SIZE_TOO_LARGE","normal"),
("R010","P003","32","Published waist is 32 but received garment measures 34.","waist 32","waist 34","Regular fit","True to size","tried on","measurement 34; tag 32","SIZE_CHART_MISMATCH","normal"),
("R011","P004","L","The stored product attribute says 42 but the garment is 40.","chest 42","chest 40","Regular fit","Fits true to size","compared with listing","confirmed 40; no damage","PRODUCT_SPEC_ERROR","normal"),
("R012","P005","34","My mistake, I selected the wrong size.","waist 34","waist 34","Regular fit","True to size","ordered wrong size","inspection matches 34; no damage","CUSTOMER_ORDER_SELECTION","normal"),
("R013","P006","M","Torn sleeve, not a sizing issue.","chest 44","chest 44","Oversized","Oversized by design","noticed damage","tear confirmed","QUALITY_DAMAGE","normal")]
def main():
    cols=["return_id","product_id","ordered_size","return_text","size_chart","product_attribute","fit_type","listing_content","customer_action","inspection_finding","ground_truth","day_type"]
    out=pd.DataFrame(ROWS,columns=cols)
    root=Path(__file__).resolve().parents[1]/"data"; root.mkdir(exist_ok=True)
    out.to_csv(root/"returns.csv",index=False)
    print(f"Wrote {len(out)} rows")
if __name__=="__main__": main()
