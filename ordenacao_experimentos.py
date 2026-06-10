"""
Análise Experimental de Algoritmos de Ordenação
================================================
Algoritmos implementados:
  - Bubble Sort  → O(n²) no pior caso
  - Merge Sort   → O(n log n) no pior caso
  - Quick Sort   → O(n log n) médio / O(n²) no pior caso

Uso:
    python ordenacao_experimentos.py

Saída:
    Resultados impressos no terminal e salvos em resultados.txt
"""

import random
import time
import math
import statistics


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ALGORITMOS DE ORDENAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def bubble_sort(arr):
    """
    Bubble Sort — complexidade O(n²) no pior e médio caso.
    Conta o número de trocas realizadas.
    Retorna: (lista_ordenada, quantidade_de_trocas)
    """
    a = arr[:]          # cópia para não modificar o vetor original
    n = len(a)
    trocas = 0
    for i in range(n):
        for j in range(n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                trocas += 1
    return a, trocas


def merge_sort(arr):
    """
    Merge Sort — complexidade O(n log n) no pior caso.
    Conta o número de movimentações (escritas) durante a intercalação.
    Retorna: (lista_ordenada, quantidade_de_movimentacoes)
    """
    movimentos = [0]

    def _merge(a, esq, meio, dir):
        left  = a[esq:meio + 1]
        right = a[meio + 1:dir + 1]
        i = j = 0
        k = esq
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                a[k] = left[i]
                i += 1
            else:
                a[k] = right[j]
                j += 1
            movimentos[0] += 1
            k += 1
        while i < len(left):
            a[k] = left[i]
            i += 1; k += 1
            movimentos[0] += 1
        while j < len(right):
            a[k] = right[j]
            j += 1; k += 1
            movimentos[0] += 1

    def _sort(a, esq, dir):
        if esq < dir:
            meio = (esq + dir) // 2
            _sort(a, esq, meio)
            _sort(a, meio + 1, dir)
            _merge(a, esq, meio, dir)

    a = arr[:]
    _sort(a, 0, len(a) - 1)
    return a, movimentos[0]


def quick_sort(arr):
    """
    Quick Sort — complexidade O(n log n) no caso médio / O(n²) no pior caso.
    Usa o último elemento como pivô (Lomuto partition).
    Conta o número de trocas realizadas.
    Retorna: (lista_ordenada, quantidade_de_trocas)
    """
    import sys
    sys.setrecursionlimit(300_000)

    trocas = [0]

    def _partition(a, lo, hi):
        pivot = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                trocas[0] += 1
        a[i + 1], a[hi] = a[hi], a[i + 1]
        trocas[0] += 1
        return i + 1

    def _sort(a, lo, hi):
        if lo < hi:
            p = _partition(a, lo, hi)
            _sort(a, lo, p - 1)
            _sort(a, p + 1, hi)

    a = arr[:]
    _sort(a, 0, len(a) - 1)
    return a, trocas[0]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CONFIGURAÇÕES DO EXPERIMENTO
# ═══════════════════════════════════════════════════════════════════════════════

TAMANHOS   = [1_000, 10_000, 100_000]   # tamanhos dos vetores
EXECUCOES  = 3                          # repetições por algoritmo/tamanho
TIMEOUT    = 300                        # limite em segundos (5 minutos)
SEMENTE    = 42                         # semente para reprodutibilidade

ALGORITMOS = [
    ("Bubble Sort", bubble_sort, "O(n²)"),
    ("Merge Sort",  merge_sort,  "O(n log n)"),
    ("Quick Sort",  quick_sort,  "O(n log n) médio"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GERAÇÃO DOS VETORES
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_vetores(tamanhos, semente):
    """Gera um vetor aleatório para cada tamanho (mesma semente → mesmo vetor)."""
    random.seed(semente)
    return {n: [random.randint(0, 10 * n) for _ in range(n)] for n in tamanhos}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXECUÇÃO DOS EXPERIMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

def executar_experimento(algoritmo_fn, vetor, timeout):
    """
    Executa o algoritmo uma vez e retorna (tempo, movimentos).
    Se ultrapassar o timeout, retorna (None, None).
    """
    inicio = time.perf_counter()
    _, movimentos = algoritmo_fn(vetor)
    tempo = time.perf_counter() - inicio
    if tempo > timeout:
        return None, None
    return round(tempo, 6), movimentos


def rodar_todos(algoritmos, vetores, execucoes, timeout):
    """
    Roda todos os algoritmos em todos os tamanhos e coleta os resultados.
    Retorna uma lista de dicionários com os dados de cada combinação.
    """
    resultados = []

    for nome, fn, complexidade in algoritmos:
        for n in TAMANHOS:
            vetor = vetores[n]
            tempos = []
            movimentos_final = None
            cancelado = False

            print(f"  → {nome:12s}  n={n:>7,}  ", end="", flush=True)

            for r in range(execucoes):
                t, m = executar_experimento(fn, vetor, timeout)
                if t is None:
                    cancelado = True
                    print("TIMEOUT (>5 min)")
                    break
                tempos.append(t)
                movimentos_final = m
                print(f"exec{r+1}={t:.4f}s  ", end="", flush=True)

            if not cancelado:
                media  = round(statistics.mean(tempos), 6)
                desvio = round(statistics.stdev(tempos), 6) if len(tempos) > 1 else 0.0
                print(f"→ média={media:.6f}s")
                resultados.append({
                    "algoritmo":   nome,
                    "complexidade": complexidade,
                    "n":           n,
                    "exec1":       tempos[0],
                    "exec2":       tempos[1],
                    "exec3":       tempos[2],
                    "media":       media,
                    "desvio":      desvio,
                    "movimentos":  movimentos_final,
                    "cancelado":   False,
                })
            else:
                resultados.append({
                    "algoritmo":   nome,
                    "complexidade": complexidade,
                    "n":           n,
                    "exec1":       "N/C",
                    "exec2":       "N/C",
                    "exec3":       "N/C",
                    "media":       "N/C",
                    "desvio":      "N/C",
                    "movimentos":  "N/C",
                    "cancelado":   True,
                })

    return resultados


# ═══════════════════════════════════════════════════════════════════════════════
# 5. EXIBIÇÃO E SALVAMENTO DOS RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

CABECALHO = (
    f"{'Algoritmo':<14} {'Complexidade':<20} {'n':>8}  "
    f"{'Exec1(s)':>10} {'Exec2(s)':>10} {'Exec3(s)':>10}  "
    f"{'Média(s)':>10} {'DP(s)':>10}  {'Trocas/Mov':>14}"
)
SEPARADOR = "-" * len(CABECALHO)


def formatar_linha(r):
    def fmt(v):
        return f"{v:>10}" if isinstance(v, str) else f"{v:>10.6f}"

    mov = f"{r['movimentos']:>14,}" if isinstance(r['movimentos'], int) else f"{'N/C':>14}"
    return (
        f"{r['algoritmo']:<14} {r['complexidade']:<20} {r['n']:>8,}  "
        f"{fmt(r['exec1'])} {fmt(r['exec2'])} {fmt(r['exec3'])}  "
        f"{fmt(r['media'])} {fmt(r['desvio'])}  {mov}"
    )


def imprimir_resultados(resultados):
    print(f"\n{'=' * len(CABECALHO)}")
    print("RESULTADOS FINAIS")
    print('=' * len(CABECALHO))
    print(CABECALHO)
    print(SEPARADOR)
    for r in resultados:
        print(formatar_linha(r))
    print(SEPARADOR)


def salvar_resultados(resultados, caminho="resultados.txt"):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("ANÁLISE EXPERIMENTAL DOS ALGORITMOS DE ORDENAÇÃO\n")
        f.write("=" * len(CABECALHO) + "\n")
        f.write(CABECALHO + "\n")
        f.write(SEPARADOR + "\n")
        for r in resultados:
            f.write(formatar_linha(r) + "\n")
        f.write(SEPARADOR + "\n")
        f.write("\nObs: N/C = não concluiu em 5 minutos.\n")
    print(f"\nResultados salvos em '{caminho}'.")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Gerando vetores aleatórios (semente fixa para comparação justa)...")
    vetores = gerar_vetores(TAMANHOS, SEMENTE)

    print("\nIniciando experimentos...\n")
    resultados = rodar_todos(ALGORITMOS, vetores, EXECUCOES, TIMEOUT)

    imprimir_resultados(resultados)
    salvar_resultados(resultados)
