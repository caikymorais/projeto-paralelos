from collections import defaultdict
from multiprocessing import Lock, Process, Queue, Value
from time import perf_counter

from comum import (
    gerar_resumo,
    listar_arquivos,
    processar_arquivo,
)


def dividir_em_blocos(lista, quantidade_blocos):
    """
    Divide uma lista em blocos equilibrados.

    Exemplo:
    20 arquivos e 2 processos -> 2 blocos com 10 arquivos.
    """
    if quantidade_blocos <= 0:
        raise ValueError(
            "A quantidade de processos deve ser maior que zero."
        )

    tamanho_base = len(lista) // quantidade_blocos
    resto = len(lista) % quantidade_blocos

    blocos = []
    inicio = 0

    for indice in range(quantidade_blocos):
        tamanho = tamanho_base + (1 if indice < resto else 0)
        fim = inicio + tamanho

        bloco = lista[inicio:fim]

        if bloco:
            blocos.append(bloco)

        inicio = fim

    return blocos


def trabalhador(
    identificador,
    arquivos,
    contador_arquivos,
    contador_palavras,
    fila_resultados,
    lock,
):
    """
    Processa um bloco independente de arquivos.

    Cada trabalhador gera uma contagem local de palavras.
    No fim, atualiza os contadores compartilhados com Lock
    e envia sua contagem local ao processo principal pela Queue.
    """
    arquivos_locais = 0
    palavras_locais = 0
    contagem_local = defaultdict(int)

    # PARTE PARALELA:
    # Cada processo trabalha no seu bloco e usa somente
    # dados locais. Não há necessidade de Lock aqui.
    for caminho in arquivos:
        resultado = processar_arquivo(caminho)

        arquivos_locais += 1
        palavras_locais += resultado["quantidade_palavras"]

        for palavra, quantidade in resultado["contagem"].items():
            contagem_local[palavra] += quantidade

    # SEÇÃO CRÍTICA:
    # Vários processos escrevem nos mesmos Values.
    # O Lock impede uma condição de corrida.
    with lock:
        contador_arquivos.value += arquivos_locais
        contador_palavras.value += palavras_locais

    # Comunicação entre processos:
    # cada trabalhador envia exatamente um dicionário local.
    fila_resultados.put(
        {
            "processo": identificador,
            "arquivos": arquivos_locais,
            "palavras": palavras_locais,
            "contagem": dict(contagem_local),
        }
    )


def executar(quantidade_processos=2):
    """
    Executa a versão paralela.

    Parâmetro:
        quantidade_processos: número de trabalhadores paralelos.

    Retorna:
        Um dicionário com tempo, totais, contagem global e resumo.
    """
    arquivos = listar_arquivos()

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo .txt foi encontrado em dados/textos. "
            "Execute primeiro: python3 gerar_textos.py"
        )

    # Não cria mais processos que arquivos.
    quantidade_processos_real = min(quantidade_processos, len(arquivos))

    blocos = dividir_em_blocos(
        arquivos,
        quantidade_processos_real,
    )

    contador_arquivos = Value("i", 0)
    contador_palavras = Value("q", 0)
    fila_resultados = Queue()
    lock = Lock()
    processos = []

    inicio = perf_counter()

    for identificador, bloco in enumerate(blocos, start=1):
        processo = Process(
            target=trabalhador,
            args=(
                identificador,
                bloco,
                contador_arquivos,
                contador_palavras,
                fila_resultados,
                lock,
            ),
        )

        processos.append(processo)
        processo.start()

    # O processo principal recebe os resultados locais.
    # Fazemos isso antes do join para evitar que a Queue
    # fique cheia e bloqueie um processo trabalhador.
    contagem_global = defaultdict(int)

    for _ in processos:
        resultado_local = fila_resultados.get()

        for palavra, quantidade in resultado_local["contagem"].items():
            contagem_global[palavra] += quantidade

    # Agora todos os processos podem terminar.
    for processo in processos:
        processo.join()

    fim = perf_counter()

    # Se algum trabalhador terminou com erro, interrompe
    # a execução com uma mensagem clara.
    for processo in processos:
        if processo.exitcode != 0:
            raise RuntimeError(
                f"O processo PID={processo.pid} terminou com erro. "
                f"Exit code: {processo.exitcode}"
            )

    contagem_final = dict(contagem_global)
    resumo = gerar_resumo(contagem_final)

    return {
        "tempo": fim - inicio,
        "total_arquivos": contador_arquivos.value,
        "total_palavras": contador_palavras.value,
        "contagem_global": contagem_final,
        "resumo": resumo,
    }


if __name__ == "__main__":
    import os

    # A EC2 t3.small possui 2 vCPUs.
    # min() evita usar mais processos do que CPUs disponíveis.
    quantidade_processos = min(2, os.cpu_count() or 1)

    resultado = executar(
        quantidade_processos=quantidade_processos,
    )

    print("=== VERSÃO PARALELA ===")
    print(f"Processos usados: {quantidade_processos}")
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
    print(
        "Palavras distintas:",
        resultado["resumo"]["quantidade_palavras_distintas"],
    )