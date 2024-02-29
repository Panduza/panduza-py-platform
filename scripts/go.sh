# Binairy install on your system
# NATIVE_PYTHON_BIN=python3.11
NATIVE_PYTHON_BIN=python

# ---
PYTHON_VENV_PATH=/opt/panduza/venv
PYTHON_VENV_BIN=$PYTHON_VENV_PATH/bin/python
PYTHON_VENV_PIP=$PYTHON_VENV_PATH/bin/pip3
PYTHON_VENV_PZA_MAIN=$PYTHON_VENV_PATH/lib/python3.11/site-packages/panduza_platform/__main__.py
# If windows system
if [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
    PYTHON_VENV_PATH=~/panduza/venv
    PYTHON_VENV_BIN=$PYTHON_VENV_PATH/Scripts/python
    PYTHON_VENV_PIP=$PYTHON_VENV_PATH/Scripts/pip3
    PYTHON_VENV_PZA_MAIN=$PYTHON_VENV_PATH/Lib/site-packages/panduza_platform/__main__.py
fi

# 
script_dir=$(dirname $0)
script_dir=$(readlink -f $script_dir)
echo "Script directory: $script_dir"

# 
${PYTHON_VENV_PIP} install ${script_dir}/..

# 
${PYTHON_VENV_BIN}  ${PYTHON_VENV_PZA_MAIN}

