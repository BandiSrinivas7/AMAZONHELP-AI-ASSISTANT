from __future__ import annotations
import csv, json, re
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

COLS=["tweet_id","author_id","inbound","created_at","text","response_tweet_id","in_response_to_tweet_id"]

def clean_text(text: str) -> str:
    text=re.sub(r"https?://\S+", " URL ", str(text))
    return re.sub(r"\s+", " ", text).strip()

def _scan_parent_map(input_csv: str, brand: str):
    parent={}; brand_ids=[]; rows=0
    with open(input_csv,"r",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        for r in reader:
            rows += 1
            tid=r.get("tweet_id")
            if not tid: continue
            try: tid=int(tid)
            except: continue
            p=r.get("in_response_to_tweet_id")
            try: parent[tid]=int(p) if p not in (None,"") else -1
            except: parent[tid]=-1
            if (r.get("author_id") or "").strip()==brand:
                brand_ids.append(tid)
    return parent, brand_ids, rows

def _select_ancestors(parent, brand_ids):
    selected=set()
    for start in brand_ids:
        x=start; seen=set()
        while x not in seen and x in parent:
            seen.add(x); selected.add(x)
            p=parent[x]
            if p == -1 or p not in parent: break
            x=p
    return selected

def build(input_csv: str, output_dir: str, brand="AmazonHelp") -> dict:
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    parent, brand_ids, total_rows = _scan_parent_map(input_csv, brand)
    selected=_select_ancestors(parent, brand_ids)
    conversations={}
    # Second pass: only materialize selected rows; memory is now small.
    with open(input_csv,"r",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        for r in reader:
            try: tid=int(r.get("tweet_id"))
            except: continue
            if tid not in selected: continue
            conversations[tid]={
                "tweet_id":tid,
                "author_id":(r.get("author_id") or "").strip(),
                "inbound":(r.get("inbound") or "").strip().lower() in {"true","1"},
                "created_at":r.get("created_at") or "",
                "text":r.get("text") or "",
                "clean_text":clean_text(r.get("text") or ""),
                "parent_id":parent.get(tid,-1)
            }
    # Build components from selected ancestry chains.
    children=defaultdict(list)
    for tid,r in conversations.items():
        p=r["parent_id"]
        if p in conversations: children[p].append(tid)
    roots=[]
    for tid in conversations:
        p=conversations[tid]["parent_id"]
        if p not in conversations: roots.append(tid)
    seen=set(); convs=[]
    for root in roots:
        stack=[root]; ids=[]
        while stack:
            x=stack.pop()
            if x in seen: continue
            seen.add(x); ids.append(x); stack.extend(children.get(x,[]))
        rows=[conversations[x] for x in ids]
        if not any(r["inbound"] for r in rows): continue
        if not any(r["author_id"]==brand for r in rows): continue
        rows.sort(key=lambda r:(r["created_at"],r["tweet_id"]))
        rows=[r for r in rows if len(r["clean_text"])>=8]
        if len(rows)>=2:
            convs.append((root,rows))
    rng=np.random.default_rng(42); idx=np.arange(len(convs)); rng.shuffle(idx)
    n=len(idx); split={convs[i][0]:("train" if j<int(.70*n) else "dev" if j<int(.85*n) else "test") for j,i in enumerate(idx)}
    conv_path=out/"amazonhelp_conversations.jsonl"; pair_path=out/"amazonhelp_reply_pairs.jsonl"
    pairs=0
    with conv_path.open("w",encoding="utf-8") as fc, pair_path.open("w",encoding="utf-8") as fp:
        for root_id,rows in convs:
            cid=f"amazon_{root_id}"; turns=[]
            for r in rows:
                turns.append({"tweet_id":r["tweet_id"],"role":"customer" if r["inbound"] else "agent","created_at":r["created_at"],"text":r["text"],"clean_text":r["clean_text"]})
            fc.write(json.dumps({"conversation_id":cid,"split":split[root_id],"turns":turns},ensure_ascii=False)+"\n")
            # Pair each customer turn with the first later AmazonHelp reply in the same component.
            for i,r in enumerate(rows):
                if not r["inbound"]: continue
                reply=next((z for z in rows[i+1:] if z["author_id"]==brand and z["created_at"]>=r["created_at"]),None)
                if reply:
                    fp.write(json.dumps({"conversation_id":cid,"split":split[root_id],"customer":r["clean_text"],"reply":reply["clean_text"]},ensure_ascii=False)+"\n"); pairs+=1
    pd.DataFrame([{"conversation_id":f"amazon_{rid}","split":split[rid],"tweet_count":len(rows),"customer_tweets":sum(r["inbound"] for r in rows),"agent_replies":sum(r["author_id"]==brand for r in rows)} for rid,rows in convs]).to_csv(out/"conversation_index.csv",index=False)
    summary={"brand":brand,"total_rows":total_rows,"raw_brand_tweets":len(brand_ids),"selected_tweets":len(selected),"usable_conversations":len(convs),"reply_pairs":pairs,"split_counts":pd.Series(list(split.values())).value_counts().to_dict()}
    (out/"phase1_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    return summary
