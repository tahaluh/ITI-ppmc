#!/usr/bin/env python3
"""
Script completo para análise 3.1, 3.2 e 3.3:
- 3.1: Performance com kmax variável (0-10)
- 3.2: Aprendizado progressivo no Dickens
- 3.3: Transições e reset no Corpus Silesia
"""

import csv
import os
import subprocess
import sys
import time
from pathlib import Path


def executar_compressao(kmax, arquivos, salvar_progressivo=False):
    """Executa compressão e retorna métricas."""
    tempo_inicio = time.time()

    cmd = ["python3", "main.py", "0", str(kmax)] + arquivos
    if salvar_progressivo:
        cmd.append("--progressivo")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        tempo_total = time.time() - tempo_inicio

        if result.returncode != 0:
            return None, tempo_total, result.stderr[:200]

        # Extrair informações do output
        bits_gerados = 0
        taxa_comp = 0.0

        for linha in result.stdout.split("\n"):
            if "Compressao finalizada" in linha:
                # Ex: "Compressao finalizada: 12345678 bits gerados"
                parts = linha.split()
                if len(parts) >= 4:
                    try:
                        bits_gerados = int(parts[3])
                    except:
                        pass
            if "Taxa de compressao" in linha:
                # Ex: "Taxa de compressão: 0.35" ou "35.0%"
                try:
                    taxa_str = linha.split(":")[-1].strip().rstrip("%")
                    taxa_comp = float(taxa_str)
                except:
                    pass

        # Tamanho do arquivo comprimido
        if os.path.exists("output.ppmc"):
            tamanho_comp = os.path.getsize("output.ppmc")
            total_original = sum(os.path.getsize(a) for a in arquivos)
            bits_por_simbolo = (
                (tamanho_comp * 8) / total_original if total_original > 0 else 0
            )

            return (
                {
                    "kmax": kmax,
                    "tamanho_original": total_original,
                    "tamanho_comprimido": tamanho_comp,
                    "bits_totais": tamanho_comp * 8,
                    "bits_por_simbolo": bits_por_simbolo,
                    "taxa_percent": (tamanho_comp / total_original * 100)
                    if total_original > 0
                    else 0,
                    "tempo_sec": tempo_total,
                },
                tempo_total,
                None,
            )

        return None, tempo_total, "Arquivo comprimido não encontrado"

    except subprocess.TimeoutExpired:
        return None, 7200, "Timeout (>2h)"
    except Exception as e:
        return None, 0, str(e)


def analise_3_1():
    """Análise 3.1: Performance com kmax variável (0-10)."""
    print("\n" + "=" * 70)
    print("3.1 ANÁLISE DE ORDEM E PERFORMANCE")
    print("=" * 70)

    # Usar arquivo único (Dickens)
    if not os.path.exists("silesia/dickens"):
        print("Erro: Arquivo 'silesia/dickens' não encontrado")
        return

    arquivo_tamanho = os.path.getsize("silesia/dickens")
    print(f"Arquivo: silesia/dickens ({arquivo_tamanho:,} bytes)")
    print(f"\nTestando kmax de 0 a 10...\n")

    resultados = []
    csv_path = "analise_3_1_resultados.csv"

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["kmax", "Bits/Símbolo", "Taxa (%)", "Tempo (s)", "Tamanho Comp. (bytes)"]
        )

        for kmax in range(0, 11):
            print(f"kmax={kmax:2d}... ", end="", flush=True)

            metricas, tempo, erro = executar_compressao(kmax, ["silesia/dickens"])

            if metricas:
                resultados.append(metricas)
                bits_sym = metricas["bits_por_simbolo"]
                taxa = metricas["taxa_percent"]
                print(f"✓ {bits_sym:.4f} bits/símbolo, {taxa:.1f}%, {tempo:.1f}s")
                writer.writerow(
                    [
                        kmax,
                        f"{bits_sym:.6f}",
                        f"{taxa:.2f}",
                        f"{tempo:.2f}",
                        metricas["tamanho_comprimido"],
                    ]
                )
            else:
                print(f"✗ Erro: {erro}")
                writer.writerow([kmax, "ERRO", "ERRO", "ERRO", "ERRO"])

            csvfile.flush()

    print(f"\nResultados salvos em: {csv_path}")

    # Resumo
    if resultados:
        melhor = min(resultados, key=lambda x: x["bits_por_simbolo"])
        pior = max(resultados, key=lambda x: x["bits_por_simbolo"])
        print(
            f"\nMelhor: kmax={melhor['kmax']} ({melhor['bits_por_simbolo']:.4f} bits/símbolo)"
        )
        print(
            f"Pior:   kmax={pior['kmax']} ({pior['bits_por_simbolo']:.4f} bits/símbolo)"
        )

    return resultados


def analise_3_2():
    """Análise 3.2: Aprendizado progressivo no Dickens."""
    print("\n" + "=" * 70)
    print("3.2 ANÁLISE DE APRENDIZADO E ESTACIONARIEDADE (DICKENS)")
    print("=" * 70)

    if not os.path.exists("silesia/dickens"):
        print("Erro: Arquivo 'silesia/dickens' não encontrado")
        return

    arquivo_tamanho = os.path.getsize("silesia/dickens")
    print(f"Arquivo: silesia/dickens ({arquivo_tamanho:,} bytes)")
    print(f"Gerando gráfico de comprimento médio progressivo...\n")

    # Usar kmax=4 (padrão)
    kmax = 4
    print(f"Usando kmax={kmax}...")

    metricas, tempo, erro = executar_compressao(
        kmax, ["silesia/dickens"], salvar_progressivo=True
    )

    if erro:
        print(f"Erro: {erro}")
        return

    # Verificar arquivo progressivo
    prog_file = "output_progressivo.txt"
    if os.path.exists(prog_file):
        print(f"✓ Dados progressivos salvos em: {prog_file}")

        # Analisar estabilização
        posicoes = []
        comprimentos = []

        with open(prog_file) as f:
            f.readline()  # cabeçalho
            for linha in f:
                parts = linha.strip().split(",")
                if len(parts) == 3:
                    try:
                        pos = int(parts[0])
                        comp = float(parts[2])
                        posicoes.append(pos)
                        comprimentos.append(comp)
                    except:
                        pass

        if comprimentos:
            # Encontrar ponto de estabilização (variação < 5% nos últimos 10%)
            n = len(comprimentos)
            if n > 10:
                final_10_pct = comprimentos[int(n * 0.9) :]
                media_final = sum(final_10_pct) / len(final_10_pct)

                for i, comp in enumerate(comprimentos):
                    if i >= int(n * 0.1):  # Após 10% do arquivo
                        variacao = (
                            abs(comp - media_final) / media_final
                            if media_final > 0
                            else 0
                        )
                        if variacao < 0.05:
                            ponto_estabil = posicoes[i]
                            print(
                                f"\\nPonto de estabilização: ~{ponto_estabil:,} bytes ({100 * ponto_estabil / arquivo_tamanho:.1f}% do arquivo)"
                            )
                            print(
                                f"Comprimento médio final: {media_final:.6f} bits/símbolo"
                            )
                            break

                # Criar script para gerar gráfico em matplotlib
                plot_script = "plotar_3_2.py"
                with open(plot_script, "w") as f:
                    f.write("""import matplotlib.pyplot as plt
import csv

# Ler dados
posicoes, comprimentos = [], []
with open('output_progressivo.txt') as file:
    next(file)
    for linha in file:
        parts = linha.strip().split(',')
        if len(parts) == 3:
            posicoes.append(int(parts[0]))
            comprimentos.append(float(parts[2]))

# Plotar
plt.figure(figsize=(12, 6))
plt.plot(posicoes, comprimentos, linewidth=1)
plt.xlabel('Posição no arquivo (bytes)')
plt.ylabel('Comprimento médio (bits/símbolo)')
plt.title('Comprimento Médio Progressivo - Dickens (kmax=4)')
plt.grid(True, alpha=0.3)
plt.savefig('grafico_3_2_dickens.png', dpi=100)
print('Gráfico salvo em: grafico_3_2_dickens.png')
plt.show()
""")
                print(f"\\nScript para gerar gráfico: {plot_script}")
                print("Execute: python3 plotar_3_2.py")


def analise_3_3():
    """Análise 3.3: Transições e reset no Corpus Silesia."""
    print("\n" + "=" * 70)
    print("3.3 ANÁLISE DE TRANSIÇÕES NO CORPUS SILESIA")
    print("=" * 70)

    # Listar arquivos do Silesia
    silesia_dir = "silesia"
    if not os.path.exists(silesia_dir):
        print(f"Aviso: Diretório '{silesia_dir}' não encontrado")
        print("Procurando arquivos individuais...")
        arquivos = [
            a
            for a in ["silesia/dickens", "silesia/mozilla", "silesia/xml"]
            if os.path.exists(a)
        ]
        if not arquivos:
            print("Erro: Nenhum arquivo encontrado")
            return
    else:
        arquivos = [
            os.path.join(silesia_dir, f)
            for f in os.listdir(silesia_dir)
            if os.path.isfile(os.path.join(silesia_dir, f))
        ]
        arquivos.sort()

    if not arquivos:
        print("Erro: Nenhum arquivo para analisar")
        return

    print(f"Arquivos encontrados: {len(arquivos)}")
    for arq in arquivos:
        tam = os.path.getsize(arq)
        print(f"  - {os.path.basename(arq)}: {tam:,} bytes")

    total_original = sum(os.path.getsize(a) for a in arquivos)
    print(f"Total: {total_original:,} bytes")

    print(f"\\nAnalisando com kmax=4, janela=1000, pct-reset=15%...")
    print("(Detectará transições entre arquivos e resets automáticos)\\n")

    tempo_inicio = time.time()
    cmd = (
        ["python3", "main.py", "0", "4"]
        + arquivos
        + ["--janela", "1000", "--pct-reset", "15"]
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        tempo_total = time.time() - tempo_inicio

        print("Output da compressão:")
        print("-" * 70)

        # Mostrar apenas linhas importantes
        transicoes = []
        resets = []

        for linha in result.stdout.split("\\n"):
            if any(
                x in linha
                for x in [
                    "Transição",
                    "Reset",
                    "Progresso",
                    "Compressao finalizada",
                    "Taxa",
                ]
            ):
                print(linha)
                if "Transição detectada" in linha:
                    transicoes.append(linha)
                if "Reset por piora" in linha:
                    resets.append(linha)

        print("-" * 70)
        print(f"\\nResumo:")
        print(f"  Transições detectadas: {len(transicoes)}")
        print(f"  Resets por piora de taxa: {len(resets)}")
        print(f"  Tempo total: {tempo_total:.2f}s")

        if os.path.exists("output.ppmc"):
            tamanho_comp = os.path.getsize("output.ppmc")
            taxa = (tamanho_comp / total_original) * 100
            bits_sym = (tamanho_comp * 8) / total_original
            print(f"  Tamanho comprimido: {tamanho_comp:,} bytes ({taxa:.1f}%)")
            print(f"  Bits por símbolo: {bits_sym:.4f}")

        # Criar script para análise de transições
        plot_script = "plotar_3_3.py"
        with open(plot_script, "w") as f:
            f.write("""import matplotlib.pyplot as plt
import os

# Ler arquivo progressivo se existir
if os.path.exists('output_progressivo.txt'):
    posicoes, comprimentos = [], []
    arquivo_nomes = {}
    offset = 0
    
    # Mapeamento de arquivos (precisa ser extraído do cabeçalho do .ppmc)
    # Por enquanto, usar aproximação visual
    
    with open('output_progressivo.txt') as file:
        next(file)
        for linha in file:
            parts = linha.strip().split(',')
            if len(parts) == 3:
                posicoes.append(int(parts[0]))
                comprimentos.append(float(parts[2]))
    
    plt.figure(figsize=(14, 7))
    plt.plot(posicoes, comprimentos, linewidth=1, marker='o', markersize=2)
    plt.xlabel('Posição no arquivo combinado (bytes)')
    plt.ylabel('Comprimento médio (bits/símbolo)')
    plt.title('Comprimento Médio Progressivo - Corpus Silesia')
    plt.grid(True, alpha=0.3)
    plt.savefig('grafico_3_3_silesia.png', dpi=100)
    print('Gráfico salvo em: grafico_3_3_silesia.png')
    plt.show()
else:
    print('Arquivo output_progressivo.txt não encontrado')
""")
        print(f"\\nScript para gerar gráfico: {plot_script}")

    except subprocess.TimeoutExpired:
        print("Timeout (>2h)")
    except Exception as e:
        print(f"Erro: {e}")


def main():
    print("\\n" + "=" * 70)
    print("ANÁLISE COMPLETA: 3.1, 3.2 e 3.3")
    print("=" * 70)

    # Confirmar se quer executar tudo (pode demorar muito)
    print("\\nAviso: Esta análise completa pode demorar várias horas!")
    print("3.1: ~15-30 min (kmax 0-10)")
    print("3.2: ~5-10 min (Dickens)")
    print("3.3: ~1-2 horas (Corpus Silesia)")

    resposta = input("\\nDeseja executar? (s/n): ").strip().lower()
    if resposta != "s":
        print("Análise cancelada")
        return

    # Executar análises
    try:
        resultados_3_1 = analise_3_1()
        analise_3_2()
        analise_3_3()

        print("\\n" + "=" * 70)
        print("ANÁLISE CONCLUÍDA!")
        print("=" * 70)
        print("\\nArquivos gerados:")
        print("  - analise_3_1_resultados.csv")
        print("  - output_progressivo.txt")
        print("  - plotar_3_2.py (para gerar gráfico)")
        print("  - plotar_3_3.py (para gerar gráfico)")

    except KeyboardInterrupt:
        print("\\nAnálise interrompida pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
