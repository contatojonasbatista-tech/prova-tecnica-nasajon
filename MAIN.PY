import pandas as pd
import requests
import unicodedata
from difflib import get_close_matches

# ==================================================
# CONFIGURAÇÕES
# ==================================================

SUPABASE_FUNCTION_URL = "https://mynxlubykylncinttggu.functions.supabase.co/ibge-submit"

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6ImR0TG03UVh1SkZPVDJwZEciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL215bnhsdWJ5a3lsbmNpbnR0Z2d1LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmMzIyMjUwYy1hMGUxLTRmNjEtODAyNy03MDgwMzQwNmExNjEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc4NjIzNTYwLCJpYXQiOjE3Nzg2MTk5NjAsImVtYWlsIjoiY29udGF0b2pvbmFzYmF0aXN0YUBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiY29udGF0b2pvbmFzYmF0aXN0YUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibm9tZSI6IkpvbmFzIFNvdXphIiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiJmMzIyMjUwYy1hMGUxLTRmNjEtODAyNy03MDgwMzQwNmExNjEifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc3ODYxOTk2MH1dLCJzZXNzaW9uX2lkIjoiZGMxZWQ4ZWItNTI3Yi00MWZhLThlZWQtYTk5MWYzNzIwOWI1IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.fIRX6eO4SaaD6ozlQyY1pailIj_s2FI1WVaj2suAQvk"

INPUT_FILE = "INPUT.csv"
OUTPUT_FILE = "resultado.csv"

# ==================================================
# NORMALIZAÇÃO
# ==================================================

def normalize(text):

    return (

        unicodedata.normalize("NFKD", str(text))
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .lower()
        .strip()

    )

# ==================================================
# CARREGAR MUNICÍPIOS DO IBGE
# ==================================================

def carregar_municipios_ibge():

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    try:

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        municipios = response.json()

        estrutura = {}

        for municipio in municipios:

            nome = municipio["nome"]

            nome_normalizado = normalize(nome)

            try:

                uf = municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]

                regiao = municipio["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]

            except:

                uf = "N/A"

                regiao = "N/A"

            estrutura[nome_normalizado] = {

                "nome": nome,
                "uf": uf,
                "regiao": regiao,
                "id": municipio["id"]

            }

        return estrutura

    except Exception as e:

        print(f"Erro ao carregar API do IBGE: {e}")

        return None

# ==================================================
# PROCESSAR MUNICÍPIOS
# ==================================================

def processar_municipios():

    municipios_ibge = carregar_municipios_ibge()

    if municipios_ibge is None:

        return None

    try:

        df = pd.read_csv(INPUT_FILE)

    except Exception as e:

        print(f"Erro ao ler CSV: {e}")

        return None

    resultados = []

    for _, row in df.iterrows():

        municipio = str(row["municipio"])

        populacao = row["populacao"]

        municipio_normalizado = normalize(municipio)

        status = "nao_encontrado"

        if municipio_normalizado in municipios_ibge:

            dados = municipios_ibge[municipio_normalizado]

            status = "ok"

        else:

            matches = get_close_matches(

                municipio_normalizado,
                municipios_ibge.keys(),
                n=1,
                cutoff=0.6

            )

            if matches:

                dados = municipios_ibge[matches[0]]

                status = "aproximado"

            else:

                dados = {

                    "nome": None,
                    "uf": None,
                    "regiao": None

                }

        resultados.append({

            "municipio": municipio,
            "municipio_encontrado": dados["nome"],
            "uf": dados["uf"],
            "regiao": dados["regiao"],
            "populacao": populacao,
            "status": status

        })

    resultado_df = pd.DataFrame(resultados)

    resultado_df["populacao"] = pd.to_numeric(

        resultado_df["populacao"],
        errors="coerce"

    )

    resultado_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nArquivo gerado: {OUTPUT_FILE}")

    return resultado_df

# ==================================================
# CALCULAR ESTATÍSTICAS
# ==================================================

def calcular_estatisticas(resultado_df):

    total_municipios = len(resultado_df)

    # SOMENTE OK
    total_ok = len(

        resultado_df[
            resultado_df["status"] == "ok"
        ]

    )

    total_nao_encontrado = len(

        resultado_df[
            resultado_df["status"] == "nao_encontrado"
        ]

    )

    total_erro_api = 0

    pop_total_ok = total_ok

    # MANTÉM APROXIMADOS NAS MÉDIAS
    medias = (

        resultado_df
        .groupby("regiao")["populacao"]
        .mean()
        .round(2)
        .to_dict()

    )

    stats = {

        "total_municipios": int(total_municipios),

        "total_ok": int(total_ok),

        "total_nao_encontrado": int(total_nao_encontrado),

        "total_erro_api": int(total_erro_api),

        "pop_total_ok": int(pop_total_ok),

        "medias_por_regiao": medias

    }

    return stats

# ==================================================
# ENVIAR RESULTADOS
# ==================================================

def enviar_resultados(stats):

    headers = {

        "Authorization": f"Bearer {ACCESS_TOKEN}",

        "Content-Type": "application/json"

    }

    payload = {

        "stats": stats

    }

    try:

        response = requests.post(

            SUPABASE_FUNCTION_URL,

            headers=headers,

            json=payload,

            timeout=30

        )

        print("\n===== RESPOSTA DA API =====")

        print(response.json())

    except Exception as e:

        print(f"Erro ao enviar resultados: {e}")

# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    resultado_df = processar_municipios()

    if resultado_df is not None:

        stats = calcular_estatisticas(resultado_df)

        print("\n===== ESTATÍSTICAS =====")

        print(stats)

        enviar_resultados(stats)