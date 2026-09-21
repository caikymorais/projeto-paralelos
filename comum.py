from pathlib import Path
import re


PASTA_TEXTOS = Path("dados/textos")


def listar_arquivos():
    """
    Retorna uma lista ordenada de todos os arquivos .txt
    presentes na pasta dados/textos.
    """
    return sorted(PASTA_TEXTOS.glob("*.txt"))


def extrair_palavras(texto):
    """
    Converte o texto para minúsculas e extrai palavras.
    A expressão regular também aceita letras acentuadas.
    """
    return re.findall(r"[a-záàâãéêíóôõúç]+", texto.lower())


def processar_arquivo(caminho):
    """
    Lê um arquivo .txt, extrai suas palavras e retorna
    a contagem local daquele arquivo.
    """
    texto = caminho.read_text(encoding="utf-8")
    palavras = extrair_palavras(texto)

    contagem = {}

    for palavra in palavras:
        contagem[palavra] = contagem.get(palavra, 0) + 1

    return {
        "arquivo": caminho.name,
        "quantidade_palavras": len(palavras),
        "contagem": contagem,
    }


def mesclar_contagem(destino, origem):
    """
    Soma as contagens do dicionário 'origem' dentro
    do dicionário 'destino'.
    """
    for palavra, quantidade in origem.items():
        destino[palavra] = destino.get(palavra, 0) + quantidade


def gerar_resumo(contagem):
    """
    Gera estatísticas finais da contagem de palavras.

    Também evita o erro:
    ValueError: max() iterable argument is empty

    Se a contagem estiver vazia, devolve um resumo seguro
    e mostra avisos para ajudar no diagnóstico.
    """
    if not contagem:
        print("\n" + "=" * 60)
        print("AVISO: A CONTAGEM DE PALAVRAS ESTÁ VAZIA.")
        print("=" * 60)
        print("Possíveis causas:")
        print("1. Não existem arquivos .txt em dados/textos.")
        print("2. O gerador de textos ainda não foi executado.")
        print("3. Os processos paralelos não gravaram resultados.")
        print("4. O caminho da pasta dados/textos está incorreto.")
        print("=" * 60 + "\n")

        return {
            "palavra_mais_frequente": "nenhuma",
            "quantidade_palavra_mais_frequente": 0,
            "quantidade_palavras_distintas": 0,
        }

    palavra_mais_frequente, quantidade = max(
        contagem.items(),
        key=lambda item: item[1],
    )

    return {
        "palavra_mais_frequente": palavra_mais_frequente,
        "quantidade_palavra_mais_frequente": quantidade,
        "quantidade_palavras_distintas": len(contagem),
    }