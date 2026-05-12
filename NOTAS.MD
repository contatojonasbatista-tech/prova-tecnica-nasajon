# Notas Explicativas

## Estratégia utilizada

O projeto foi desenvolvido em Python utilizando integração com a API do IBGE e envio de resultados para uma função Supabase.

Foi implementado:

- leitura de arquivo CSV;
- tratamento de encoding;
- normalização de texto;
- aproximação de nomes de municípios;
- cálculo de estatísticas;
- geração automática do resultado.csv;
- envio autenticado para API.

## Tratamentos realizados

Para aumentar a taxa de acerto dos municípios foram utilizados:

- unicodedata.normalize
- lower()
- strip()
- difflib.get_close_matches

Isso permitiu tratar:
- acentos;
- diferenças de maiúsculas/minúsculas;
- espaços;
- erros de digitação.

## Bibliotecas utilizadas

- pandas
- requests
- unicodedata
- difflib

## Estrutura do projeto

- main.py → processamento principal
- input.csv → entrada
- resultado.csv → saída gerada
- NOTAS.md → explicações técnicas

## Observações

Foi realizado tratamento de exceções para:
- erros da API;
- municípios não encontrados;
- falhas de autenticação;
- dados inválidos.

As estatísticas foram calculadas utilizando pandas.
