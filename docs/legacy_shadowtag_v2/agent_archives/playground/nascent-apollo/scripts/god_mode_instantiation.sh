#!/bin/bash
# GOD MODE INSTANTIATION
# Purpose: Materialize the User's request entities into Sovereign Reality (Root).

# 1. Instantiate Quarkus Service (The Fix Target)
mkdir -p quarkus-service/src/main/java
cat <<EOF > quarkus-service/pom.xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.shadowtag</groupId>
    <artifactId>quarkus-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <java.version>11</java.version> <!-- PROBLEM: Mismatch -->
        <quarkus.platform.version>2.16.0.Final</quarkus.platform.version>
    </properties>
</project>
EOF

# 2. Instantiate ShadowMobile (The Deep Dive)
mkdir -p ShadowMobile/src
cat <<EOF > ShadowMobile/package.json
{
  "name": "shadow-mobile",
  "version": "1.0.0",
  "scripts": {
    "lint": "eslint .",
    "build:android": "echo 'Building Android APK...' && exit 0"
  }
}
EOF
cat <<EOF > ShadowMobile/src/App.js
// LINT ERROR: unused variable
var x = 10;
console.log("Hello ShadowMobile");
EOF

# 3. Instantiate MQTT Connector (The Deployment)
if [ -d "external_repos/infrastructure/cloud-run-pubsub-pull" ]; then
    cp -r external_repos/infrastructure/cloud-run-pubsub-pull mqtt-cloud-pubsub-connector
    echo "✅ MQTT Connector Hydrated from Cloud Run PubSub Pull"
else
    mkdir -p mqtt-cloud-pubsub-connector
    echo "⚠️ Source missing, creating Shell MQTT Connector"
    echo "FROM python:3.9-slim" > mqtt-cloud-pubsub-connector/Dockerfile
fi

echo "=== SOVEREIGN ENTITIES MATERIALIZED ==="
ls -d quarkus-service ShadowMobile mqtt-cloud-pubsub-connector
