from __future__ import annotations
import json,re,math
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# Small dependency-free BM25 implementation so the take-home runs offline after pip install.
class BM25Lite:
    def __init__(self, corpus, k1=1.5,b=0.75):
        self.k1=k1; self.b=b; self.N=len(corpus); self.df={}; self.tf=[]; self.lengths=[]; self.postings={}
        for i,doc in enumerate(corpus):
            c={}
            for t in doc: c[t]=c.get(t,0)+1
            self.tf.append(c); self.lengths.append(len(doc))
            for t in c:
                self.df[t]=self.df.get(t,0)+1; self.postings.setdefault(t,[]).append(i)
        self.avgdl=sum(self.lengths)/max(self.N,1)
    def score_candidates(self,query,candidates):
        scores={i:0.0 for i in candidates}; q=set(query)
        for t in q:
            df=self.df.get(t,0)
            if not df: continue
            idf=math.log(1+(self.N-df+0.5)/(df+0.5))
            for i in self.postings.get(t,[]):
                if i not in scores: continue
                f=self.tf[i].get(t,0); dl=self.lengths[i]
                scores[i]+=idf*(f*(self.k1+1))/(f+self.k1*(1-self.b+self.b*dl/max(self.avgdl,1e-9)))
        return scores

def tok(s): return re.findall(r"[a-z0-9']+", str(s).lower())

class HybridRetriever:
    def __init__(self, rows):
        self.rows=rows
        texts=[r["customer"] for r in rows]
        self.bm25=BM25Lite([tok(x) for x in texts])
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,min_df=1,max_features=100000)
        self.X=normalize(self.vectorizer.fit_transform(texts))
    @classmethod
    def from_jsonl(cls,path):
        p=Path(path)
        if p.suffix==".json": rows=json.loads(p.read_text(encoding="utf-8"))
        else: rows=[json.loads(x) for x in p.open(encoding="utf-8")]
        return cls(rows)
    def search(self,query,k=5):
        tokens=tok(query); q=self.vectorizer.transform([query]); dense=np.asarray(self.X.dot(q.T).toarray()).ravel()
        candidate_n=min(1500,len(dense)); cand=np.argpartition(-dense,candidate_n-1)[:candidate_n] if candidate_n else np.array([],dtype=int)
        cand=list(map(int,cand)); bm=self.bm25.score_candidates(tokens,cand)
        tf_rank=sorted(cand,key=lambda i:dense[i],reverse=True); bm_rank=sorted(cand,key=lambda i:bm.get(i,0),reverse=True)
        scores={}
        for rank,i in enumerate(tf_rank): scores[i]=scores.get(i,0)+1/(60+rank+1)
        for rank,i in enumerate(bm_rank): scores[i]=scores.get(i,0)+1/(60+rank+1)
        order=sorted(scores,key=scores.get,reverse=True)[:k]
        return [{**self.rows[i],"retrieval_score":float(scores[i]),"bm25_score":float(bm.get(i,0)),"tfidf_score":float(dense[i])} for i in order]
