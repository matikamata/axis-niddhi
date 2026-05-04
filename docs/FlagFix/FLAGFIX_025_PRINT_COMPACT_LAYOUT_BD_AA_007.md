# #FlagFix_025 — Impressão: layout muito espremido em BD.AA.007

**Status:** aberto para investigação futura  
**Severidade:** média  
**Escopo:** impressão/PDF, CSS de layout, imagens/vídeos, regras globais de print  
**Página afetada observada:** `https://niddhi.pages.dev/pages/BD.AA.007/`  
**PD#PN:** `BD.AA.007`  
**Título:** `Evidence For Rebirth` / `Evidências do Renascimento`

---

## 1. Sintoma observado

Ao imprimir a página `BD.AA.007`, o conteúdo aparece visualmente mais estreito/espremido do que em outros ensaios já revisados, mesmo usando as mesmas configurações no diálogo de impressão do navegador:

- Papel: A4
- Escala: “Fit to page width”
- Margens: mesmas configurações usadas nos demais testes
- Cabeçalhos/rodapés do navegador: ligados
- Backgrounds: ligados

O screenshot mostra que a coluna de texto parece ocupar uma largura menor e o corpo impresso fica mais compacto, gerando a impressão de que a página tem uma régua de layout diferente das demais.

---

## 2. Por que isso importa

Esse problema não é apenas estético. Para revisão humana em papel/PDF, a largura da coluna afeta:

- legibilidade;
- quantidade de páginas geradas;
- conforto do revisor;
- consistência visual entre PDFs arquivados;
- confiança de que todos os ensaios seguem a mesma política de impressão.

Como o AXIS-NIDDHI está sendo usado para revisão e preservação, páginas com comportamento visual divergente devem ser rastreadas como possíveis sinais de inconsistência no template, no conteúdo herdado do WordPress, ou nas regras CSS de impressão.

---

## 3. Hipóteses de causa raiz

### H1 — Conteúdo específico causando shrink-to-fit do navegador

A página contém múltiplos vídeos/embeds, links longos, imagens e caixas de marcador de vídeo. Algum elemento pode estar excedendo a largura imprimível e forçando o navegador a recalcular o layout de forma mais estreita.

Investigar especialmente:

- `.print-video-marker`
- imagens grandes ou com largura fixa herdada
- iframes/embeds ocultos na impressão, mas ainda influenciando layout antes do print
- links longos dentro dos marcadores de vídeo
- blocos com `width`, `min-width`, `max-width`, `margin`, `padding` ou `transform`

### H2 — Regra de print global não centraliza a área útil de forma robusta

Mesmo que o conteúdo principal tenha `max-width`, pode estar faltando uma regra clara para garantir:

```css
@media print {
  main,
  .content-block {
    margin-left: auto;
    margin-right: auto;
    box-sizing: border-box;
  }
}
```

Atenção: isso deve ser testado com muito cuidado para não quebrar páginas que já imprimem bem.

### H3 — Diferença entre visualização do navegador e preview de impressão

O diálogo de impressão pode aplicar escala automática diferente quando detecta conteúdo horizontalmente largo. Mesmo com as mesmas configurações, o mecanismo do navegador pode reduzir uma página específica se algum elemento “vazar” horizontalmente.

### H4 — Elementos invisíveis ainda participando do layout

Alguns elementos escondidos para impressão podem estar com `display: none`, mas outros podem estar apenas invisíveis ou deslocados. Verificar se algum elemento de navegação, toc, LABZ, vídeo ou imagem está deixando largura residual.

---

## 4. Verificações recomendadas

Rodar no repositório local:

```bash
cd ~/axis/axis-niddhi-production

# Confirmar branch seguro
git status -sb

# Procurar estilos inline ou wrappers suspeitos no HTML gerado
python3 - <<'PY'
from pathlib import Path
p = Path('pipeline/13-static-site/pages/BD.AA.007/index.html')
text = p.read_text(encoding='utf-8', errors='replace')
for needle in ['width:', 'min-width', 'max-width', 'iframe', 'video-container', 'youtube', 'print-video-marker', 'style=']:
    print('\n===', needle, '===')
    for i, line in enumerate(text.splitlines(), 1):
        if needle.lower() in line.lower():
            print(f'{i}: {line[:240]}')
PY

# Comparar com uma página que imprime bem
python3 - <<'PY'
from pathlib import Path
pages = [
    'pipeline/13-static-site/pages/BD.AA.007/index.html',
    'pipeline/13-static-site/pages/TL.JJ.008/index.html',
]
for page in pages:
    text = Path(page).read_text(encoding='utf-8', errors='replace')
    print('\n===', page, '===')
    print('iframe:', text.lower().count('<iframe'))
    print('img:', text.lower().count('<img'))
    print('style=:', text.lower().count('style='))
    print('youtube:', text.lower().count('youtube'))
    print('video-container:', text.lower().count('video-container'))
PY
```

---

## 5. Teste visual recomendado

Criar uma branch própria antes de qualquer tentativa de correção:

```bash
cd ~/axis/axis-niddhi-production
git switch main
git pull origin main
git switch -c flagfix-025-print-layout-bd-aa-007
```

Testar localmente:

```bash
python3 -m http.server 8080 -d pipeline/13-static-site
```

Abrir:

```text
http://localhost:8080/pages/BD.AA.007/
```

Comparar com pelo menos três páginas que já imprimem bem:

```text
http://localhost:8080/pages/TL.JJ.008/
http://localhost:8080/pages/BD.AA.002/
http://localhost:8080/pages/TL.EE.003/
```

---

## 6. Direção de correção possível

A correção ideal deve ser global, mas somente após diagnóstico.

Possíveis linhas de ação:

1. criar um “print content frame” robusto para todos os posts;
2. garantir que imagens, vídeos e marcadores respeitem `max-width: 100%`;
3. garantir que `main` e `.content-block` fiquem centralizados em print;
4. detectar elementos que causam overflow horizontal;
5. adicionar um teste automático simples para listar páginas com largura/overflow suspeito.

Evitar correções específicas para `BD.AA.007` sem antes confirmar a causa raiz, pois o mesmo padrão pode existir em outras páginas com muitos vídeos/imagens.

---

## 7. Critério de aceite

O #FlagFix_025 pode ser considerado resolvido quando:

- `BD.AA.007` imprimir com largura visual consistente com páginas já aprovadas;
- não houver regressão em `TL.JJ.008`, `BD.AA.002`, `TL.EE.003` e outras páginas com vídeos;
- os marcadores de vídeo continuarem aparecendo corretamente;
- links, cores didáticas e legendas de revisão continuarem preservados;
- o diff tocar apenas CSS/JS/template estritamente necessário;
- não houver alteração no CSL/corpus canônico.

---

## 8. Observação para GitHub Issue

Título sugerido:

```text
#FlagFix_025: Print layout too narrow/compact on BD.AA.007
```

Labels sugeridas:

```text
print
css
layout
review-pdf
flagfix
medium
```

Descrição curta:

```text
BD.AA.007 prints with a noticeably narrower/over-compressed content column compared with other reviewed posts, despite identical browser print settings. Investigate whether videos, images, long URLs, hidden embeds, or print CSS width rules are causing shrink-to-fit behavior. Fix should be global and must preserve PureDhamma didactic colors, video traceability markers, and canonical content.
```

---

## 9. Nota arquitetural

Este issue pertence ao bloco de refinamento de impressão/revisão, não ao bloco de tradução nem ao bloco canônico. Ele deve ser agrupado com outros #FlagFix relacionados a PDF/print antes de virar PR, para evitar microcorreções espalhadas.

