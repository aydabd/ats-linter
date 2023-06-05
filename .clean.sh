#!/bin/sh
<<'###COMMENTS'
Clean the project:
    Removes:
        build/
        _build/
        dist/
        .tox/
        __pycach__/
        *.pyc files
        .egg dirs and files
        .pytest_cache/
        docs/api/
        lib64/
        output/
###COMMENTS
find . -type d \( -name "_build" -o -name "build" -o -name "dist" -o -name ".tox" -o -name "__pycache__" \
                  -o -name ".pyc*" -o -name "*.egg*" -o -name ".pytest_cache" -o -name "lib" -o -name "include" \
                  -o -name "htmlcov" -o -name "share" -o -name "bin" -o -name "output" -o -name "lib64" \) \
                  -print0 | xargs -0 -I {} /bin/rm -rf "{}"
rm -rf docs/api
