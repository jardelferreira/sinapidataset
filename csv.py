import fitz
import re
import pandas as pd

pdf = fitz.open("SINAPI_Fichas_Especificacao_Tecnica_Insumos.pdf")

dados = []

for page in pdf:

    texto = page.get_text()

    codigo = re.search(
        r"Código do SINAPI:\s*(\d+)",
        texto
    )

    descricao = re.search(
        r"Descrição Básica:\s*(.*?)\n",
        texto
    )

    unidade = re.search(
        r"Unidade:\s*(.*?)\n",
        texto
    )

    atualizado = re.search(
        r"Atualizado em:\s*(\d{2}/\d{2}/\d{4})",
        texto
    )

    dados.append({
        "codigo": codigo.group(1) if codigo else None,
        "descricao": descricao.group(1) if descricao else None,
        "unidade": unidade.group(1) if unidade else None,
        "atualizado_em": atualizado.group(1) if atualizado else None
    })

df = pd.DataFrame(dados)

df.to_excel('output/insumos.xlsx', index=False)