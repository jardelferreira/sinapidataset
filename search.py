import json
import os
import re
import sys

import pymupdf as fitz

PDF_PATH = "../Downloads/SINAPI_Fichas_Especificacao_Tecnica_Insumos.pdf"

JSON_DIR = "json"
IMAGE_DIR = "imagens"

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


def limpar_texto(texto):
    if not texto:
        return None

    return re.sub(r"\s+", " ", texto).strip()


def extrair_campo(pattern, texto, flags=re.DOTALL):
    match = re.search(pattern, texto, flags)

    if not match:
        return None

    return limpar_texto(match.group(1))


def localizar_pagina(pdf, codigo_procurado):

    for numero_pagina in range(len(pdf)):

        pagina = pdf[numero_pagina]

        texto = pagina.get_text("text")

        match = re.search(
            r"Código do SINAPI:\s*(\d+)",
            texto,
            re.IGNORECASE,
        )

        if not match:
            continue

        codigo = match.group(1)

        if codigo == codigo_procurado:
            return numero_pagina, pagina, texto

    return None, None, None


def extrair_imagem(pagina, codigo):

    page_dict = pagina.get_text("dict")

    blocos_imagem = [
        bloco
        for bloco in page_dict["blocks"]
        if bloco["type"] == 1
    ]

    if not blocos_imagem:
        return None

    #
    # Normalmente a foto do produto é a maior área
    #

    bloco_imagem = max(
        blocos_imagem,
        key=lambda b: (
            (b["bbox"][2] - b["bbox"][0])
            * (b["bbox"][3] - b["bbox"][1])
        ),
    )

    bbox = bloco_imagem["bbox"]

    clip = fitz.Rect(*bbox)

    imagem_path = os.path.join(
        IMAGE_DIR,
        f"{codigo}.png"
    )

    pix = pagina.get_pixmap(
        matrix=fitz.Matrix(4, 4),
        clip=clip,
        alpha=False,
    )

    pix.save(imagem_path)

    return imagem_path


def extrair_dados(texto):

    return {
        "descricao": extrair_campo(
            r"Descrição Básica:\s*(.*?)\nUnidade:",
            texto,
        ),
        "unidade": extrair_campo(
            r"Unidade:\s*(.*?)\n",
            texto,
        ),
        "normas": extrair_campo(
            r"Normas Técnicas:\s*(.*?)Imagem:",
            texto,
        ),
        "informacoes": extrair_campo(
            r"Informações Gerais:\s*(.*?)Atualizado em:",
            texto,
        ),
        "atualizado_em": extrair_campo(
            r"Atualizado em:\s*(\d{2}/\d{2}/\d{4})",
            texto,
            re.IGNORECASE,
        ),
    }


def salvar_json(codigo, dados):

    json_path = os.path.join(
        JSON_DIR,
        f"{codigo}.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4,
        )

    return json_path


def main():

    if len(sys.argv) < 2:

        print(
            "Uso: python search.py <codigo>"
        )

        sys.exit(1)

    codigo = str(sys.argv[1])

    pdf = fitz.open(PDF_PATH)

    pagina_num, pagina, texto = localizar_pagina(
        pdf,
        codigo,
    )

    if pagina is None:

        print(
            f"Código {codigo} não encontrado."
        )

        sys.exit(0)

    dados = extrair_dados(texto)

    imagem_path = extrair_imagem(
        pagina,
        codigo,
    )

    resultado = {
        "codigo": codigo,
        "pagina": pagina_num + 1,
        **dados,
        "imagem": imagem_path,
    }

    json_path = salvar_json(
        codigo,
        resultado,
    )

    print()
    print("=" * 50)
    print("INSUMO ENCONTRADO")
    print("=" * 50)
    print(f"Código : {codigo}")
    print(f"Página : {pagina_num + 1}")
    print(f"JSON   : {json_path}")
    print(f"Imagem : {imagem_path}")
    print()


if __name__ == "__main__":
    main()