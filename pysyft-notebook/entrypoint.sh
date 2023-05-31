#!/bin/sh

# Use the passed WORKSPACE DIRECTORY
# Otherwise use /workspace
if [ -z "${WORKSPACE_DIR}" ]; then
  WORKSPACE="/workspace"
else
  WORKSPACE="${WORKSPACE_DIR}"
fi

cd $WORKSPACE
#jupyter notebook --ip=`cat /etc/hosts |tail -n 1|cut -f 1` --allow-root
jupyter lab -NotebookApp.token='amdex_rulez' --ip=`cat /etc/hosts --NotebookApp.allow_origin_pat=https://.*vscode-cdn\.net |tail -n 1|cut -f 1` --allow-root
# jupyter lab -NotebookApp.token='amdex_rulez' --ip=`cat /etc/hosts --allow-root --NotebookApp.allow_origin_pat=https://.*vscode-cdn\.net |tail -n 1|cut -f 1` 
# jupyter lab -NotebookApp.token='amdex_rulez' --ip=`cat /etc/hosts --allow-root |tail -n 1|cut -f 1` 
