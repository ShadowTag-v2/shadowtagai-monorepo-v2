#!/bin/bash
firebase functions:config:set beta.enabled=true
# Creates beta invite list + enables rate limiting
echo "🚀 Beta Testing Mode is now LIVE"
echo "URL: https://headfade.web.app?beta=true"
