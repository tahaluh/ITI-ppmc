#!/usr/bin/env python3
"""
Análise Final - APENAS SILESIA
3.1: kmax 0-10 (somente compressão, modo rápido)
3.2 + 3.3: uma única compressão completa com progressivo + transições
"""

import csv
import os
import subprocess
import time


def executar_teste(modo, kmax, arquivos, desc="", extra_args=None, timeout=7200):
    """Executa compression (0) ou decompression (1)."""
    tempo_inicio = time.time()
    cmd = ["python3", "main.py", str(modo), str(kmax)] + arquivos
    if extra_args:
        cmd += extra_args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        tempo = time.time() - tempo_inicio

        if result.returncode == 0:
            return tempo, None
        else:
            return None, f"Erro (exit {result.returncode}): {result.stderr[:150]}"
    except subprocess.TimeoutExpired:
        return None, "Timeout (>2h)"
    except Exception as e:
        return None, str(e)


def analise_3_1_silesia():
    """3.1: kmax 0-10 com compressão apenas (rápido)."""
    print("\n" + "=" * 80)
    print("3.1 ANÁLISE DE ORDEM E PERFORMANCE - SILESIA (kmax 0-10)")
    print("=" * 80)

    arquivo_base = "silesia/dickens"
    if not os.path.exists(arquivo_base):
        print(f"Erro: Arquivo {arquivo_base} não encontrado")
        return

    arquivos = [arquivo_base]
    total_original = os.path.getsize(arquivo_base)
    print(f"Arquivo base (do corpus Silesia): {arquivo_base}")
    print(f"Tamanho: {total_original:,} bytes ({total_original / (1024**2):.1f} MB)\n")

    csv_path = "analise_3_1_silesia_completo.csv"

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "kmax",
                "Bits/Símbolo",
                "Taxa (%)",
                "Tempo Comp (s)",
                "Tempo Decomp (s)",
                "Tempo Total (s)",
                "Tamanho Comprimido (bytes)",
                "Obs",
            ]
        )

        for kmax in range(0, 11):
            print(f"kmax={kmax:2d}... ", end="", flush=True)

            # COMPRESSÃO
            tempo_comp, erro_comp = executar_teste(0, kmax, arquivos, "comp")

            if erro_comp:
                print(f"✗ Comp: {erro_comp}")
                writer.writerow(
                    [kmax, "ERRO", "ERRO", "ERRO", "ERRO", "ERRO", "ERRO", erro_comp]
                )
                csvfile.flush()
                continue

            # Ler tamanho comprimido
            if os.path.exists("output.ppmc"):
                tamanho_comp = os.path.getsize("output.ppmc")
                bits_sym = (tamanho_comp * 8) / total_original
                taxa = (tamanho_comp / total_original) * 100
            else:
                print(f"✗ Arquivo não gerado")
                continue

            # Modo rápido: sem descompressão por kmax para caber no tempo total
            tempo_decomp = "N/A"
            tempo_total = tempo_comp
            print(f"✓ {bits_sym:.4f} bits/sym | {taxa:.1f}% | Comp:{tempo_comp:.0f}s")

            writer.writerow(
                [
                    kmax,
                    f"{bits_sym:.6f}",
                    f"{taxa:.2f}",
                    f"{tempo_comp:.2f}",
                    tempo_decomp,
                    f"{tempo_total:.2f}",
                    tamanho_comp,
                    "Descompressão por kmax omitida para otimizar tempo",
                ]
            )
            csvfile.flush()

    print(f"\n✅ Resultados salvos: {csv_path}")


def analise_3_2_silesia_todo():
    """3.2: Aprendizado progressivo em TODO SILESIA (usa output_progressivo.txt)."""
    print("\n" + "=" * 80)
    print("3.2 ANÁLISE DE APRENDIZADO - TODO SILESIA")
    print("=" * 80)

    if not os.path.exists("output_progressivo.txt"):
        print("Arquivo output_progressivo.txt ainda não existe.")
        print(
            "Ele será gerado na execução do experimento 3.3 (compressão completa com --progressivo)."
        )
        return

    try_generate_plot_3_2()


def try_generate_plot_3_2():
    """Tenta gerar gráfico de aprendizado TODO Silesia."""
    try:
        import matplotlib.pyplot as plt

        if not os.path.exists("output_progressivo.txt"):
            print("⚠️  Arquivo progressivo não gerado")
            return

        dados = []
        with open("output_progressivo.txt") as f:
            for linha in f:
                if linha.strip():
                    try:
                        pos, bits = map(float, linha.strip().split())
                        comprimento_medio = bits / pos
                        dados.append((pos, comprimento_medio))
                    except:
                        pass

        if not dados:
            print("⚠️  Nenhum dado progressivo")
            return

        x, y = zip(*dados)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(x, y, linewidth=2, color="#2E86AB", label="Comprimento Médio")
        ax.set_xlabel("Posição no arquivo (símbolos)", fontsize=12)
        ax.set_ylabel("Bits/símbolo", fontsize=12)
        ax.set_title("Aprendizado Progressivo - TODO SILESIA (kmax=4)", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig("grafico_3_2_silesia_progressive.png", dpi=150)
        print("✅ Gráfico: grafico_3_2_silesia_progressive.png")

        # Análise
        if len(y) > 0:
            inicio = y[0] if y else 0
            fim = y[-1] if y else 0
            reducao = ((inicio - fim) / inicio * 100) if inicio > 0 else 0
            print(f"\n📊 Análise de Aprendizado:")
            print(f"   Comprimento inicial:  {inicio:.4f} bits/símbolo")
            print(f"   Comprimento final:    {fim:.4f} bits/símbolo")
            print(f"   Melhoria total:       {reducao:.1f}%")

    except ImportError:
        print("⚠️  matplotlib não disponível, gráfico não gerado")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")


def analise_3_3_silesia_todo():
    """3.3: Transições em TODO silesia com reset."""
    print("\n" + "=" * 80)
    print("3.3 ANÁLISE DE TRANSIÇÕES - TODO SILESIA")
    print("=" * 80)

    silesia_dir = "silesia"
    if not os.path.exists(silesia_dir):
        print(f"Erro: {silesia_dir} não encontrado")
        return

    arquivos = sorted(
        [
            os.path.join(silesia_dir, f)
            for f in os.listdir(silesia_dir)
            if os.path.isfile(os.path.join(silesia_dir, f))
        ]
    )

    if not arquivos:
        print("Nenhum arquivo")
        return

    total_original = sum(os.path.getsize(a) for a in arquivos)
    print(f"Arquivos: {len(arquivos)}")
    for a in arquivos:
        print(f"  - {os.path.basename(a)}: {os.path.getsize(a):,} bytes")
    print(f"Total: {total_original:,} bytes ({total_original / (1024**2):.1f} MB)\n")

    print("Comprimindo TODO Silesia com kmax=4, janela=1000, pct-reset=15%...")
    print("(Monitorando transições e resets)\n")

    tempo_inicio = time.time()
    cmd = (
        ["python3", "main.py", "0", "4"]
        + arquivos
        + [
            "--janela",
            "1000",
            "--pct-reset",
            "15",
            "--progressivo",
        ]
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=14400)
        tempo_comp = time.time() - tempo_inicio

        # Coletar eventos importantes
        transicoes = []
        resets = []

        for linha in result.stdout.split("\n"):
            if "Transição" in linha:
                print(linha)
                transicoes.append(linha)
            elif "Reset" in linha:
                print(linha)
                resets.append(linha)

        # Métricas
        if os.path.exists("output.ppmc"):
            tamanho_comp = os.path.getsize("output.ppmc")
            taxa = (tamanho_comp / total_original) * 100
            bits_sym = (tamanho_comp * 8) / total_original

            print(f"\n✅ Compressão TODO Silesia:")
            print(f"   Tempo total:        {tempo_comp:.1f}s")
            print(f"   Tamanho comprimido: {tamanho_comp:,} bytes")
            print(f"   Taxa:               {taxa:.1f}%")
            print(f"   Bits/símbolo:       {bits_sym:.4f}")
            print(f"   Transições detectadas: {len(transicoes)}")
            print(f"   Resets acionados:   {len(resets)}")

        # Reaproveita os dados progressivos desta mesma execução para 3.2
        if os.path.exists("output_progressivo.txt"):
            print("\nReaproveitando output_progressivo.txt para o experimento 3.2...")
            try_generate_plot_3_2()

        # Gerar gráfico de estrutura
        try_generate_plot_3_3(arquivos, total_original)

    except Exception as e:
        print(f"Erro: {e}")


def try_generate_plot_3_3(arquivos, total_bytes):
    """Gráfico esquemático do Silesia."""
    try:
        import matplotlib.pyplot as plt

        offsets = []
        offset_acumulado = 0
        for arq in arquivos:
            tam = os.path.getsize(arq)
            nome = os.path.basename(arq)
            offsets.append((offset_acumulado, offset_acumulado + tam, nome))
            offset_acumulado += tam

        fig, ax = plt.subplots(figsize=(14, 4))
        cores = plt.cm.tab20(range(len(offsets)))

        for i, (inicio, fim, nome) in enumerate(offsets):
            ax.barh(
                0,
                fim - inicio,
                left=inicio,
                height=0.5,
                label=nome,
                color=cores[i],
                edgecolor="black",
                linewidth=0.5,
            )

        ax.set_xlabel("Posição no arquivo (bytes)", fontsize=12)
        ax.set_title("Corpus Silesia - Estrutura com Transições", fontsize=14)
        ax.set_ylim(-1, 1)
        ax.set_xlim(0, total_bytes)
        ax.set_yticks([])
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=6, fontsize=9)

        plt.tight_layout()
        plt.savefig("grafico_3_3_silesia_structure.png", dpi=150, bbox_inches="tight")
        print("✅ Gráfico: grafico_3_3_silesia_structure.png")

    except ImportError:
        print("⚠️  matplotlib não disponível")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ANÁLISE FINAL - PPMC SILESIA")
    print("=" * 80)
    print("\nEscopo: 3.1, 3.2, 3.3 - APENAS SILESIA")
    print("Plano otimizado: 11 execuções (kmax 0..10) + 1 execução completa (3.2+3.3)")
    print("ETA otimizado: 3-4 horas\n")

    # Executar tudo automaticamente
    analise_3_1_silesia()
    analise_3_3_silesia_todo()
    analise_3_2_silesia_todo()

    print("\n" + "=" * 80)
    print("✅ ANÁLISE COMPLETA")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  - analise_3_1_silesia_completo.csv")
    print("  - grafico_3_2_silesia_progressive.png")
    print("  - grafico_3_3_silesia_structure.png")
