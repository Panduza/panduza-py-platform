# Binairy install on your system
# NATIVE_PYTHON_BIN=python3.11
NATIVE_PYTHON_BIN=python

# ---
PYTHON_VENV_PATH=/opt/panduza/venv
PYTHON_VENV_PIP=$PYTHON_VENV_PATH/bin/pip3
# If windows system
if [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
    PYTHON_VENV_PATH=~/panduza/venv
    PYTHON_VENV_PIP=$PYTHON_VENV_PATH/Scripts/pip3
fi


script_dir=$(dirname $0)
script_dir=$(readlink -f $script_dir)
echo "Script directory: $script_dir"


mkdir -p ${PYTHON_VENV_PATH}

# Create venv
${NATIVE_PYTHON_BIN} -m venv ${PYTHON_VENV_PATH}

# 
${PYTHON_VENV_PIP} install -r ${script_dir}/../requirements.txt

# 
${PYTHON_VENV_PIP} install ${script_dir}/..
