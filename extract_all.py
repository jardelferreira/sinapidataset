import json
import re
import time

import pymupdf as fitz

PDF_PATH = "../Downloads/SINAPI_Fichas_Especificacao_Tecnica_Insumos.pdf"
OUTPUT_FILE = "sinapi_insumos.json"


def limpar(texto):

    if not texto:
        return None

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def extrair(pattern, texto, flags=re.DOTALL):

    match = re.search(
        pattern,
        texto,
        flags,
    )

    if not match:
        return None

    return limpar(match.group(1))


def processar_pagina(pagina_num, pagina):

    texto = pagina.get_text("text")

    codigo = extrair(
        r"Código do SINAPI:\s*(\d+)",
        texto,
        re.IGNORECASE,
    )

    if not codigo:
        return None

    descricao = extrair(
        r"Descrição Básica:\s*(.*?)\nUnidade:",
        texto,
    )

    unidade = extrair(
        r"Unidade:\s*(.*?)\n",
        texto,
    )

    normas = extrair(
        r"Normas Técnicas:\s*(.*?)Imagem:",
        texto,
    )

    informacoes = extrair(
        r"Informações Gerais:\s*(.*?)Atualizado em:",
        texto,
    )

    atualizado_em = extrair(
        r"Atualizado em:\s*(\d{2}/\d{2}/\d{4})",
        texto,
    )

    return {
        "codigo": codigo,
        "descricao": descricao,
        "unidade": unidade,
        "normas": normas,
        "informacoes": informacoes,
        "atualizado_em": atualizado_em,
        "pagina": pagina_num + 1,
    }


def main():

    inicio = time.time()

    print("Abrindo PDF...")

    pdf = fitz.open(PDF_PATH)

    total_paginas = len(pdf)

    print(f"Total de páginas: {total_paginas}")

    insumos = []

    for pagina_num in range(total_paginas):

        pagina = pdf[pagina_num]

        item = processar_pagina(
            pagina_num,
            pagina,
        )

        if item:
            insumos.append(item)

        if pagina_num % 100 == 0:

            print(
                f"Processadas "
                f"{pagina_num}/{total_paginas}"
            )

    print()

    print(
        f"Total de insumos encontrados: "
        f"{len(insumos)}"
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            insumos,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    fim = time.time()

    print()
    print(f"JSON gerado: {OUTPUT_FILE}")
    print(
        f"Tempo total: "
        f"{round(fim - inicio, 2)}s"
    )


if __name__ == "__main__":
    main()