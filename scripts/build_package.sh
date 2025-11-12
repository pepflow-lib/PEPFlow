#!/bin/bash

set -Eeuo pipefail

uv version --bump patch
uv build