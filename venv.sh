# USAGE on the project folder
# source run.sh

# If PYTHON_EXE is set, use that. Otherwise, look for python3 and settle for
# python.
if [ -z "$PYTHON_EXE" ]; then
 if command -v python3 > /dev/null 2>&1; then
   export PYTHON_EXE=python3
 else
   export PYTHON_EXE=python
 fi
fi

if [ -d "venv" ]; then
  echo "venv already exists"
else
  echo "creating venv"

  if $PYTHON_EXE --version 2>&1 | grep -q "Python 2"; then
    $PYTHON_EXE -m virtualenv venv
  else
    $PYTHON_EXE -m venv venv
  fi
fi

. venv/bin/activate

# Update pip if necessary. Version 8.1.1 that ships with Ubuntu 16.04 fails to
# download some packages due to SSL difficulties.
pip install -U pip

pip_cmd="pip install -r requirements.txt"
if [ -e extra-requirements.txt ]; then
  pip_cmd="$pip_cmd -r extra-requirements.txt"
fi
if [ -e constraints.txt ]; then
  pip_cmd="$pip_cmd -c constraints.txt"
fi

echo $pip_cmd
eval $pip_cmd
