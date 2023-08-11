#!/bin/sh 

if [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OS X
  echo "Running on Mac OS X"

  if [ -f "/opt/homebrew/bin/brew" ]; then
    echo "Brew exists"
  else   # 安裝 brew 
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew install pipenv
  pipenv --python 3.10 
  pipenv shell 
  pipenv install requests
  pipenv install BeautifulSoup4
  # Execute some command on Mac
else
  # Linux
  sudo apt update && sudo apt install -y pipenv 
  pipenv --python 3.10 
  pipenv shell 
  pipenv install requests
  pipenv install BeautifulSoup4 
fi