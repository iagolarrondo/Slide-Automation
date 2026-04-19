#!/bin/bash
# Double-click this file in Finder to pick a JSON deck spec and render to PowerPoint.
# First run may prompt for Terminal / automation permissions on some macOS versions.

cd "$(dirname "$0")"
exec ./scripts/mac_pick_and_render.sh "$@"
