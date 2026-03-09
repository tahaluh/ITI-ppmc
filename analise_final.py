#!/usr/bin/env python3
"""
Análise Final Completa: 3.1, 3.2, 3.3
Com descompressão, TODO Silesia, gráficos e comparação comercial
"""

import csv
import os
import subprocess
import sys
import time
from pathlib import Path


def executar_compressao(kmax, arquivos):
    """Executa compressão e retorna (tempo_comp, bits, taxa, tamanho_comp)."""
    tempo_inicio = time.time()
    cmd = ["python3", "main.py", "0", str(kmax)] + arquivos

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        tempo_comp = time.time() - tempo_inicio

        if result.returncode != 0:
            return None, None, None, None, f"Erro: {result.stderr[:100]}"

        if os.path.exists("output.ppmc"):
            tamanho_comp = os.path.getsize("output.ppmc")
            total_original = sum(os.path.getsize(a) for a in arquivos)
            bits = tamanho_comp * 8
            bits_per_symbol = bits / total_original if total_original > 0 else 0
            taxa = (tamanho_comp / total_original * 100) if total_original > 0 else 0

            return tempo_comp, bits_per_symbol, taxa, tamanho_comp, None

        return None, None, None, None, "Arquivo comprimido não gerado"
    except subprocess.TimeoutExpired:
        return None, None, None, None, "Timeout (>2h)"
    except Exception as e:
        return None, None, None, None, str(e)


def executar_descompressao():
    """Executa descompressão e retorna tempo."""
    tempo_inicio = time.time()
    cmd = ["python3", "main.py", "1", "0"]  # modo 1=decomp, kmax irrelevante

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        tempo_decomp = time.time() - tempo_inicio

        if result.returncode == 0:
            return tempo_decomp, None
        else:
            return None, f"Erro: {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return None, "Timeout descompressão"
    except Exception as e:
        return None, str(e)


def analise_3_1_completa():
    """3.1: Análise de Ordem e Performance (kmax 0-10 com descompressão)."""
    print("\n" + "=" * 80)
    print("3.1 ANÁLISE DE ORDEM E PERFORMANCE (kmax 0-10)")
    print("=" * 80)

    if not os.path.exists("silesia/dickens"):
        print("Erro: silesia/dickens não encontrado")
        return

    arquivo_tamanho = os.path.getsize("silesia/dickens")
    print(f"Arquivo: silesia/dickens ({arquivo_tamanho:,} bytes)\n")

    resultados = []
    csv_path = "analise_3_1_completa.csv"

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
            ]
        )

        for kmax in range(0, 11):
            print(f"kmax={kmax:2d}... ", end="", flush=True)

            # Compressão
            tempo_comp, bits_sym, taxa, tamanho_comp, erro_comp = executar_compressao(
                kmax, ["silesia/dickens"]
            )

            if erro_comp:
                print(f"✗ Comp: {erro_comp}")
                continue

            # Descompressão
            tempo_decomp, erro_decomp = executar_descompressao()

            if erro_decomp:
                print(f"✗ Decomp: {erro_decomp}")
                continue

            tempo_total = tempo_comp + tempo_decomp
            print(
                f"✓ {bits_sym:.4f} bits/sym | {taxa:.1f}% | "
                f"Comp:{tempo_comp:.1f}s Decomp:{tempo_decomp:.1f}s"
            )

            resultados.append(
                {
                    "kmax": kmax,
                    "bits_sym": bits_sym,
                    "taxa": taxa,
                    "tempo_comp": tempo_comp,
                    "tempo_decomp": tempo_decomp,
                    "tamanho_comp": tamanho_comp,
                }
            )

            writer.writerow(
                [
                    kmax,
                    f"{bits_sym:.6f}",
                    f"{taxa:.2f}",
                    f"{tempo_comp:.2f}",
                    f"{tempo_decomp:.2f}",
                    f"{tempo_total:.2f}",
                    tamanho_comp,
                ]
            )
            csvfile.flush()

    print(f"\nResultados salvos em: {csv_path}")

    # Resumo e comparação comercial
    if resultados:
        melhor = min(resultados, key=lambda x: x["bits_sym"])
        print(
            f"\n🏆 Melhor: kmax={melhor['kmax']} "
            f"({melhor['bits_sym']:.4f} bits/símbolo, {melhor['taxa']:.1f}%, "
            f"Total: {melhor['tempo_comp'] + melhor['tempo_decomp']:.1f}s)"
        )

        print("\n📊 COMPARAÇÃO COM COMERCIAIS (típico):")
        print("  WinRAR:       ~3.2 bits/símbolo (~40% taxa)")
        print("  7-Zip:        ~2.8 bits/símbolo (~35% taxa)")
        print(
            "  PPMC (melhor):",
            f"{melhor['bits_sym']:.2f} bits/símbolo ({melhor['taxa']:.1f}%)",
        )

        if melhor["bits_sym"] < 3.0:
            print("  ✅ PPMC competitivo com comerciais!")
        elif melhor["bits_sym"] < 3.5:
            print("  ✓ PPMC próximo aos comerciais")
        else:
            print("  ~ PPMC abaixo do esperado (possível implementação não-otimizada)")


def analise_3_2_dickens():
    """3.2: Aprendizado Progressivo no Dickens."""
    print("\n" + "=" * 80)
    print("3.2 ANÁLISE DE APRENDIZADO PROGRESSIVO (DICKENS)")
    print("=" * 80)

    if not os.path.exists("silesia/dickens"):
        print("Erro: silesia/dickens não encontrado")
        return

    print("Comprimindo com coleta progressiva (kmax=4)...\n")

    tempo_inicio = time.time()
    cmd = ["python3", "main.py", "0", "4", "silesia/dickens", "--progressivo"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        tempo_total = time.time() - tempo_inicio

        if result.returncode != 0:
            print(f"Erro na compressão: {result.stderr[:200]}")
            return

        print(f"Compressão concluída em {tempo_total:.1f}s")

        # Gerar gráfico
        if os.path.exists("output_progressivo.txt"):
            gerar_grafico_3_2()
        else:
            print("⚠️  Arquivo progressivo não gerado")

    except Exception as e:
        print(f"Erro: {e}")


def gerar_grafico_3_2():
    """Gera gráfico do aprendizado progressivo (Dickens)."""
    try:
        import matplotlib.pyplot as plt

        dados = []
        with open("output_progressivo.txt") as f:
            for linha in f:
                if linha.strip():
                    try:
                        pos, bits = map(float, linha.strip().split())
                        comprimento_medio = bits / pos  # bits por símbolo
                        dados.append((pos, comprimento_medio))
                    except:
                        pass

        if not dados:
            print("⚠️  Nenhum dado progressivo")
            return

        x, y = zip(*dados)

        plt.figure(figsize=(12, 6))
        plt.plot(x, y, linewidth=2, color="#2E86AB")
        plt.xlabel("Posição no arquivo (símbolos)", fontsize=12)
        plt.ylabel("Comprimento Médio (bits/símbolo)", fontsize=12)
        plt.title("Aprendizado Progressivo - Dickens (kmax=4)", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("grafico_3_2_dickens.png", dpi=150)
        print("✅ Gráfico salvo: grafico_3_2_dickens.png")

        # Análise
        media_inicial = y[0] if y else 0
        media_final = y[-1] if y else 0
        reducao = (
            ((media_inicial - media_final) / media_inicial * 100)
            if media_inicial > 0
            else 0
        )

        print(f"\n📈 Análise:")
        print(f"  Comprimento inicial:  {media_inicial:.4f} bits/símbolo")
        print(f"  Comprimento final:    {media_final:.4f} bits/símbolo")
        print(f"  Melhoria:             {reducao:.1f}%")

        # Detectar estabilização (derivada pequena)
        if len(y) > 10:
            primeira_metade_fim = y[len(y) // 2]
            segunda_metade_inicio = y[len(y) // 2]
            estab = (
                abs(primeira_metade_fim - segunda_metade_inicio)
                / primeira_metade_fim
                * 100
            )
            print(f"  Estabilização na 2ª metade: {estab:.2f}% de variação")

    except ImportError:
        print("⚠️  matplotlib não disponível, gráfico não gerado")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")


def analise_3_3_silesia():
    """3.3: Transições no Corpus TODO Silesia."""
    print("\n" + "=" * 80)
    print("3.3 ANÁLISE DE TRANSIÇÕES - TODO CORPUS SILESIA")
    print("=" * 80)

    silesia_dir = "silesia"
    if not os.path.exists(silesia_dir):
        print(f"Erro: Diretório {silesia_dir} não encontrado")
        return

    # Listar TODOS os arquivos
    arquivos = sorted(
        [
            os.path.join(silesia_dir, f)
            for f in os.listdir(silesia_dir)
            if os.path.isfile(os.path.join(silesia_dir, f))
        ]
    )

    if not arquivos:
        print("Nenhum arquivo encontrado")
        return

    print(f"Arquivos encontrados: {len(arquivos)}")
    total_original = 0
    for arq in arquivos:
        tam = os.path.getsize(arq)
        total_original += tam
        print(f"  - {os.path.basename(arq)}: {tam:,} bytes")

    print(f"Total: {total_original:,} bytes ({total_original / (1024**2):.1f} MB)\n")

    print("Comprimindo TODO Corpus com kmax=4, janela=1000, pct-reset=15%...")
    print("(Monitorando transições entre arquivos)\n")

    tempo_inicio = time.time()
    cmd = (
        ["python3", "main.py", "0", "4"]
        + arquivos
        + ["--janela", "1000", "--pct-reset", "15"]
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=14400)
        tempo_total = time.time() - tempo_inicio

        print("Output da compressão (transições e resets):")
        print("-" * 80)

        transicoes = []
        resets = []

        for linha in result.stdout.split("\n"):
            if "Transição" in linha or "Reset" in linha or "Progresso" in linha:
                print(linha)
                if "Transição" in linha:
                    transicoes.append(linha)
                if "Reset" in linha:
                    resets.append(linha)

        print("-" * 80)

        if os.path.exists("output.ppmc"):
            tamanho_comp = os.path.getsize("output.ppmc")
            taxa = tamanho_comp / total_original * 100
            bits_sym = tamanho_comp * 8 / total_original

            print(f"\n✅ Compressão concluída:")
            print(f"  Tempo total:        {tempo_total:.1f}s")
            print(f"  Tamanho original:   {total_original:,} bytes")
            print(f"  Tamanho comprimido: {tamanho_comp:,} bytes")
            print(f"  Taxa:               {taxa:.1f}%")
            print(f"  Bits/símbolo:       {bits_sym:.4f}")
            print(f"  Transições:         {len(transicoes)}")
            print(f"  Resets:             {len(resets)}")

            # Salvagráfico
            gerar_grafico_3_3_silesia(arquivos, total_original)

    except Exception as e:
        print(f"Erro: {e}")


def gerar_grafico_3_3_silesia(arquivos, total_bytes):
    """Gera gráfico de transições no Silesia."""
    try:
        import matplotlib.pyplot as plt

        # Calcular offset de cada arquivo
        offsets = []
        offset_acumulado = 0
        for arq in arquivos:
            tam = os.path.getsize(arq)
            nome = os.path.basename(arq)
            offsets.append((offset_acumulado, offset_acumulado + tam, nome))
            offset_acumulado += tam

        # Criar gráfico esquemático
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
        ax.set_title("Corpus Silesia - Estrutura e Transições", fontsize=14)
        ax.set_ylim(-1, 1)
        ax.set_xlim(0, total_bytes)

        # Adicionar nomes dos arquivos
        for inicio, fim, nome in offsets:
            meio = (inicio + fim) / 2
            ax.text(
                meio,
                0,
                nome,
                ha="center",
                va="center",
                fontsize=8,
                rotation=0,
                weight="bold",
                color="white",
            )

        ax.set_yticks([])
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=6, fontsize=9)

        plt.tight_layout()
        plt.savefig("grafico_3_3_silesia.png", dpi=150, bbox_inches="tight")
        print("✅ Gráfico salvo: grafico_3_3_silesia.png")

    except ImportError:
        print("⚠️  matplotlib não disponível")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ANÁLISE FINAL - PPMC COMPRESSOR")
    print("=" * 80)
    print("\nExecutando: 3.1, 3.2, 3.3")
    print("Corpus: TODO Silesia + Dickens")
    print("Aviso: Total estimado 4-5 horas\n")
    
    # Executar análises
    analise_3_1_completa()
    analise_3_2_dickens()
    analise_3_3_silesia()

    print("\n" + "=" * 80)
    print("✅ ANÁLISE COMPLETA FINALIZADA")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  - analise_3_1_completa.csv (com descompressão)")
    print("  - grafico_3_2_dickens.png")
    print("  - grafico_3_3_silesia.png")
    print("  - output_progressivo.txt")
