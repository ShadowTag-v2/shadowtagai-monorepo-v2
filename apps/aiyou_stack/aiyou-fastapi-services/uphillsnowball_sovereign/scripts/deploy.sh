#!/bin/bash
gcloud builds submit --config infrastructure/cloudbuild.yaml .
