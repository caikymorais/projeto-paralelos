# Contagem Paralela de Frequência de Termos

Projeto da disciplina **Sistemas Distribuídos e Paralelos**.

O projeto compara uma implementação sequencial e uma implementação paralela para contar a frequência de palavras em um acervo volumoso de arquivos de texto. A versão paralela utiliza processos, comunicação por fila e sincronização com `Lock`.

## Equipe

- Marcos de Souza
- Caiky Alves

**Turma:** CC6NA  
**Professor:** Fábio Rocha de Araújo

## Objetivo

Processar um acervo de documentos `.txt` e calcular:

- Quantidade de arquivos processados
- Quantidade total de palavras
- Frequência global de cada termo
- Termo mais frequente e sua quantidade de ocorrências

Foram implementadas duas versões do mesmo programa:

- **Sequencial:** processa todos os arquivos em um único fluxo.
- **Paralela:** divide o acervo entre processos independentes e agrega os resultados finais.

## Problema e paralelização

A aplicação representa um cenário de mineração e indexação de textos. Cada documento pode ser lido e analisado sem depender dos demais, portanto a unidade de trabalho é um arquivo de texto.

Foi utilizado **paralelismo de dados**:

```text
Acervo de arquivos
├── Processo 1: processa um bloco de arquivos
└── Processo 2: processa outro bloco de arquivos
```

Cada processo executa as seguintes etapas no seu bloco:

1. Abre o arquivo de texto
2. Normaliza o conteúdo para minúsculas
3. Extrai palavras com expressão regular
4. Cria uma contagem local de termos
5. Envia a contagem local ao processo principal por uma `Queue`

O processo principal agrega as contagens locais e gera a frequência global de termos.

## Estrutura do projeto

```text
projeto-textos-paralelo/
├── dados/
│   └── textos/                 # Arquivos .txt usados como entrada
├── resultados/
│   ├── medicoes.csv            # Medições geradas pelo benchmark
│   └── medicoes_ec2_final.csv  # Medições oficiais na EC2
├── benchmark.py                # Executa medições repetidas e valida resultados
├── comum.py                    # Funções compartilhadas pelas duas versões
├── gerar_textos.py             # Gera o acervo sintético reproduzível
├── paralelo.py                 # Implementação paralela com multiprocessing
├── sequencial.py               # Implementação sequencial
└── README.md                   # Documentação do projeto
```

## Requisitos

- Python 3.9 ou superior
- Nenhuma biblioteca externa é necessária

Verifique a versão instalada:

```bash
python3 --version
```

No Windows:

```powershell
py --version
```

## Como gerar a entrada

O acervo é sintético e reproduzível. A semente fixa garante que a mesma entrada possa ser recriada.

No arquivo `gerar_textos.py`, configure os parâmetros:

```python
QUANTIDADE_ARQUIVOS = 20_000
PALAVRAS_POR_ARQUIVO = 10_000
SEMENTE = 42
```

Gere os textos:

```bash
python3 gerar_textos.py
```

No Windows:

```powershell
py gerar_textos.py
```

A entrada usada na medição oficial possui:

| Item                         |       Valor |
| ---------------------------- | ----------: |
| Arquivos de texto            |      20.000 |
| Palavras por arquivo         |      10.000 |
| Total aproximado de palavras | 200.000.000 |
| Codificação                  |       UTF-8 |
| Semente                      |          42 |

## Como executar

### Versão sequencial

Linux / EC2:

```bash
python3 sequencial.py
```

Windows:

```powershell
py sequencial.py
```

### Versão paralela

Linux / EC2:

```bash
python3 paralelo.py
```

Windows:

```powershell
py paralelo.py
```

A versão paralela cria até dois processos, coerente com a instância AWS `t3.small` utilizada nas medições oficiais, que disponibiliza duas vCPUs.

## Sincronização

Os processos possuem contagens locais para evitar contenção durante a maior parte do processamento. Ao final de cada bloco, todos os trabalhadores atualizam dois estados compartilhados:

```python
contador_arquivos
contador_palavras
```

A atualização é protegida por `multiprocessing.Lock`:

```python
with lock:
    contador_arquivos.value += arquivos_locais
    contador_palavras.value += palavras_locais
```

Essa é a seção crítica do programa. O `Lock` evita condição de corrida, pois garante que apenas um processo atualize os contadores compartilhados por vez.

As frequências de palavras são construídas localmente e enviadas ao processo principal com `Queue`. O processo principal é responsável por agregar as contagens, evitando escrita concorrente em um único dicionário global.

## Validação da correção

A versão sequencial e a versão paralela devem produzir resultados idênticos para a mesma entrada. A validação compara:

- Total de arquivos processados
- Total de palavras processadas
- Dicionário completo de frequência dos termos
- Termo mais frequente e número de ocorrências

Na entrada oficial, o resultado esperado inclui:

```text
Arquivos processados: 20000
Palavras processadas: 200000000
Termo mais frequente: tempo
Ocorrências: 15630972
```

## Benchmark

O arquivo `benchmark.py` realiza:

1. Uma execução de aquecimento, descartada das médias
2. Três repetições da versão sequencial
3. Três repetições da versão paralela com dois processos
4. Validação dos resultados em cada execução
5. Geração de um arquivo CSV em `resultados/medicoes.csv`

Execute:

```bash
python3 benchmark.py
```

No Windows:

```powershell
py benchmark.py
```

## Resultados oficiais

As medições oficiais foram realizadas no AWS Academy Learner Lab, em uma instância Amazon EC2 `t3.small`.

### Ambiente

| Item                    | Configuração            |
| ----------------------- | ----------------------- |
| Provedor                | AWS Academy Learner Lab |
| Serviço                 | Amazon EC2              |
| Região                  | `us-east-1`             |
| Zona de disponibilidade | `us-east-1f`            |
| Sistema operacional     | Amazon Linux 2023       |
| Tipo de instância       | `t3.small`              |
| vCPUs                   | 2                       |
| Memória                 | Aproximadamente 1,9 GiB |
| Armazenamento           | Volume EBS de 30 GiB    |
| Python                  | 3.9.25                  |

### Tempos medidos

| Versão     | Processos |  Execução 1 |  Execução 2 |  Execução 3 |           Média |   Speedup |
| ---------- | --------: | ----------: | ----------: | ----------: | --------------: | --------: |
| Sequencial |         1 | 85,556642 s | 87,662885 s | 86,598585 s | **86,606037 s** |     1,00× |
| Paralela   |         2 | 76,069251 s | 75,839767 s | 80,594783 s | **77,501267 s** | **1,12×** |

O speedup foi calculado por:

\[
S = \frac{T*{sequencial}}{T*{paralelo}}
\]

\[
S = \frac{86,606037}{77,501267} \approx 1,12
\]

A versão paralela reduziu o tempo médio de execução em aproximadamente **10,5%**. A eficiência obtida com dois processos foi aproximadamente **55,9%**.

## Lei de Amdahl

Foi estimado que 90% do trabalho é paralelizável, pois leitura, tokenização e contagem local ocorrem de forma independente em cada bloco. Os 10% restantes representam inicialização dos processos, divisão da entrada, comunicação pela fila, sincronização e agregação final.

Com fração paralelizável \(p = 0,90\) e \(n = 2\) processos:

\[
S(2) = \frac{1}{(1 - 0,90) + \frac{0,90}{2}}
\]

\[
S(2) = \frac{1}{0,10 + 0,45} \approx 1,82
\]

O teto teórico estimado foi **1,82×**, enquanto o speedup medido foi **1,12×**.

A diferença é explicada principalmente por:

- Leitura concorrente de 20.000 arquivos no mesmo volume EBS
- Criação e gerenciamento de processos
- Comunicação das contagens locais por `Queue`
- Atualização dos contadores na seção crítica protegida por `Lock`
- Agregação final realizada pelo processo principal
- Limitação de duas vCPUs e possível variação de desempenho da família `t3`

## Segurança na nuvem

A instância EC2 utilizou grupo de segurança com a regra de entrada:

| Finalidade        | Protocolo | Porta | Origem                                      |
| ----------------- | --------- | ----: | ------------------------------------------- |
| Administração SSH | TCP       |    22 | IP público atual da equipe em formato `/32` |

A porta SSH não foi aberta para `0.0.0.0/0`. Nenhuma porta de serviço adicional foi aberta, pois a aplicação é executada via terminal e não expõe site ou API.

## Licença

Projeto acadêmico desenvolvido para a disciplina Sistemas Distribuídos e Paralelos.
