import csv, subprocess, time, pathlib
PYTHON = '/home/thaua/Documents/ufpb/pdi/tp2/venv/bin/python'
arquivo = 'silesia/dickens'
rows = []
for k in range(0, 11):
    print(f'k={k}: compressao...')
    t0 = time.perf_counter()
    c = subprocess.run([PYTHON, 'main.py', '0', str(k), arquivo], capture_output=True, text=True)
    tc = time.perf_counter() - t0
    if c.returncode != 0:
        print(c.stderr)
        raise SystemExit(f'Falha compressao k={k}')

    print(f'k={k}: descompressao...')
    t1 = time.perf_counter()
    d = subprocess.run([PYTHON, 'main.py', '1', str(k)], capture_output=True, text=True)
    td = time.perf_counter() - t1
    if d.returncode != 0:
        print(d.stderr)
        raise SystemExit(f'Falha descompressao k={k}')

    rows.append((k, round(tc, 2), round(td, 2)))
    print(f'k={k}: comp={tc:.2f}s decomp={td:.2f}s')

out = pathlib.Path('tempos_3_1_medidos.csv')
with out.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['kmax','tempo_comp_s','tempo_decomp_s'])
    w.writerows(rows)
print(f'CSV salvo em {out}')
