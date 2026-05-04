# #FlagFix_022 — Shortcode WordPress `easy_media_download` vazando no site estático

## Status

Aberto para investigação futura.

## Severidade

MÉDIO / ALTO

Não é apenas um problema visual. O conteúdo exibido no site estático contém um shortcode WordPress bruto que deveria ter sido convertido, removido, renderizado ou substituído por um componente equivalente.

## Página afetada observada

AXIS-NIDDHI:

https://niddhi.pages.dev/pages/TL.EE.003/

Trecho afetado no fim do post:

```text
[easy_media_download url="https://drive.google.com/open?id=1g1Pazd97MvrEit1mAf2rmhzJYuRW3XYD" text="Baixar" width="90" target="_blank"]
````

Página original PureDhamma.net relacionada:

[https://puredhamma.net/three-levels-of-practice/moral-living-and-fundamentals/kilesa-relationship-to-akusala-kusala-and-punna-kamma/](https://puredhamma.net/three-levels-of-practice/moral-living-and-fundamentals/kilesa-relationship-to-akusala-kusala-and-punna-kamma/)

## Sintoma observado

No site e na impressão/PDF, aparece texto técnico bruto do WordPress:

```text
[easy_media_download ...]
```

Isso não deveria aparecer para o leitor final nem para o revisor de tradução.

No contexto do post, o shortcode aparece logo após uma referência a um desana/áudio, onde provavelmente o site original esperava renderizar um botão de download ou link de mídia.

## Diagnóstico provável

O pipeline de extração/conversão preservou o shortcode WordPress como texto comum, sem interpretá-lo.

Possíveis causas:

1. O parser HTML não remove shortcodes WordPress desconhecidos.
2. O shortcode `easy_media_download` não está mapeado na camada de normalização.
3. O WordPress original renderiza esse shortcode dinamicamente via plugin, mas o export/HTML usado pelo AXIS-NIDDHI capturou a forma bruta.
4. A conversão para CSL preservou corretamente o texto recebido, mas não havia uma regra semântica para transformar esse shortcode em um link seguro.
5. O sistema de impressão apenas revelou o problema já existente no conteúdo estático.

## Importante

Este FlagFix não deve ser tratado como problema de impressão.

A impressão apenas tornou o defeito mais visível.

O problema real está em uma camada anterior:

* extração WordPress;
* pré-processamento HTML;
* normalização CSL;
* renderização SSG;
* ou regras de limpeza de shortcodes.

## Impacto

### Para o leitor

O shortcode parece erro técnico e quebra a experiência de leitura.

### Para o revisor

Pode gerar dúvida sobre se o trecho deve ser traduzido, removido, preservado ou transformado em link.

### Para preservação

Shortcodes WordPress são dependências de runtime/plugin. Em um site estático preservado por milênios, eles não devem permanecer como instruções opacas.

### Para auditoria

A presença de shortcodes brutos indica que pode haver outros resíduos WordPress ainda não tratados no corpus.

## Hipótese de correção futura

Criar uma etapa de auditoria e normalização de shortcodes WordPress.

Exemplo de detecção:

```bash
grep -RniE '\[[a-zA-Z0-9_-]+[[:space:]][^]]*\]' pipeline/09-csl pipeline/13-static-site
```

Ou especificamente:

```bash
grep -Rni "easy_media_download" pipeline/
```

## Regra proposta

### Para `easy_media_download`

Quando encontrado:

```text
[easy_media_download url="URL" text="TEXT" width="90" target="_blank"]
```

Transformar em HTML semântico:

```html
<p class="media-download-link">
  <a href="URL" target="_blank" rel="noopener noreferrer">
    TEXT
  </a>
</p>
```

Para pt-BR, se `text="Download"` ou `text="Baixar"` estiver presente, preservar conforme origem ou normalizar de acordo com política futura.

## Regra de fallback

Se o shortcode for reconhecido mas não puder ser convertido com segurança:

```html
<div class="axis-source-note">
  Media/download reference preserved from source. Manual review required.
</div>
```

Em pt-BR:

```html
<div class="axis-source-note">
  Referência de mídia/download preservada da fonte. Revisão manual necessária.
</div>
```

## O que NÃO fazer agora

Não editar manualmente apenas essa página.

Não remover o shortcode sem registrar o link.

Não transformar cegamente todos os shortcodes em texto invisível.

Não fazer correção somente via CSS `display:none`, pois isso esconderia uma referência potencialmente importante.

## Ação futura recomendada

Criar um script de auditoria:

```text
SA_shortcodes_audit.py
```

Objetivos:

1. Escanear todo o corpus por shortcodes WordPress remanescentes.
2. Gerar relatório CSV/JSON com:

   * PD#PN;
   * caminho do arquivo;
   * shortcode encontrado;
   * URL interna/externa se existir;
   * tipo de shortcode;
   * ação sugerida.
3. Classificar cada shortcode como:

   * conversível automaticamente;
   * requer revisão humana;
   * deve ser preservado como nota;
   * deve ser removido por ser ruído técnico.

## Possíveis shortcodes a procurar

Lista inicial:

```text
[easy_media_download ...]
[audio ...]
[video ...]
[caption ...]
[gallery ...]
[embed ...]
[playlist ...]
```

## Critério de aceite futuro

Este FlagFix pode ser considerado resolvido quando:

1. Nenhum shortcode WordPress bruto aparecer no site estático final.
2. Nenhum shortcode bruto aparecer em PDFs de revisão.
3. Shortcodes de mídia forem convertidos para links/componentes estáticos.
4. Um relatório de auditoria listar todos os shortcodes encontrados e suas ações.
5. O comportamento for reproduzível via pipeline, sem correções manuais por página.

## Nota para posteridade

Este é um exemplo clássico de dependência invisível do WordPress.

No WordPress original, um plugin podia transformar automaticamente esse trecho em botão, player ou link. No AXIS-NIDDHI, porém, o objetivo é preservação estática, reprodutível e independente de runtime. Portanto, qualquer shortcode remanescente deve ser tratado como vestígio de uma camada dinâmica antiga.

A solução correta não é esconder o problema, mas transformar a intenção semântica do shortcode em HTML estático, auditável e preservável.

## Convite às Abelhas

Este FlagFix é uma boa tarefa para colaboradores técnicos interessados em preservação digital.

Ajuda necessária:

* mapear todos os shortcodes remanescentes;
* identificar quais plugins WordPress os geravam;
* propor equivalentes HTML estáticos;
* criar testes de regressão;
* garantir que nenhuma informação de mídia seja perdida.

Objetivo final:

Transformar resíduos WordPress em artefatos estáticos claros, bonitos e duráveis.

---

## Read-only Triage / Triagem sem implementação

Status: partially implemented / operationally resolved / hardening pending.

The original visible `TL.EE.003` raw shortcode leak is no longer reader-facing.

Recognized shortcodes are preserved as `axis-media-evidence` media evidence blocks.

Corrupted or unknown legacy media cases may remain as review evidence, including `LEGACY_MEDIA_CORRUPTED`, `LEGACY_MEDIA_UNKNOWN`, and `RAW_SHORTCODE` evidence in HTML comments.

No immediate implementation is recommended.

Future hardening requires a corpus-wide audit.

No manual CSL or static-site page edits are recommended.

Recommended future hardening items:

1. audit all `axis-media-evidence` blocks;
2. inventory `LEGACY_MEDIA_CORRUPTED` / `LEGACY_MEDIA_UNKNOWN` cases;
3. review `RAW_SHORTCODE` evidence in HTML comments;
4. detect invalid surrounding markup;
5. investigate glossary/Pāli markup inside shortcode URLs;
6. only then consider pipeline hardening and an approved rebuild.
