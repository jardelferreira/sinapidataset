import os
import re
import sys

import pymupdf as fitz

PDF_PATH = "../Downloads/SINAPI_Fichas_Especificacao_Tecnica_Insumos.pdf"
OUTPUT_DIR = "imagens"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def localizar_pagina(pdf, codigo_procurado):

    print(f"Procurando código {codigo_procurado}...")

    for pagina_num in range(len(pdf)):

        pagina = pdf[pagina_num]

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
            return pagina_num, pagina

    return None, None


def extrair_imagem(pagina, codigo):

    page_dict = pagina.get_text("dict")

    blocos_imagem = []

    for bloco in page_dict["blocks"]:

        if bloco["type"] != 1:
            continue

        bbox = bloco["bbox"]

        largura = bbox[2] - bbox[0]
        altura = bbox[3] - bbox[1]

        area = largura * altura

        blocos_imagem.append(
            {
                "bbox": bbox,
                "area": area,
            }
        )

    if not blocos_imagem:
        raise Exception(
            "Nenhum bloco de imagem encontrado."
        )

    #
    # A foto principal normalmente é a maior
    #

    maior_bloco = max(
        blocos_imagem,
        key=lambda b: b["area"]
    )

    bbox = maior_bloco["bbox"]

    #
    # margem de segurança
    #

    margem = 3

    clip = fitz.Rect(
        bbox[0] - margem,
        bbox[1] - margem,
        bbox[2] + margem,
        bbox[3] + margem,
    )

    pix = pagina.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        clip=clip,
        alpha=False,
    )

    arquivo_saida = os.path.join(
        OUTPUT_DIR,
        f"{codigo}.png"
    )

    pix.save(arquivo_saida)

    return arquivo_saida


def main():

    if len(sys.argv) != 2:

        print()
        print("Uso:")
        print("python extract_image.py 39719")
        print()

        sys.exit(1)

    codigo = sys.argv[1]

    pdf = fitz.open(PDF_PATH)

    pagina_num, pagina = localizar_pagina(
        pdf,
        codigo,
    )

    if pagina is None:

        print(
            f"Código {codigo} não encontrado."
        )

        sys.exit(1)

    print(
        f"Página encontrada: {pagina_num + 1}"
    )

    arquivo = extrair_imagem(
        pagina,
        codigo,
    )

    print()
    print("Imagem extraída com sucesso")
    print(f"Arquivo: {arquivo}")
    print()


if __name__ == "__main__":
    main()