#!/usr/bin/env bash
# Generates documentation for FiftyOne.
#
# Copyright 2017-2023, Voxel51, Inc.
# voxel51.com
#


# Show usage information
usage() {
    echo "Usage:  bash $0 [-h] [-c] [-s]

Options:
-h      Display this help message.
-f      Perform a fast build (don't regenerate zoo/plugin docs).
-c      Perform a clean build (deletes existing build directory).
-s      Copy static files only (CSS, JS).
"
}


# Parse flags
SHOW_HELP=false
FAST_BUILD=false
CLEAN_BUILD=false
STATIC_ONLY=false
while getopts "hfcs" FLAG; do
    case "${FLAG}" in
        h) SHOW_HELP=true ;;
        f) FAST_BUILD=true ;;
        c) CLEAN_BUILD=true ;;
        s) STATIC_ONLY=true ;;
        *) usage; exit 2 ;;
    esac
done
[ ${SHOW_HELP} = true ] && usage && exit 0


set -e

export FIFTYONE_HEADLESS=1

THIS_DIR=$(dirname "$0")

if [[ ${STATIC_ONLY} = true ]]; then
    echo "**** Updating static files ****"
    rsync -av "${THIS_DIR}/source/_static/" "${THIS_DIR}/build/html/_static/"
    exit 0
fi

FIFTYONE_BRAIN_DIR=$(
    python -c "import os, fiftyone.brain as fob; print(os.path.dirname(fob.__file__))" ||
    true
)
# Get the last line from the output. Github workflows produce extraneous output
FIFTYONE_BRAIN_DIR="${FIFTYONE_BRAIN_DIR##*$'\n'}"

if [[ -z "${FIFTYONE_BRAIN_DIR}" ]] || [[ ! -d "${FIFTYONE_BRAIN_DIR}" ]]; then
    echo "fiftyone-brain not installed" >&2
    # workaround for https://github.com/voxel51/fiftyone/issues/583
    echo "Importing fiftyone.brain produced the following output:" >&2
    echo "${FIFTYONE_BRAIN_DIR}" >&2
    exit 1
fi

if [[ ${CLEAN_BUILD} = true ]]; then
    echo "**** Deleting existing build directories ****"
    rm -rf "${THIS_DIR}/source/api"
    rm -rf "${THIS_DIR}/build"
fi


echo "**** Generating documentation ****"

cd "${THIS_DIR}/.."

# Symlink to fiftyone-brain
ln -sf $FIFTYONE_BRAIN_DIR fiftyone/brain

echo "Generating API docs"
# sphinx-apidoc [OPTIONS] -o <OUTPUT_PATH> <MODULE_PATH> [EXCLUDE_PATTERN, ...]
sphinx-apidoc --force --no-toc --separate --follow-links \
    --templatedir=docs/templates/apidoc \
    -o docs/source/api fiftyone \
        fiftyone/brain/internal \
        fiftyone/server \
        fiftyone/service

# Remove symlink
rm fiftyone/brain

cd docs

if [[ ${FAST_BUILD} = false ]]; then
    echo "Generating model zoo listing page"
    python scripts/make_model_zoo_docs.py

    echo "Generating TypeScript API docs"
    cd ../app
    yarn doc
    cd ../docs
fi

echo "Building docs"
# sphinx-build [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]
sphinx-build -M html source build $SPHINXOPTS

echo "**** Documentation complete ****"
printf "To view the docs, open:\n\ndocs/build/html/index.html\n\n"
