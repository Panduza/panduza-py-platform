PYTHON_BIN=python3.11
PYTHON_VENV_PATH=/opt/panduza/venv

script_dir=$(dirname $0)
script_dir=$(readlink -f $script_dir)
echo "Script directory: $script_dir"

# 
${PYTHON_VENV_PATH}/bin/pip3 install ${script_dir}/..


