# prova-tecnica-nasajon
Prova técnica Nasajon - Integração IBGE e Supabase
# Prova Técnica Nasajon

## Tecnologias utilizadas
- Python
- Pandas
- Requests
- API IBGE
- Supabase

## Funcionalidades
- Leitura do input.csv
- Enriquecimento de municípios usando API do IBGE
- Tratamento de nomes aproximados
- Geração do resultado.csv
- Cálculo de estatísticas
- Envio automático para API de correção

## Como executar

Instale as dependências:

pip install pandas requests

Execute:

python main.py

## Observações técnicas
- Foi utilizado normalize para tratamento de acentos.
- Foi utilizado get_close_matches para aproximação de municípios digitados incorretamente.
- Foram tratados erros de API e municípios não encontrados.
