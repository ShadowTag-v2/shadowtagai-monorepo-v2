# Original Path: “#p-env/“#p-env.txt

# Categories: LEGAL

“#p-env
%%bash
set -e;p=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)};r=${P_AI_REGION:-us-central1};b=${P*BUCKET:-pnkln-$p-$r};echo -n $p>$HOME/.p;echo -n $r>$HOME/.r;echo -n $b>$HOME/.b;gcloud config set project $p 1>/dev/null;printf p=%s r=%s b=%s\n "$p" "$r" "$b"
#p-pip
%%bash
python - <<'PY'
import sys,subprocess as s
for x in["google-cloud-aiplatform","vertexai","google-cloud-storage","google-cloud-vision","numpy"]:s.run([sys.executable,"-m","pip","-q","install","-U",x],check=True)
print(0)
PY
#p-vertex
%%python
import os,vertexai
h=os.path.expanduser("~");p=open(h+'/.p').read();r=open(h+'/.r').read();vertexai.init(project=p,location=r);print(p,r)
#p-bucket
%%python
import os
from google.cloud import storage
h=os.path.expanduser("~");p=open(h+'/.p').read();r=open(h+'/.r').read();b=open(h+'/.b').read();c=storage.Client(project=p)
try:c.create_bucket(b,location=r)
except Exception:pass
print(b)
#p-paths
%%python
import os,uuid
h=os.path.expanduser("~");b=open(h+'/.b').read();loc="/tmp/pnkln";os.makedirs(loc,exist_ok=True);print(loc,b)
#p-util
%%python
import os,sys,json,gzip,io,base64,hashlib,numpy as np
def rd(p):return open(p,"rb").read()
def wr(p,x):open(p,"wb").write(x if isinstance(x,(bytes,bytearray)) else (x if isinstance(x,bytes) else (x.encode() if isinstance(x,str) else json.dumps(x,separators=(',',':')).encode())));return p
def j(x):return json.dumps(x,separators=(',',':'))
def gz(x):return gzip.compress(x if isinstance(x,(bytes,bytearray)) else (x.encode() if isinstance(x,str) else j(x).encode()))
def ug(x):return gzip.decompress(x)
def h(x):return hashlib.sha256(x if isinstance(x,(bytes,bytearray)) else x.encode()).hexdigest()[:16]
def cs(a,b):a=np.array(a);b=np.array(b);return float(a.dot(b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
print(0)
#p-gcs
%%python
from google.cloud import storage
h=os.path.expanduser("~");p=open(h+'/.p').read();b=open(h+'/.b').read();c=storage.Client(project=p);bk=c.bucket(b)
def up(k,x):bk.blob(k).upload*from_string(x if isinstance(x,(bytes,bytearray)) else (x.encode() if isinstance(x,str) else j(x)),'application/octet-stream');return f"gs://{b}/{k}"
def dl(k):return bk.blob(k).download_as_bytes()
print(0)
#p-gem
%%python
from vertexai.generative_models import GenerativeModel,Part
gm=GenerativeModel("gemini-3.1-family")
def gen(p):return gm.generate_content(p).text
print(gen("ok")[:2])
#p-emb
%%python
from vertexai.language_models import TextEmbeddingModel
em=TextEmbeddingModel.from_pretrained("text-embedding-005")
def emb(t):return em.get_embeddings([t])[0].values
print(len(emb("x")))
#p-ocr
%%python
from google.cloud import vision
vc=vision.ImageAnnotatorClient()
def ocr_path(p):with open(p,"rb") as f:img=vision.Image(content=f.read());r=vc.document_text_detection(image=img);return r.full_text_annotation.text if r.full_text_annotation.text else (r.text_annotations[0].description if r.text_annotations else "")
print(0)
#p-ocr-sum
%%python
def ocr_sum(paths):t=[];
for p in paths:
try:t.append(ocr_path(p))
except Exception as e:t.append("")
s="\n\n".join(t);r=gen([Part.from_text("summarize ocr:"),Part.from_text(s)]);return r
print(0)
#p-rag-build
%%python
import os,json,numpy as np
def rag_build(items,out_np,out_json):
v=[];m=[]
for it in items:
e=np.array(emb(it["t"]),dtype=np.float32);v.append(e);m.append({"k":it["k"],"t":it["t"]})
np.save(out_np,np.stack(v,0));wr(out_json,j(m))
print(0)
#p-rag-query
%%python
import numpy as np,json
def rag_query(q,npf,mpf,top=3):
V=np.load(npf);M=json.loads(open(mpf).read());e=np.array(emb(q));s=[(i,float(V[i].dot(e)/(np.linalg.norm(V[i])*np.linalg.norm(e)+1e-9))) for i in range(len(M))];s.sort(key=lambda x:x[1],reverse=True);R=[M[i] for i,* in s[:top]];ctx="\n".join(x["t"] for x in R);a=gen([Part.from_text("use context:"),Part.from_text(ctx),Part.from_text("q:"+q)]);return a
print(0)
#p-batch-sum
%%python
def batch_sum(txts,sz=8):o=[]
for i in range(0,len(txts),sz):o.append(gen("summarize:"+("\n".join(txts[i:i+sz]))))
return o
print(0)
#p-prompts
%%python
P={"spec":"You are pnkln systems. Produce terse JSON plan.","contract":"Summarize positions into his/hers matrix JSON.","lawcal":"Extract deadlines & triggers JSON.","neg":"List open issues, missing terms JSON.","risk":"Top-5 risks JSON with mitigations."};print(len(P))
#p-spec
%%python
def run_spec(x):return gen([Part.from_text(P["spec"]),Part.from_text(x)])
print(0)
#p-dead
%%python
def run_dead(x):return gen([Part.from_text(P["lawcal"]),Part.from_text(x)])
print(0)
#p-neg
%%python
def run_neg(x):return gen([Part.from_text(P["neg"]),Part.from_text(x)])
print(0)
#p-risk
%%python
def run_risk(x):return gen([Part.from_text(P["risk"]),Part.from_text(x)])
print(0)
#p-imgcap
%%python
def imgcap(p):b=open(p,"rb").read();pa=Part.from_data(mime_type="image/png",data=b);return gm.generate_content([Part.from_text("caption briefly"),pa]).text
print(0)
#p-ocr-dir
%%python
import os,glob
def ocr_dir(d):fs=sorted(sum([[*glob.glob(os.path.join(d,ext))] for ext in("\*.png","_.jpg","_.jpeg","_.webp","_.tif","\_.bmp","\*.pdf")],[]));txt=[ocr_path(f) for f in fs if os.path.isfile(f)];s=ocr_sum([]) if not txt else gen("summarize:\n"+("\n".join(txt)));return {"n":len(fs),"sum":s}
print(0)
#p-io-api
%%python
def save_txt(k,t):return up(k,t)
def save_json(k,x):return up(k,j(x))
def load(k):return dl(k)
print(0)
#p-mini-demo
%%python
S=["This is a sample clause about payments due in 30 days.","Another clause: counterparty may terminate with 10-day notice.","Filing served triggers a 20-day response deadline."]
wr("/tmp/rag.jsonl","\n".join(j({"k":str(i),"t":t}) for i,t in enumerate(S)))
import json,numpy as np
items=[{"k":str(i),"t":t} for i,t in enumerate(S)]
rag_build(items,"/tmp/rag.npy","/tmp/rag.meta.json");print(rag_query("what are deadlines?", "/tmp/rag.npy","/tmp/rag.meta.json")[:120])
#p-end
%%python
print("pnkln-ready")”
