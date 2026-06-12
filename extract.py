import fitz
import os

pdf = fitz.open("SINAPI_Fichas_Especificacao_Tecnica_Insumos.pdf")

os.makedirs("imagens", exist_ok=True)

for pagina_num in range(len(pdf)):
    pagina = pdf[pagina_num]

    texto = pagina.get_text()

    imagens = pagina.get_images(full=True)

    for i, img in enumerate(imagens):
        xref = img[0]

        imagem = pdf.extract_image(xref)

        with open(
            f"imagens/pagina_{pagina_num+1}_{i}.png",
            "wb"
        ) as f:
            f.write(imagem["image"])

    print(texto[:500])