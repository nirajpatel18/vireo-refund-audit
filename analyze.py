#!/usr/bin/env python3
import argparse, os, re, json
from pathlib import Path
import pandas as pd, numpy as np

PATTERNS={
"CANCEL":[r"\bcancel(?:led|lation)?\b",r"ordered by mistake",r"wrong colour",r"stop the shipment",r"don't ship"],
"DUP-PAYMENT":[r"double charge",r"duplicate",r"two payments",r"charged twice",r"charged two",r"twice",r"payment was deducted but no order",r"amount deducted without order",r"no order (was )?created"],
"PRICE-ADJ":[r"coupon",r"discount",r"promo",r"price adjustment",r"offer",r"discount not applied"],
"LOST-TRANSIT":[r"not delivered",r"not received",r"haven't received",r"nothing in hand",r"delivery delayed",r"shipment.*not",r"stuck on shipped",r"out for delivery"],
"RETURN-QC-OK":[r"refund not",r"refund.*delay",r"refund.*credited",r"reverse pickup",r"pickup.*pending",r"return.*refund",r"qc status",r"pickup not done"],
"DOA-REPL":[r"damaged",r"crack",r"dead on arrival",r"arrived.*damage",r"not working",r"doesn't work",r"won't charge",r"not charging",r"low mic",r"fault",r"single side"],
"WTY-BUYBACK":[r"warranty",r"repair",r"\brma\b",r"service centre",r"buyback",r"firmware",r"battery drain",r"pairing"],
}
def local_reason(row):
    txt=f"{row.get('customer_message','')} {row.get('agent_notes','')}".lower()
    scores={k:sum(len(re.findall(p,txt)) for p in pats) for k,pats in PATTERNS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best] else "REVIEW"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default=".")
    ap.add_argument("--ai",action="store_true")
    args=ap.parse_args()
    d=Path(args.data_dir); out=d/"outputs"; out.mkdir(exist_ok=True)
    t=pd.read_csv(d/"tickets.csv"); a=pd.read_csv(d/"agents.csv"); p=pd.read_csv(d/"products.csv")
    t["created_at"]=pd.to_datetime(t["created_at"])
    t["refund_amount_inr"]=pd.to_numeric(t["refund_amount_inr"],errors="coerce")
    t["_src_priority"]=t["source_system"].map({"helpdesk":0,"legacy_fd":1}).fillna(9)
    c=t.sort_values(["ticket_id","_src_priority"]).drop_duplicates("ticket_id").copy()
    paired=t.groupby(["ticket_id","source_system"])["refund_amount_inr"].first().unstack()
    ratios=(paired["legacy_fd"]/paired["helpdesk"]).dropna()
    scale=float(ratios.mode().iloc[0]) if len(ratios) else 100.0
    if abs(scale-100)>1e-9: raise RuntimeError(f"Unexpected legacy scale: {scale}")
    c["refund_inr_normalized"]=np.where(c["source_system"].eq("legacy_fd"),c["refund_amount_inr"]/scale,c["refund_amount_inr"])
    c=c.merge(a[["agent_id","name","team","tier"]],on="agent_id",how="left")
    c=c.merge(p[["sku","unit_cost_inr"]],left_on="product_sku",right_on="sku",how="left")
    c["refund_flag"]=c["refund_inr_normalized"].notna()
    c["dual_fulfilment_flag"]=c["refund_flag"]&c["replacement_issued"].eq("Y")
    c["replacement_cost_inr"]=np.where(c["replacement_issued"].eq("Y")&c["unit_cost_inr"].notna(),c["unit_cost_inr"]+340,0)
    c["dual_fulfilment_exposure_inr"]=np.where(c["dual_fulfilment_flag"],c["refund_inr_normalized"].fillna(0)+c["replacement_cost_inr"],0)
    r=c[c["refund_flag"]].copy()
    r["text_audit_reason"]=r.apply(local_reason,axis=1)
    r["reason_mismatch_flag"]=r["text_audit_reason"].ne("REVIEW")&r["text_audit_reason"].ne(r["refund_reason_code"])

    # Optional LLM mode. Requires user-supplied key/model.
    if args.ai:
        try:
            from openai import OpenAI
            client=OpenAI()
            model=os.environ["OPENAI_MODEL"]
            prompt=open(d/"prompts"/"reason_code_audit.md",encoding="utf-8").read()
            ai_reason=[]; ai_conf=[]; ai_basis=[]
            for _,row in r.iterrows():
                inp=prompt+"\n\nCustomer:\n"+str(row.customer_message)+"\n\nAgent notes:\n"+str(row.agent_notes)
                resp=client.responses.create(model=model,input=inp)
                try:
                    obj=json.loads(resp.output_text.strip())
                except Exception:
                    obj={"reason":"REVIEW","confidence":0,"basis":"invalid JSON"}
                ai_reason.append(obj.get("reason","REVIEW")); ai_conf.append(obj.get("confidence",0)); ai_basis.append(obj.get("basis",""))
            r["ai_reason"]=ai_reason; r["ai_confidence"]=ai_conf; r["ai_basis"]=ai_basis
        except Exception as e:
            r["ai_reason"]="AI_UNAVAILABLE"; r["ai_confidence"]=0; r["ai_basis"]=str(e)

    r["month"]=r["created_at"].dt.to_period("M").astype(str)
    r.groupby(["month","refund_reason_code"]).agg(refund_tickets=("ticket_id","count"),refund_value_inr=("refund_inr_normalized","sum")).reset_index().to_csv(out/"monthly_refunds_by_reason.csv",index=False)
    r.groupby(["month","agent_id","name","team","tier"]).agg(refund_tickets=("ticket_id","count"),refund_value_inr=("refund_inr_normalized","sum"),dual_fulfilment_tickets=("dual_fulfilment_flag","sum"),dual_fulfilment_exposure_inr=("dual_fulfilment_exposure_inr","sum")).reset_index().to_csv(out/"monthly_refunds_by_agent.csv",index=False)
    ag=c.groupby(["agent_id","name","team","tier"]).agg(tickets=("ticket_id","count"),refund_tickets=("refund_flag","sum"),refund_value_inr=("refund_inr_normalized","sum"),dual_fulfilment_tickets=("dual_fulfilment_flag","sum"),dual_fulfilment_exposure_inr=("dual_fulfilment_exposure_inr","sum")).reset_index()
    ag["refund_rate"]=ag["refund_tickets"]/ag["tickets"]; ag["refund_value_per_ticket"]=ag["refund_value_inr"]/ag["tickets"]
    ag.sort_values("refund_value_inr",ascending=False).to_csv(out/"agent_summary.csv",index=False)
    r[r["dual_fulfilment_flag"]|r["reason_mismatch_flag"]].to_csv(out/"review_queue.csv",index=False)
    print(f"Canonical tickets: {len(c):,}")
    print(f"Refund tickets: {len(r):,}")
    print(f"Normalized refunds: ₹{r.refund_inr_normalized.sum():,.0f}")
    print(f"Refund+replacement exceptions: {int(c.dual_fulfilment_flag.sum()):,}")
    print(f"Dual-fulfilment exposure: ₹{c.dual_fulfilment_exposure_inr.sum():,.0f}")
    print(f"Legacy scale: {scale:g}x")
if __name__=="__main__": main()
