# Ultra-Foco (#UlFO)

## a) Mapa visual — AXIS-NIDDHI (1 página)

Você pode enviar isto para a Vayo **depois da próxima resposta dela**.

```text
AXIS-NIDDHI ARCHITECTURE MAP
(one-page mental model)

                    ┌────────────────────────────┐
                    │        KNOWLEDGE            │
                    │         CORPUS              │
                    │     (PureDhamma etc.)       │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │   SOURCES       │
                        │  raw materials  │
                        │  html / text    │
                        └────────┬────────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │     AXIS ENGINE     │
                     │  30 CORE SCRIPTS    │
                     │ deterministic build │
                     └─────────┬───────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     WORKSPACE       │
                    │ transformation      │
                    │ normalization       │
                    └─────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │      RELEASE       │
                     │ canonical output   │
                     │ site / artifacts   │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │   MANIFEST SHA256  │
                     │ deterministic hash │
                     │ verification layer │
                     └─────────┬──────────┘
                               │
                               ▼
                   ┌──────────────────────┐
                   │    ARCHAEOLOGY       │
                   │ historical snapshots │
                   │ preservation layer   │
                   └──────────────────────┘


EVOLUTION ROADMAP

V5.4  Canon Engine
      deterministic pipeline

V6    Multi-Corpus
      corpus registry + adapters

V7    Council Layer
      independent builds
      manifest consensus
```

**Função:**
Esse mapa vira o **“modelo mental instantâneo”** de qualquer operador novo.

---

# b) Rodar o pipeline com tranquilidade (step-by-step)

### 0️⃣ Entrar no projeto

```bash
cd /beng-fut/pipeline
```

ou diretório equivalente do engine.

---

### 1️⃣ Verificar integridade do engine

```bash
./verify_pipeline_integrity.sh
```

Esperado:

```
CORE scripts: 30/30
Pipeline spine: OK
Integrity: PASS
```

Se falhar → **não rodar build ainda**.

---

### 2️⃣ Limpar workspace

Evita resíduos de builds anteriores.

```bash
rm -rf workspace/*
```

ou usar script se existir:

```bash
./clean_workspace.sh
```

---

### 3️⃣ Executar pipeline

Rodar sequência canônica.

Exemplo típico:

```bash
./00_bootstrap.sh
./01_ingest.sh
./02_preprocess.sh
./03_structure.sh
./04_csl_build.sh
./05_output.sh
```

(ou o **runner único**, se houver)

```bash
./run_pipeline.sh
```

---

### 4️⃣ Verificar saída

Conferir se o corpus foi gerado:

```
dist/
09-csl/
release/
```

Checar contagem esperada:

```
posts: 748
languages: EN + PT-BR
```

---

### 5️⃣ Criar snapshot canônico

```bash
./build_release_snapshot.sh
```

Isso gera:

```
manifest.sha256
release archive
```

---

### 6️⃣ Verificar determinismo

Rodar novamente:

```bash
./build_release_snapshot.sh
```

Comparar:

```
manifest.sha256
```

Se **idêntico → build determinístico**.

---

### 7️⃣ Arquivar

Mover snapshot para archaeology:

```
/archaeology/releases/
```

ou equivalente.

---

# Pipeline completo em 30 segundos (resumo)

```bash
cd pipeline

./verify_pipeline_integrity.sh
rm -rf workspace/*
./run_pipeline.sh
./build_release_snapshot.sh
```

---

✅ **Resultado esperado**

```
canonical release generated
manifest verified
pipeline deterministic
```

---

Se quiser, no próximo passo posso te mostrar **uma propriedade estrutural muito rara do AXIS-NIDDHI** que explica por que esse tipo de sistema pode sobreviver **décadas ou séculos sem corromper o corpus** — algo que quase todos os repositórios digitais falham em fazer.

