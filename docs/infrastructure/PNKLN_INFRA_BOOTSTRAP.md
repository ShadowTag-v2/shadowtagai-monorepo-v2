# Pnkln Phase 1 Infrastructure Bootstrap (Vertex AI Studio Cells)

## Env Setup

```python
import os,uuid,json,base64,random,string as s
def env(k,v):os.environ[k]=v
pnkln={"ORG_ID":"","BILLING_ACCOUNT":"","FOLDER_ID":"","PROJECT_ID":f"pnkln-{uuid.uuid4().hex[:8]}","REGION":"us-central1","LOC":"us","REPO":"pnkln","BUCKET":f"pnkln-{uuid.uuid4().hex[:8]}","BQ":"pnkln_core","SA":"pnkln-svc","VERTICALS":["legal","aivideo","defense","tower","transport","commerce"],"IMAGE":"us-docker.pkg.dev/cloudrun/container/hello","CHANNEL":"stable"}
for k,v in pnkln.items():env(f"PNKLN_{k}",v if isinstance(v,str) else json.dumps(v))
print(json.dumps(pnkln))

```

## GCP Project

```bash
set -euo pipefail
gcloud services enable cloudresourcemanager.googleapis.com billingbudgets.googleapis.com --quiet
gcloud projects create "${PNKLN_PROJECT_ID}"${PNKLN_FOLDER_ID:+ --folder="${PNKLN_FOLDER_ID}"} --quiet
gcloud beta billing projects link "${PNKLN_PROJECT_ID}" --billing-account="${PNKLN_BILLING_ACCOUNT}" --quiet
gcloud config set project "${PNKLN_PROJECT_ID}"

```

## APIs Enable

```bash
set -euo pipefail
gcloud services enable aiplatform.googleapis.com run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com iam.googleapis.com iamcredentials.googleapis.com compute.googleapis.com servicenetworking.googleapis.com cloudkms.googleapis.com pubsub.googleapis.com bigquery.googleapis.com storage.googleapis.com workflows.googleapis.com cloudscheduler.googleapis.com logging.googleapis.com monitoring.googleapis.com eventarc.googleapis.com vision.googleapis.com documentai.googleapis.com --quiet

```

## IAM Service Account

```bash
set -euo pipefail
SA_EMAIL="${PNKLN_SA}@${PNKLN_PROJECT_ID}.iam.gserviceaccount.com"
gcloud iam service-accounts create "${PNKLN_SA}" --display-name=pnkln --quiet
roles=(roles/aiplatform.admin roles/run.admin roles/artifactregistry.admin roles/iam.serviceAccountUser roles/storage.admin roles/secretmanager.admin roles/bigquery.admin roles/pubsub.admin roles/workflows.admin roles/cloudscheduler.admin roles/logging.configWriter roles/monitoring.admin)
for r in "${roles[@]}";do gcloud projects add-iam-policy-binding "${PNKLN_PROJECT_ID}" --member "serviceAccount:${SA_EMAIL}" --role "$r" --quiet;done
gcloud iam service-accounts keys create sa-key.json --iam-account="${SA_EMAIL}"

```

## Artifact Registry

```bash
set -euo pipefail
gcloud artifacts repositories create "${PNKLN_REPO}" --repository-format=docker --location="${PNKLN_REGION}" --quiet || true
gcloud auth configure-docker "${PNKLN_REGION}-docker.pkg.dev" --quiet

```

## GCS Core

```bash
set -euo pipefail
gsutil mb -l "${PNKLN_REGION}" "gs://${PNKLN_BUCKET}"
gsutil versioning set on "gs://${PNKLN_BUCKET}"
printf '{}' | gsutil cp - "gs://${PNKLN_BUCKET}/bootstrap.json"

```

## BigQuery Core

```bash
set -euo pipefail
bq --location="${PNKLN_LOC}" mk -d "${PNKLN_BQ}" || true
bq mk --table "${PNKLN_BQ}.events" schema:ts:TIMESTAMP,vertical:STRING,kind:STRING,id:STRING,data:JSON || true
bq mk --table "${PNKLN_BQ}.metrics" schema:ts:TIMESTAMP,name:STRING,val:FLOAT64,labels:JSON || true

```

## PubSub Core

```bash
set -euo pipefail
for t in ingress events metrics ocr doc intake;do gcloud pubsub topics create "pnkln-${t}" --quiet || true; gcloud pubsub subscriptions create "pnkln-${t}-sub" --topic="pnkln-${t}" --quiet || true;done

```

## Secrets Core

```bash
set -euo pipefail
for n in OPENAI_API_KEY COHERE_API_KEY ANTHROPIC_API_KEY HF_TOKEN PNKLN_EDGE_TOKEN;do echo -n "setme" | gcloud secrets create "$n" --data-file=- --replication-policy="automatic" --quiet || gcloud secrets versions add "$n" --data-file=<(echo -n "setme") --quiet;done

```

## Container Sample

```bash
set -euo pipefail
cat > Dockerfile <<'EOF'
FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY app.py /app/app.py
CMD ["app.py"]
EOF
cat > app.py <<'EOF'
from http.server import BaseHTTPRequestHandler,HTTPServer,os
class H(BaseHTTPRequestHandler):
  def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write((os.getenv("PNKLN_TAG","ok")).encode())
HTTPServer(('',8080),H).serve_forever()
EOF
IMG="${PNKLN_REGION}-docker.pkg.dev/${PNKLN_PROJECT_ID}/${PNKLN_REPO}/core:$(date +%s)"
gcloud builds submit --tag "$IMG" --quiet
echo -n "$IMG">img.txt

```

## Run Deploy

```bash
set -euo pipefail
IMG=$(cat img.txt)
gcloud run deploy pnkln-core --image "$IMG" --region "${PNKLN_REGION}" --platform managed --allow-unauthenticated --service-account "${PNKLN_SA}@${PNKLN_PROJECT_ID}.iam.gserviceaccount.com" --project "${PNKLN_PROJECT_ID}" --quiet

```

## Vertex Datasets

```python
from google.cloud import aiplatform as ai,storage
import os,json,time
ai.init(project=os.environ["PNKLN_PROJECT_ID"],location=os.environ["PNKLN_REGION"])
gcs=f'gs://{os.environ["PNKLN_BUCKET"]}/vertex/'
storage.Client().bucket(os.environ["PNKLN_BUCKET"]).blob("vertex/.keep").upload_from_string(b"")
print(gcs)

```

## Vertex Model Upload

```python
from google.cloud import aiplatform as ai,storage,exceptions
import os,uuid
ai.init(project=os.environ["PNKLN_PROJECT_ID"],location=os.environ["PNKLN_REGION"])
bucket=os.environ["PNKLN_BUCKET"];b=storage.Client().bucket(bucket)
b.blob("models/dummy/model.txt").upload_from_string(b"pnkln")
m=ai.Model.upload(display_name=f"pnkln-dummy-{uuid.uuid4().hex[:6]}",artifact_uri=f"gs://{bucket}/models/dummy",serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.2-3:latest")
m.wait();print(m.resource_name)

```

## Vertex Endpoint

```python
from google.cloud import aiplatform as ai
import os,uuid
ai.init(project=os.environ["PNKLN_PROJECT_ID"],location=os.environ["PNKLN_REGION"])
e=ai.Endpoint.create(display_name=f"pnkln-endpoint-{uuid.uuid4().hex[:6]}");e.wait();print(e.resource_name)

```

## Vertex Deploy

```python
from google.cloud import aiplatform as ai
ai.init()
m=list(ai.Model.list(order_by="create_time desc",filter='display_name:pnkln-dummy'))[0]
e=list(ai.Endpoint.list(order_by="create_time desc",filter='display_name:pnkln-endpoint'))[0]
e.deploy(model=m,machine_type="n1-standard-4",traffic_percentage=100);print("ok")

```

## Pipelines Min

```python
from kfp import dsl
from kfp.v2 import compiler
@dsl.pipeline(name="pnkln-mini")
def p():
  op=dsl.ContainerOp(name="echo",image="busybox",command=["sh","-lc"],arguments=["echo pnkln && date"])
compiler.Compiler().compile(pipeline_func=p,package_path="pnkln-mini.json")
print("pnkln-mini.json")

```

## Workflows Ingest

```bash
set -euo pipefail
cat > wf.yaml <<'Y'
main:
  params: [in]
  steps:

  - pub: {call: http.post, args: {url: "https://pubsub.googleapis.com/v1/projects/${sys.get_env(\"PNKLN_PROJECT_ID\")}/topics/pnkln-ingress:publish", auth: {type: OAuth2}, body: {"messages":[{"data": base64.encode(text.concat("ING:", string(in)))}]}}}

  - ret: {return: "ok"}
Y
gcloud workflows deploy pnkln-ingest --source wf.yaml --location "${PNKLN_REGION}" --quiet

```

## Scheduler Tick

```bash
set -euo pipefail
URL=$(gcloud run services describe pnkln-core --region "${PNKLN_REGION}" --format='value(status.url)')
gcloud scheduler jobs create http pnkln-ping --schedule="*/5 * * * *" --uri="${URL}" --http-method=GET --oidc-service-account-email="${PNKLN_SA}@${PNKLN_PROJECT_ID}.iam.gserviceaccount.com" --oidc-token-audience="${URL}" --quiet || gcloud scheduler jobs update http pnkln-ping --schedule="*/5 * * * *" --uri="${URL}" --http-method=GET --oidc-service-account-email="${PNKLN_SA}@${PNKLN_PROJECT_ID}.iam.gserviceaccount.com" --oidc-token-audience="${URL}" --quiet

```

## Logging Sink

```bash
set -euo pipefail
gcloud logging sinks create pnkln_bq_sink "bigquery.googleapis.com/projects/${PNKLN_PROJECT_ID}/datasets/${PNKLN_BQ}" --quiet || true

```

## Monitoring Uptime

```bash
set -euo pipefail
URL=$(gcloud run services describe pnkln-core --region "${PNKLN_REGION}" --format='value(status.url)')
cat > uptime.json <<EOF
{"displayName":"pnkln-core","monitoredResource":{"type":"uptime_url","labels":{"project_id":"${PNKLN_PROJECT_ID}"}},"httpCheck":{"path":"/","port":443,"useSsl":true,"authInfo":{}},"timeout":"10s","period":"60s","selectedRegions":["USA"],"resourceGroup":{"groupId":"","resourceType":"RESOURCE_TYPE_UNSPECIFIED"},"contentMatchers":[{"content":"ok"}],"syntheticMonitor":{"sslCheck":{}},"httpCheck":{"path":"/","port":443,"useSsl":true,"authInfo":{},"headers":{"Host":"$(echo "$URL"|sed 's#https://##' )"}}}
EOF
gcloud monitoring uptime create --config-from-file=uptime.json --quiet || true

```

## Event Ingest

```python
from google.cloud import pubsub_v1,logging_v2,bigquery
import os,json,time
p=os.environ["PNKLN_PROJECT_ID"]
pub=pubsub_v1.PublisherClient()
pub.publish(pub.topic_path(p,"pnkln-events"),json.dumps({"ts":time.time(),"vertical":"boot","kind":"ok","id":"init","data":{}}).encode())
bq=bigquery.Client();bq.query(f"INSERT INTO `{p}.{os.environ['PNKLN_BQ']}.metrics`(ts,name,val,labels) VALUES(CURRENT_TIMESTAMP(),'boot',1,JSON '{{}}')").result()
print("ok")

```

## OCR DocAI Batch

```python
from google.cloud import documentai_v1 as docai,storage,bigquery
import os,glob,json
p=os.environ["PNKLN_PROJECT_ID"];loc=os.environ["PNKLN_REGION"];proc="us:general-document-extractor"
gcs=f"gs://{os.environ['PNKLN_BUCKET']}/ingest/"
storage.Client().bucket(os.environ["PNKLN_BUCKET"]).blob("ingest/.keep").upload_from_string(b"")
print(json.dumps({"project":p,"location":loc,"processor":proc,"gcs_prefix":gcs}))

```

## Prompt Templates Min

```python
import json,os,sys
templates=[{"name":"pnkln_sys_clarity","role":"system","content":"You are Pnkln. Optimize for lawful, safe, high-ROI execution."},{"name":"pnkln_user_issue","role":"user","content":"Summarize issues, parties, deadlines, and required filings from: {{text}} -> JSON."},{"name":"pnkln_video_plan","role":"user","content":"Given transcript {{text}}, output a 60s hook+CTA storyboard JSON."},{"name":"pnkln_defense_parse","role":"user","content":"Given spec {{text}}, extract TRL, interfaces, env, constraints JSON."},{"name":"pnkln_tower_eval","role":"user","content":"Given site params {{json}}, return mast design SKU and BOM JSON."},{"name":"pnkln_transport_route","role":"user","content":"Given constraints {{json}}, return route plan and cost JSON."},{"name":"pnkln_commerce_bundle","role":"user","content":"Given catalog {{json}} and goal {{kpi}}, emit bundle + price JSON."}]
print(json.dumps(templates))

```

## Vertex Chat Studio Example

```python
from google.cloud import aiplatform as ai
import os,json
ai.init(project=os.environ["PNKLN_PROJECT_ID"],location=os.environ["PNKLN_REGION"])
req={"system_instruction":"You are Pnkln. Output JSON.","contents":[{"role":"user","parts":[{"text":"ping"}]}],"generation_config":{"temperature":0}}
print(json.dumps(req))

```

## Legal Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.legal_cases`(id STRING,party_a STRING,party_b STRING,jurisdiction STRING,status STRING,last_update TIMESTAMP)").result()
print("ok")

```

## AIVideo Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.aivideo_jobs`(id STRING,src_gcs STRING,dst_gcs STRING,status STRING,created TIMESTAMP)").result()
print("ok")

```

## Defense Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.defense_specs`(id STRING,agency STRING,trl INT64,deadline DATE,status STRING)").result()
print("ok")

```

## Tower Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.tower_sites`(id STRING,lat FLOAT64,lon FLOAT64,wind FLOAT64,code STRING,status STRING)").result()
print("ok")

```

## Transport Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.transport_routes`(id STRING,src STRING,dst STRING,cost FLOAT64,duration FLOAT64,status STRING)").result()
print("ok")

```

## Commerce Vertical Bootstrap

```python
from google.cloud import bigquery
import os
bq=bigquery.Client()
bq.query(f"CREATE TABLE IF NOT EXISTS `{os.environ['PNKLN_PROJECT_ID']}.{os.environ['PNKLN_BQ']}.commerce_orders`(id STRING,sku STRING,qty INT64,price FLOAT64,status STRING,ts TIMESTAMP)").result()
print("ok")

```

## Router Min

```python
import os,json,sys,time
def route(vertical,payload):
  t=time.time()
  return {"ts":t,"vertical":vertical,"input":payload,"out":{"ok":True},"lat":round(time.time()-t,6)}
print(json.dumps(route("boot",{"v":"pnkln"})))

```

## Events Emit

```python
from google.cloud import pubsub_v1
import os,json,time
p=os.environ["PNKLN_PROJECT_ID"];pub=pubsub_v1.PublisherClient()
for v in json.loads(os.environ["PNKLN_VERTICALS"]):
  pub.publish(pub.topic_path(p,"pnkln-events"),json.dumps({"ts":time.time(),"vertical":v,"kind":"init","id":v,"data":{}}).encode())
print("ok")

```

## Ingest HTTP CloudRun

```bash
set -euo pipefail
cat > Dockerfile <<'EOF'
FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine
RUN apk add --no-cache bash curl jq
ENV PORT=8080
CMD bash -lc 'while :;do { read l;[[ $l == $'\''\r'\'' ]]&&break;d+="$l"$'\''\n'\'';done; body=$(dd bs=1 count=${CONTENT_LENGTH:-0} 2>/dev/null); echo -e "HTTP/1.1 200 OK\r\n\r\nok"; done < /dev/tcp/0.0.0.0/$PORT'
EOF
IMG="${PNKLN_REGION}-docker.pkg.dev/${PNKLN_PROJECT_ID}/${PNKLN_REPO}/ingest:$(date +%s)"
gcloud builds submit --tag "$IMG" --quiet
gcloud run deploy pnkln-ingest --image "$IMG" --region "${PNKLN_REGION}" --allow-unauthenticated --service-account "${PNKLN_SA}@${PNKLN_PROJECT_ID}.iam.gserviceaccount.com" --quiet

```

## DocAI Vision Quick

```python
from google.cloud import vision,storage
import os,io,json
b=storage.Client().bucket(os.environ["PNKLN_BUCKET"])
b.blob("ocr/sample.txt").upload_from_string(b"pnkln")
print("ok")

```

## Studio Prompts Merge

```python
import os,json
merged={"legal":"{{facts}} -> deadlines JSON","aivideo":"{{transcript}} -> storyboard JSON","defense":"{{rqmt}} -> TRL/ifc JSON","tower":"{{site}} -> mast/BOM JSON","transport":"{{graph}} -> route JSON","commerce":"{{cart}} -> bundle JSON"}
print(json.dumps(merged))

```

## Policy Baseline

```bash
set -euo pipefail
cat > constraints.yaml <<'Y'
constraints:

- name: restrictVpcExternalIp
  value: DENY

- name: enforceUniformBucketLevelAccess
  value: REQUIRE

- name: restrictCrossProjectServiceAccounts
  value: DENY
Y
printf "%s" "$(cat constraints.yaml|tr -d '\n\t ' )"

```

## Run Labels

```bash
set -euo pipefail
for s in pnkln-core pnkln-ingest;do gcloud run services update "$s" --region "${PNKLN_REGION}" --update-labels "app=pnkln,phase=1" --quiet;done

```

## BQ Views

```bash
set -euo pipefail
bq query --use_legacy_sql=false "CREATE VIEW IF NOT EXISTS \`${PNKLN_PROJECT_ID}.${PNKLN_BQ}.v_events_daily\` AS SELECT DATE(TIMESTAMP_MILLIS(CAST(ts*1000 AS INT64))) d,vertical,kind,COUNT(*) c FROM \`${PNKLN_PROJECT_ID}.${PNKLN_BQ}.events\` GROUP BY d,vertical,kind"

```

## Export State

```python
import os,json
state={k:v for k,v in os.environ.items() if k.startswith("PNKLN_")}
print(json.dumps(state))

```

## Ready Signal

```bash
set -euo pipefail
echo ready

```
