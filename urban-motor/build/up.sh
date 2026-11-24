#!/bin/bash
# up.sh FILE 'UPLOAD_URL'  -> PUT a frame to Higgsfield's presigned URL
curl -s -o /dev/null -w "%{http_code}\n" -X PUT -H "Content-Type: image/png" -H "If-None-Match: *" --data-binary @"$1" "$2"
