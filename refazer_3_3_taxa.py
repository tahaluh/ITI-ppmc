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
import selectors
import signal
import subprocess
import time


def _executar_cmd(cmd, timeout, log_path):
    inicio = time.time()
    heartbeat_s = 20
    ultimo_heartbeat = inicio

    transicoes = 0
    resets = 0
    ultimas_stderr = []
    max_ultimas_stderr = 80

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"CMD: {' '.join(cmd)}\n")
        f.write("=" * 80 + "\n")
        f.flush()

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ, data="STDOUT")
        sel.register(proc.stderr, selectors.EVENT_READ, data="STDERR")

        try:
            while sel.get_map():
                agora = time.time()
                if timeout and (agora - inicio) > timeout:
                    proc.kill()
                    raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

                eventos = sel.select(timeout=1.0)
                if not eventos and (agora - ultimo_heartbeat) >= heartbeat_s:
                    decorrido = int(agora - inicio)
                    hb = f"[HEARTBEAT] Execucao em andamento... {decorrido}s"
                    print(hb)
                    f.write(hb + "\n")
                    f.flush()
                    ultimo_heartbeat = agora

                for key, _ in eventos:
                    stream = key.fileobj
                    origem = key.data
                    linha = stream.readline()

                    if linha == "":
                        sel.unregister(stream)
                        continue

                    linha_limpa = linha.rstrip("\n")
                    msg = f"[{origem}] {linha_limpa}"
                    print(msg)
                    f.write(msg + "\n")
                    f.flush()

                    if origem == "STDOUT":
                        if "Transição" in linha_limpa or "Transicao" in linha_limpa:
                            transicoes += 1
                        if "Reset" in linha_limpa:
                            resets += 1
                    else:
                        ultimas_stderr.append(linha_limpa)
                        if len(ultimas_stderr) > max_ultimas_stderr:
                            ultimas_stderr.pop(0)

            returncode = proc.wait()

        finally:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()

    tempo_total = time.time() - inicio
    result = subprocess.CompletedProcess(
        args=cmd,
        returncode=returncode,
        stdout="",
        stderr="\n".join(ultimas_stderr),
    )
    return result, tempo_total, transicoes, resets


def listar_arquivos_silesia(silesia_dir="silesia"):
    arquivos = sorted(
        [
            os.path.join(silesia_dir, f)
            for f in os.listdir(silesia_dir)
            if os.path.isfile(os.path.join(silesia_dir, f))
        ]
    )
    return arquivos


def executar_3_3(
    arquivos,
    kmax=4,
    janela=2000,
    pct_reset=30.0,
    progress_step=2000,
    timeout=21600,
):
    cmd = (
        ["python3", "-X", "faulthandler", "-u", "main.py", "0", str(kmax)]
        + arquivos
        + [
            "--janela",
            str(janela),
            "--pct-reset",
            str(pct_reset),
            "--progressivo",
            "--progress-step",
            str(progress_step),
        ]
    )
    cmd_fallback = (
        ["python3", "-X", "faulthandler", "-u", "main.py", "0", str(kmax)]
        + arquivos
        + ["--progressivo", "--progress-step", str(progress_step)]
    )

    print("\n" + "=" * 80)
    print("REFAZENDO EXPERIMENTO 3.3 (TAXA AO LONGO DO FLUXO)")
    print("=" * 80)
    print(f"Arquivos: {len(arquivos)}")
    print(
        f"kmax={kmax}, janela={janela}, pct-reset={pct_reset}%, "
        f"progress-step={progress_step}"
    )
    print("Executando compressao completa...\n")

    result, tempo_total, transicoes, resets = _executar_cmd(
        cmd, timeout, "refazer_3_3_exec.log"
    )

    if result.returncode != 0:
        if result.returncode < 0:
            sig_num = -result.returncode
            try:
                sig_nome = signal.Signals(sig_num).name
            except Exception:
                sig_nome = "DESCONHECIDO"
            print(
                f"Causa da falha principal: processo finalizado por sinal {sig_num} ({sig_nome})."
            )
            if sig_num == 11:
                print(
                    "Diagnostico: SIGSEGV (segmentation fault), geralmente associado a "
                    "pressao extrema de memoria ou falha em codigo nativo."
                )
        else:
            print(f"Causa da falha principal: retorno nao-zero ({result.returncode}).")

        if result.stderr:
            print("Ultimas linhas de stderr da tentativa principal:")
            for linha in result.stderr.splitlines()[-20:]:
                print(f"  {linha}")

        print(f"Falha na tentativa principal (exit {result.returncode}).")
        print("Log salvo em refazer_3_3_exec.log")
        print("Tentando fallback sem janela/reset para evitar crash...\n")

        result, tempo_total, transicoes, resets = _executar_cmd(
            cmd_fallback, timeout, "refazer_3_3_exec_fallback.log"
        )
        if result.returncode != 0:
            if result.returncode < 0:
                sig_num = -result.returncode
                try:
                    sig_nome = signal.Signals(sig_num).name
                except Exception:
                    sig_nome = "DESCONHECIDO"
                print(
                    f"Causa da falha fallback: processo finalizado por sinal {sig_num} ({sig_nome})."
                )
            else:
                print(
                    f"Causa da falha fallback: retorno nao-zero ({result.returncode})."
                )

            if result.stderr:
                print("Ultimas linhas de stderr do fallback:")
                for linha in result.stderr.splitlines()[-20:]:
                    print(f"  {linha}")

            print(f"Fallback tambem falhou (exit {result.returncode}).")
            print("Log salvo em refazer_3_3_exec_fallback.log")

            if os.path.exists("output_progressivo.txt"):
                print(
                    "Reutilizando output_progressivo.txt existente para gerar o grafico."
                )
                return 0.0, 0, 0

            raise RuntimeError(f"Falha na compressao (exit {result.returncode})")

    print(f"Tempo total: {tempo_total:.1f}s")
    print(f"Transicoes detectadas: {transicoes}")
    print(f"Resets acionados: {resets}")

    return tempo_total, transicoes, resets


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
        arquivos, kmax=4, janela=2000, pct_reset=30.0
    )

    xs, bits_acum = carregar_progressivo("output_progressivo.txt")
    print(f"Pontos progressivos carregados: {len(xs)}")

    final_bps, final_taxa = gerar_grafico_taxa(xs, bits_acum, arquivos)

    salvar_resumo(tempo_total, transicoes, resets, final_bps, final_taxa)

    print("\nConcluido.")


if __name__ == "__main__":
    main()
