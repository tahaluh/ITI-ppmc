#!/usr/bin/env python3
"""
Refaz o experimento 3.3 com foco em taxa de compressao ao longo do corpus.

Saidas:
- output.ppmc
- output_progressivo.txt
- grafico_3_3_taxa_ao_longo.png
- resumo_3_3_taxa.txt
"""

import os
import subprocess
import time


def _executar_cmd(cmd, timeout, log_path):
    inicio = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tempo_total = time.time() - inicio

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("STDOUT\n")
        f.write("=" * 60 + "\n")
        f.write(result.stdout or "")
        f.write("\n\nSTDERR\n")
        f.write("=" * 60 + "\n")
        f.write(result.stderr or "")

    return result, tempo_total


def listar_arquivos_silesia(silesia_dir="silesia"):
    arquivos = sorted(
        [
            os.path.join(silesia_dir, f)
            for f in os.listdir(silesia_dir)
            if os.path.isfile(os.path.join(silesia_dir, f))
        ]
    )
    return arquivos


def executar_3_3(arquivos, kmax=4, janela=1000, pct_reset=15.0, timeout=21600):
    cmd = (
        ["python3", "main.py", "0", str(kmax)]
        + arquivos
        + [
            "--janela",
            str(janela),
            "--pct-reset",
            str(pct_reset),
            "--progressivo",
        ]
    )
    cmd_fallback = ["python3", "main.py", "0", str(kmax)] + arquivos + ["--progressivo"]

    print("\n" + "=" * 80)
    print("REFAZENDO EXPERIMENTO 3.3 (TAXA AO LONGO DO FLUXO)")
    print("=" * 80)
    print(f"Arquivos: {len(arquivos)}")
    print(f"kmax={kmax}, janela={janela}, pct-reset={pct_reset}%")
    print("Executando compressao completa...\n")

    result, tempo_total = _executar_cmd(cmd, timeout, "refazer_3_3_exec.log")

    if result.returncode != 0:
        print(f"Falha na tentativa principal (exit {result.returncode}).")
        print("Log salvo em refazer_3_3_exec.log")
        print("Tentando fallback sem janela/reset para evitar crash...\n")

        result, tempo_total = _executar_cmd(
            cmd_fallback, timeout, "refazer_3_3_exec_fallback.log"
        )
        if result.returncode != 0:
            print(f"Fallback tambem falhou (exit {result.returncode}).")
            print("Log salvo em refazer_3_3_exec_fallback.log")

            if os.path.exists("output_progressivo.txt"):
                print(
                    "Reutilizando output_progressivo.txt existente para gerar o grafico."
                )
                return 0.0, 0, 0

            raise RuntimeError(f"Falha na compressao (exit {result.returncode})")

    linhas = result.stdout.splitlines()
    transicoes = [l for l in linhas if "Transição" in l or "Transicao" in l]
    resets = [l for l in linhas if "Reset" in l]

    print(f"Tempo total: {tempo_total:.1f}s")
    print(f"Transicoes detectadas: {len(transicoes)}")
    print(f"Resets acionados: {len(resets)}")

    return tempo_total, len(transicoes), len(resets)


def carregar_progressivo(path="output_progressivo.txt"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")

    xs = []
    bits_acum = []

    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip()
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            if len(partes) < 2:
                continue
            pos = float(partes[0])
            bits = float(partes[1])
            xs.append(pos)
            bits_acum.append(bits)

    if not xs:
        raise RuntimeError("Sem pontos progressivos no arquivo")

    return xs, bits_acum


def gerar_grafico_taxa(xs, bits_acum, arquivos, saida="grafico_3_3_taxa_ao_longo.png"):
    import matplotlib.pyplot as plt

    bits_por_simbolo = [b / x if x > 0 else 0.0 for x, b in zip(xs, bits_acum)]
    taxa_pct = [(bps / 8.0) * 100.0 for bps in bits_por_simbolo]

    # Limites de arquivos para marcar transicoes no grafico
    limites = []
    nomes = []
    acumulado = 0
    for arq in arquivos:
        tam = os.path.getsize(arq)
        acumulado += tam
        limites.append(acumulado)
        nomes.append(os.path.basename(arq))

    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(xs, bits_por_simbolo, color="#1f77b4", linewidth=1.8, label="Bits/simbolo")
    ax1.set_xlabel("Posicao no fluxo (simbolos)")
    ax1.set_ylabel("Bits/simbolo", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(xs, taxa_pct, color="#d62728", linewidth=1.2, alpha=0.85, label="Taxa (%)")
    ax2.set_ylabel("Taxa de compressao (%)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    for i, lim in enumerate(limites[:-1]):
        ax1.axvline(lim, color="gray", linestyle="--", linewidth=0.7, alpha=0.4)
        if i % 2 == 0:
            ax1.text(
                lim,
                ax1.get_ylim()[1] * 0.98,
                nomes[i],
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
                color="gray",
            )

    final_bps = bits_por_simbolo[-1]
    final_taxa = taxa_pct[-1]

    plt.title(
        "Experimento 3.3 - Taxa de compressao ao longo do corpus Silesia\n"
        f"Final: {final_bps:.4f} bits/simbolo ({final_taxa:.2f}%)"
    )

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.tight_layout()
    plt.savefig(saida, dpi=160)
    print(f"Grafico salvo em: {saida}")

    return final_bps, final_taxa


def salvar_resumo(
    tempo_total,
    transicoes,
    resets,
    final_bps,
    final_taxa,
    out_path="resumo_3_3_taxa.txt",
):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Experimento 3.3 - Resumo\n")
        f.write("=" * 40 + "\n")
        f.write(f"Tempo total (s): {tempo_total:.1f}\n")
        f.write(f"Transicoes detectadas: {transicoes}\n")
        f.write(f"Resets acionados: {resets}\n")
        f.write(f"Bits/simbolo final: {final_bps:.6f}\n")
        f.write(f"Taxa final (%): {final_taxa:.4f}\n")
    print(f"Resumo salvo em: {out_path}")


def main():
    silesia_dir = "silesia"
    if not os.path.isdir(silesia_dir):
        raise FileNotFoundError("Pasta silesia nao encontrada")

    arquivos = listar_arquivos_silesia(silesia_dir)
    if not arquivos:
        raise RuntimeError("Nenhum arquivo na pasta silesia")

    tempo_total, transicoes, resets = executar_3_3(
        arquivos, kmax=4, janela=1000, pct_reset=15.0
    )

    xs, bits_acum = carregar_progressivo("output_progressivo.txt")
    print(f"Pontos progressivos carregados: {len(xs)}")

    final_bps, final_taxa = gerar_grafico_taxa(xs, bits_acum, arquivos)

    salvar_resumo(tempo_total, transicoes, resets, final_bps, final_taxa)

    print("\nConcluido.")


if __name__ == "__main__":
    main()
