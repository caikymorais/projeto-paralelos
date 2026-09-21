from pathlib import Path
import random


PASTA_SAIDA = Path("dados/textos")
QUANTIDADE_ARQUIVOS = 20_000
PALAVRAS_POR_ARQUIVO = 10_000
SEMENTE = 42


VOCABULARIO = [
    "sistemas",
    "distribuidos",
    "processamento",
    "paralelo",
    "processos",
    "dados",
    "computacao",
    "desempenho",
    "algoritmo",
    "programa",
    "nuvem",
    "servidor",
    "memoria",
    "arquivo",
    "rede",
    "software",
    "hardware",
    "resultado",
    "medicao",
    "tempo",
]


def gerar_arquivo(indice):
    palavras = random.choices(
        VOCABULARIO,
        weights=[
            10,
            8,
            9,
            7,
            6,
            10,
            5,
            8,
            6,
            7,
            4,
            4,
            4,
            8,
            3,
            5,
            3,
            6,
            5,
            10,
        ],
        k=PALAVRAS_POR_ARQUIVO,
    )

    caminho = PASTA_SAIDA / f"texto_{indice:05d}.txt"
    caminho.write_text(" ".join(palavras), encoding="utf-8")


def main():
    random.seed(SEMENTE)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    for indice in range(QUANTIDADE_ARQUIVOS):
        gerar_arquivo(indice)

        if (indice + 1) % 100 == 0:
            print(f"{indice + 1}/{QUANTIDADE_ARQUIVOS} arquivos gerados")

    print("Acervo criado com sucesso.")


if __name__ == "__main__":
    main()