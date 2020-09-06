#!/bin/bash

ffmpeg -i /opt/robotframework/artifact_store/old_clip.mp4  -i /opt/robotframework/artifact_store/new_clip.mp4   -lavfi  "ssim" -f null -



