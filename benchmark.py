import csv
from pathlib import Path
from statistics import mean

from paralelo import executar as executar_paralelo
from sequencial import executar as executar_sequencial


PASTA_RESULTADOS = Path("resultados")
ARQUIVO_MEDICOES = PASTA_RESULTADOS / "medicoes.csv"
REPETICOES = 3
CONFIGURACOES = [1, 2]


def validar_resultados(resultado_sequencial, resultado_paralelo):
    campos = [
        "total_arquivos",
        "total_palavras",
        "contagem_global",
    ]

    for campo in campos:
        if resultado_sequencial[campo] != resultado_paralelo[campo]:
            print(f"ERRO: diferença encontrada em '{campo}'.")
            return False

    return True


def medir_sequencial():
    tempos = []
    referencia = None

    for repeticao in range(1, REPETICOES + 1):
        print(f"Sequencial — repetição {repeticao}/{REPETICOES}...")
        resultado = executar_sequencial()

        tempos.append(resultado["tempo"])

        if referencia is None:
            referencia = resultado
        elif not validar_resultados(referencia, resultado):
            raise RuntimeError(
                "A versão sequencial produziu resultados diferentes "
                "entre repetições."
            )

    return referencia, tempos


def medir_paralelo(referencia, quantidade_processos):
    tempos = []

    for repeticao in range(1, REPETICOES + 1):
        print(
            f"Paralelo com {quantidade_processos} processos "
            f"— repetição {repeticao}/{REPETICOES}..."
        )

        resultado = executar_paralelo(
            quantidade_processos=quantidade_processos
        )

        if not validar_resultados(referencia, resultado):
            raise RuntimeError(
                f"Falha na validação com {quantidade_processos} processos."
            )

        tempos.append(resultado["tempo"])

    return tempos


def salvar_csv(linhas):
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    with open(ARQUIVO_MEDICOES, "w", newline="", encoding="utf-8") as arquivo:
        campos = [
            "versao",
            "processos",
            "repeticao",
            "tempo_segundos",
            "speedup",
        ]

        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def main():
    print("=" * 60)
    print("INÍCIO DAS MEDIÇÕES")
    print("=" * 60)

    print("Aquecimento: executando uma vez sem registrar o tempo...")
    executar_sequencial()
    executar_paralelo(quantidade_processos=4)
    print("Aquecimento concluído.\n")

    referencia, tempos_sequenciais = medir_sequencial()
    media_sequencial = mean(tempos_sequenciais)

    print("\nTempos sequenciais:", tempos_sequenciais)
    print(f"Média sequencial: {media_sequencial:.4f} s")

    linhas_csv = []

    for indice, tempo in enumerate(tempos_sequenciais, start=1):
        linhas_csv.append(
            {
                "versao": "sequencial",
                "processos": 1,
                "repeticao": indice,
                "tempo_segundos": f"{tempo:.6f}",
                "speedup": "1.000000",
            }
        )

    for quantidade_processos in CONFIGURACOES[1:]:
        print("\n" + "=" * 60)
        print(f"MEDIÇÃO COM {quantidade_processos} PROCESSOS")
        print("=" * 60)

        tempos_paralelos = medir_paralelo(
            referencia,
            quantidade_processos,
        )

        media_paralela = mean(tempos_paralelos)
        speedup = media_sequencial / media_paralela

        print(f"Tempos: {tempos_paralelos}")
        print(f"Média paralela: {media_paralela:.4f} s")
        print(f"Speedup: {speedup:.2f}x")

        for indice, tempo in enumerate(tempos_paralelos, start=1):
            linhas_csv.append(
                {
                    "versao": "paralela",
                    "processos": quantidade_processos,
                    "repeticao": indice,
                    "tempo_segundos": f"{tempo:.6f}",
                    "speedup": f"{speedup:.6f}",
                }
            )

    salvar_csv(linhas_csv)

    print("\n" + "=" * 60)
    print("MEDIÇÕES CONCLUÍDAS")
    print("=" * 60)
    print(f"Arquivo criado: {ARQUIVO_MEDICOES}")
    print(f"Arquivos processados: {referencia['total_arquivos']}")
    print(f"Palavras processadas: {referencia['total_palavras']}")
    print(
        "Palavra mais frequente:",
        referencia["resumo"]["palavra_mais_frequente"],
    )
    print(
        "Quantidade:",
        referencia["resumo"]["quantidade_palavra_mais_frequente"],
    )


if __name__ == "__main__":
    main()