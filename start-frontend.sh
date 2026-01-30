#!/bin/bash
export PATH="$HOME/local/node/bin:$PATH"
cd "$(dirname "$0")/web"
npm run dev
