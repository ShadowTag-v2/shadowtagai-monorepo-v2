# Gemini Ingestion Layer - GKE CronJob Specification

**Version**: 1.0-draft
**Status**: Pre-Production Design
**Date**: 2025-11-15

---

## CronJob Definition

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ingestion-nightly
  namespace: ingestion
  labels:
    app: gemini-ingestion
    component: batch-crawler
    tier: foundational
spec:
  # Run nightly at 3:00 AM UTC
  schedule: "0 3 * * *"
  timeZone: "UTC"
  concurrencyPolicy: Forbid  # Don't allow overlapping runs
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3

  jobTemplate:
    spec:
      # 45-minute timeout for entire job
      activeDeadlineSeconds: 2700  # 45 minutes
      backoffLimit: 1  # Only retry once on failure

      template:
        metadata:
          labels:
            app: gemini-ingestion
            batch: nightly
        spec:
          restartPolicy: Never
          serviceAccountName: ingestion-sa

          # Init container: Pre-flight checks
          initContainers:
          - name: preflight
            image: gcr.io/pnkln-prod/ingestion-preflight:v1.0
            command: ["/bin/sh", "-c"]
            args:
              - |
                echo "Checking source availability..."
                # Validate all 8 sources are reachable
                python /app/check_sources.py
                echo "Validating robots.txt compliance..."
                python /app/validate_robots.py
                echo "Preflight checks complete"
            resources:
              requests:
                cpu: 100m
                memory: 128Mi
              limits:
                cpu: 200m
                memory: 256Mi

          # Main containers: Parallel execution
          containers:
          # Container 1: Source Crawler (YouTube)
          - name: crawler-youtube
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "youtube"
            - name: API_KEY
              valueFrom:
                secretKeyRef:
                  name: youtube-api-key
                  key: key
            - name: RATE_LIMIT
              value: "10"  # 10 requests/sec
            - name: MAX_ITEMS
              value: "300"
            command: ["/app/crawler.py"]
            args: ["--source", "youtube", "--output", "/data/youtube.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 500m
                memory: 512Mi
              limits:
                cpu: 1000m
                memory: 1Gi

          # Container 2: Source Crawler (Twitter)
          - name: crawler-twitter
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "twitter"
            - name: BEARER_TOKEN
              valueFrom:
                secretKeyRef:
                  name: twitter-api-token
                  key: bearer
            - name: RATE_LIMIT
              value: "1"  # 1 request/sec (Twitter strict)
            - name: MAX_ITEMS
              value: "250"
            command: ["/app/crawler.py"]
            args: ["--source", "twitter", "--output", "/data/twitter.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Container 3: Source Crawler (News RSS)
          - name: crawler-news
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "news"
            - name: RATE_LIMIT
              value: "20"  # 20 requests/sec for RSS
            - name: MAX_ITEMS
              value: "400"
            command: ["/app/crawler.py"]
            args: ["--source", "news", "--output", "/data/news.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 512Mi

          # Container 4: Source Crawler (Reddit)
          - name: crawler-reddit
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "reddit"
            - name: CLIENT_ID
              valueFrom:
                secretKeyRef:
                  name: reddit-api-creds
                  key: client_id
            - name: CLIENT_SECRET
              valueFrom:
                secretKeyRef:
                  name: reddit-api-creds
                  key: client_secret
            - name: RATE_LIMIT
              value: "5"  # 5 requests/sec
            - name: MAX_ITEMS
              value: "200"
            command: ["/app/crawler.py"]
            args: ["--source", "reddit", "--output", "/data/reddit.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Container 5: Classifier (runs after crawlers complete)
          - name: classifier
            image: gcr.io/pnkln-prod/ingestion-classifier:v1.0
            env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-api-key
                  key: key
            - name: BATCH_SIZE
              value: "10"  # Batch 10 items per API call
            - name: TIER1_THRESHOLD
              value: "0.7"  # Confidence score for Tier 1
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for crawlers to finish
                while [ ! -f /data/.crawl_complete ]; do sleep 10; done
                echo "Starting classification..."
                python /app/classify.py --input /data/*.jsonl --output /data/classified.jsonl
                echo "Classification complete"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 500m
                memory: 1Gi
              limits:
                cpu: 1000m
                memory: 2Gi

          # Container 6: Compliance Validator
          - name: validator
            image: gcr.io/pnkln-prod/ingestion-validator:v1.0
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for classification
                while [ ! -f /data/classified.jsonl ]; do sleep 10; done
                echo "Validating ethical compliance..."
                python /app/validate.py --input /data/classified.jsonl --output /data/validated.jsonl
                echo "Validation complete"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 200m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 512Mi

          # Container 7: Briefing Generator
          - name: briefing
            image: gcr.io/pnkln-prod/ingestion-briefing:v1.0
            env:
            - name: DELIVERY_TIME
              value: "06:00"  # 6:00 AM target
            - name: RECIPIENT_EMAILS
              value: "team@pnkln.ai"
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for validation
                while [ ! -f /data/validated.jsonl ]; do sleep 10; done
                echo "Generating AM briefing..."
                python /app/generate_briefing.py --input /data/validated.jsonl --output /data/briefing.html
                python /app/send_email.py --briefing /data/briefing.html
                echo "Briefing delivered"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Shared volume for inter-container communication
          volumes:
          - name: data-volume
            emptyDir:
              sizeLimit: 5Gi

---

## Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ingestion-quota
  namespace: ingestion
spec:
  hard:
    requests.cpu: "5"
    requests.memory: "8Gi"
    limits.cpu: "10"
    limits.memory: "16Gi"
    pods: "20"
```

---

## Node Pool Configuration (Preemptible)

```yaml
# Terraform configuration for GKE node pool
resource "google_container_node_pool" "ingestion_pool" {
  name       = "ingestion-preemptible"
  cluster    = google_container_cluster.primary.name
  node_count = 2  # Auto-scale 2-5 nodes

  autoscaling {
    min_node_count = 2
    max_node_count = 5
  }

  node_config {
    preemptible  = true  # Cost savings
    machine_type = "e2-standard-4"  # 4 vCPU, 16GB RAM

    labels = {
      workload = "ingestion"
    }

    taint {
      key    = "workload"
      value  = "ingestion"
      effect = "NO_SCHEDULE"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
```

---

## Performance Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Total Runtime** | ≤45 minutes | Untested (pre-prod) |
| **Crawler Phase** | ≤20 minutes | Estimated |
| **Classification Phase** | ≤15 minutes | Estimated (1000 items @ 10/batch) |
| **Validation Phase** | ≤5 minutes | Estimated |
| **Briefing Phase** | ≤5 minutes | Estimated |

---

## Failure Scenarios & Recovery

### Scenario 1: Single Crawler Failure

- **Detection**: Container exit code ≠ 0
- **Impact**: Partial data (e.g., YouTube down, but Twitter/News/Reddit succeed)
- **Recovery**: Job continues with available data, alerts Slack channel

### Scenario 2: Classification API Timeout

- **Detection**: Gemini API returns 504
- **Impact**: Items remain unclassified
- **Recovery**: Retry with exponential backoff (2s, 4s, 8s), fallback to rule-based classifier

### Scenario 3: Briefing Delivery Failure

- **Detection**: Email send fails
- **Impact**: Team doesn't receive AM briefing
- **Recovery**: Store briefing in Cloud Storage, send Slack notification with link

### Scenario 4: Job Exceeds 45-Minute Deadline

- **Detection**: `activeDeadlineSeconds` triggers
- **Impact**: Incomplete data ingestion
- **Recovery**: Job terminates, alerts on-call engineer, reschedule for next night

---

## Open Questions (for Analysis)

1. **Resource Sizing**: Are 4 vCPU/16GB RAM nodes sufficient for 2000 items/night?
2. **Preemptible Risk**: What's acceptable failure rate for cost savings?
3. **Container Dependencies**: Should we use Kubernetes Jobs instead of sidecar containers?
4. **Data Persistence**: Should intermediate data (crawl results) be stored in Cloud Storage?
5. **Monitoring**: What metrics should trigger alerts (runtime >40 min? cost >$3/night?)?

---

**Status**: Draft specification for analysis review
**Next Steps**: Run Gemini 2.0 Pro analysis, address findings before implementation
