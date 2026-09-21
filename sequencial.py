from time import perf_counter

from comum import (
    gerar_resumo,
    listar_arquivos,
    mesclar_contagem,
    processar_arquivo,
)


def executar():
    arquivos = listar_arquivos()

    contagem_global = {}
    total_arquivos = 0
    total_palavras = 0

    inicio = perf_counter()

    for caminho in arquivos:
        resultado = processar_arquivo(caminho)

        total_arquivos += 1
        total_palavras += resultado["quantidade_palavras"]

        mesclar_contagem(
            contagem_global,
            resultado["contagem"],
        )

    fim = perf_counter()

    resumo = gerar_resumo(contagem_global)

    return {
        "tempo": fim - inicio,
        "total_arquivos": total_arquivos,
        "total_palavras": total_palavras,
        "contagem_global": contagem_global,
        "resumo": resumo,
    }


if __name__ == "__main__":
    resultado = executar()

    print("=== VERSÃO SEQUENCIAL ===")
    print(f"Tempo: {resultado['tempo']:.4f} segundos")
    print(f"Arquivos: {resultado['total_arquivos']}")
    print(f"Palavras: {resultado['total_palavras']}")
    print(
        "Palavra mais frequente:",
        resultado["resumo"]["palavra_mais_frequente"],
    )
    print(
        "Quantidade:",
        resultado["resumo"]["quantidade_palavra_mais_frequente"],
    )