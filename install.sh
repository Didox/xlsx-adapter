#!/bin/bash

# Instalação das dependências listadas no arquivo bundle.txt
python3 -m pip install -r bundle.txt

# Verifica se a instalação foi bem-sucedida
if [ $? -eq 0 ]; then
  echo "Instalação concluída com sucesso!"
else
  echo "Houve um problema na instalação das dependências."
fi
