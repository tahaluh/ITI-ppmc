# Compressor PPMC (Prediction by Partial Matching)

Implementacao de PPMC com codificacao aritmetica para compressao/descompressao e scripts de analise dos experimentos 3.1, 3.2 e 3.3.

## Requisitos

- Python 3.10+
- (Opcional) ambiente virtual `venv`
- `matplotlib` para gerar graficos

## Uso Basico (`main.py`)

### Compressao

```bash
python3 main.py 0 <kmax> <arquivo1> [arquivo2 ...] [opcoes]
```

Exemplo (arquivo unico):

```bash
python3 main.py 0 4 silesia/dickens
```

Exemplo (multiplos arquivos com monitoramento):

```bash
python3 main.py 0 4 silesia/dickens silesia/mozilla silesia/xml --janela 1000 --pct-reset 15 --progressivo --progress-step 2000
```

### Descompressao

```bash
python3 main.py 1 <kmax>
```

Exemplo:

```bash
python3 main.py 1 4
```

## Parametros

- `mode`: `0` para comprimir, `1` para descomprimir.
- `kmax`: ordem maxima de contexto.
- `arquivos`: um ou mais arquivos de entrada (obrigatorio em `mode=0`).
- `--janela [N]`: ativa monitoramento local (padrao `1000` se passado sem valor).
- `--pct-reset X`: limiar de piora percentual para reset (padrao `10.0`).
- `--progressivo`: salva dados de aprendizado progressivo em `output_progressivo.txt`.
- `--progress-step N`: passo de amostragem do progressivo (padrao `1000`).

## Entradas e Saidas

- Comprimido: `output.ppmc`
- Progressivo: `output_progressivo.txt` (quando `--progressivo`)
- Descomprimido: `descomprimido/<nome_original>`

## Experimentos

### 3.1 - Ordem e Performance

Script principal no repositorio:

```bash
python3 analise_silesia_final.py
```

Tambem existe CSV de referencia:

- `analise_3_1_silesia_completo.csv`

### 3.2 - Aprendizado Progressivo (Dickens)

Opcao rapida:

```bash
python3 main.py 0 4 silesia/dickens --progressivo --progress-step 1000
python3 plotar_3_2.py
```

Alternativa com script dedicado:

```bash
python3 gerar_3_2.py
```

Saida esperada:

- `grafico_3_2_silesia_progressive.png`

### 3.3 - Transicoes e Reset (Silesia)

Script recomendado:

```bash
python3 refazer_3_3_taxa.py
```

Esse script:

- executa compressao de todo o Silesia com reset adaptativo;
- registra logs em tempo real + heartbeat;
- em caso de falha, tenta fallback sem janela/reset;
- gera:
	- `grafico_3_3_taxa_ao_longo.png`
	- `resumo_3_3_taxa.txt`
	- `refazer_3_3_exec.log` (e fallback, se houver)

## Observacoes

- `exit code 130` normalmente indica interrupcao manual (`Ctrl+C`).
- `exit -11` indica termino por sinal `SIGSEGV` no processo filho.
- Para reduzir custo de E/S e memoria no progressivo, prefira `--progress-step` entre `1000` e `5000` para corpus grandes.
- O experimento 3.3 pode levar dezenas de minutos dependendo da maquina.
