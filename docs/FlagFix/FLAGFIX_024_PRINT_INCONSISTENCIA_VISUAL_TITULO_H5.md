# #FlagFix_024 — Print / Site: inconsistência visual em título H5

**Status:** Aberto  
**Prioridade:** Baixa/Média  
**Tipo:** UI / CSS / Impressão  
**Escopo:** AXIS-NIDDHI static site  
**Detectado em:** 2026-05-01

---

## 1. Resumo

Foi detectada uma inconsistência visual em um título interno do post:

https://niddhi.pages.dev/pages/BD.AA.002/

No modo impressão/PDF, o título:

> Introdução

aparece visualmente diferente do padrão observado na maior parte dos demais ensaios impressos.

O bloco possui uma borda vertical escura à esquerda e tipografia verde forte, mas o espaçamento, peso visual e alinhamento parecem destoar do restante do sistema.

---

## 2. Evidência observada

Página afetada:

https://niddhi.pages.dev/pages/BD.AA.002/

Sintoma:

- título interno aparece como um bloco destacado;
- estilo parece diferente do padrão geral dos subtítulos;
- pode estar relacionado a `h5`, headings importados do WordPress, ou classes aplicadas durante a conversão CSL → static site;
- no PDF, a diferença fica mais evidente porque o layout é mais rígido.

---

## 3. Hipótese técnica

Possíveis causas:

1. O HTML original do PureDhamma.net usa um heading específico, possivelmente `h5`, em alguns posts.
2. O pipeline preserva esse heading corretamente, mas o CSS de impressão não normaliza todos os níveis de título.
3. Alguns headings podem estar recebendo estilos diferentes por combinação de:
   - tag HTML (`h4`, `h5`, `h6`);
   - classe herdada do WordPress;
   - regra global de `.content-block h5`;
   - regra dentro de `@media print`;
   - regra de collapsible/section heading reaproveitada no site.
4. O print CSS pode estar deixando `h5` mais “pesado” do que o desejado, enquanto outros posts usam `h2`/`h3` ou blocos normais.

---

## 4. Impacto

Não bloqueia leitura.

Não altera o conteúdo canônico.

Não altera tradução.

Mas afeta a sensação de consistência editorial do material impresso.

Para revisores humanos, isso pode causar a impressão de que aquele trecho tem uma importância estrutural diferente, mesmo quando talvez seja apenas um subtítulo comum.

---

## 5. Critério de investigação

Antes de corrigir, comparar pelo menos estes pontos:

```bash
grep -Rni "<h5\\|</h5\\|Introdução" \
  pipeline/13-static-site/pages/BD.AA.002/index.html \
  pipeline/13-ssg/templates \
  pipeline/13-ssg/static/css \
  | sed -n '1,160p'
````

Também verificar se há outros posts com `h5`:

```bash
grep -Rni "<h5\\|</h5" pipeline/13-static-site/pages \
  | sed -n '1,200p'
```

E contar ocorrências:

```bash
grep -Rni "<h5\\|</h5" pipeline/13-static-site/pages | wc -l
```

---

## 6. Diretriz de correção futura

A correção ideal deve ser global e conservadora:

* não editar conteúdo CSL;
* não alterar texto;
* não alterar títulos originais;
* não mexer em tradução;
* apenas normalizar a apresentação de headings internos no site e no modo impressão.

Possível solução:

1. criar uma regra CSS específica para `.content-block h5`;
2. garantir que no print `h5` tenha aparência consistente com os demais subtítulos;
3. preservar a borda lateral se ela for considerada parte da identidade visual;
4. evitar que o título fique grande demais, pesado demais ou com espaçamento excessivo.

---

## 7. Opção estética recomendada

Se a borda vertical for mantida, padronizar como feature editorial:

* borda vertical fina;
* verde AXIS/PureDhamma consistente;
* espaçamento equilibrado antes/depois;
* sem box verde cheio no print;
* aparência de “marcador de seção”, não de banner.

Exemplo conceitual:

```css
@media print {
  .content-block h5 {
    color: var(--green-axiom);
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.35;
    margin: 1.6rem 0 0.8rem;
    padding-left: 0.7rem;
    border-left: 2pt solid #555;
    break-after: avoid;
  }
}
```

Essa regra é apenas referência. Deve ser testada antes de aplicação.

---

## 8. Pergunta aberta

Determinar se o título “Introdução” nesse post deveria semanticamente ser:

* `h2`;
* `h3`;
* `h4`;
* `h5`;
* ou apenas um parágrafo destacado preservado do original.

Se o HTML original do PureDhamma.net usa `h5`, o AXIS pode preservar semanticamente, mas ainda normalizar visualmente para impressão.

---

## 9. Recomendação

Manter este FlagFix aberto até existir uma auditoria de headings em todo o corpus.

Este problema provavelmente não é isolado.

A ação correta é criar uma pequena auditoria automática:

```bash
grep -Rni "<h1\\|<h2\\|<h3\\|<h4\\|<h5\\|<h6" pipeline/13-static-site/pages \
  > metadata/reports/heading_inventory.txt
```

Depois, revisar os padrões mais frequentes antes de mexer no CSS.

---

## 10. Escopo proibido

Este FlagFix não deve:

* alterar CSL;
* alterar PureDhamma source;
* alterar tradução;
* alterar termos Pāli;
* normalizar cores didáticas;
* mexer em links;
* modificar estrutura de navegação.

Somente apresentação visual de headings internos.

---

## 11. Classificação para GitHub Issue

**Título sugerido:**

`#FlagFix_024: Normalize internal H5 heading style in print/site output`

**Labels sugeridas:**

* `flagfix`
* `print`
* `css`
* `ui-polish`
* `low-risk`
* `needs-audit`

EOF
