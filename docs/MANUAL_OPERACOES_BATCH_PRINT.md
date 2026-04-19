# 🖨️ AXIS-NIDDHI: Manual de Operações (Batch Print & Deploy)

Este manual descreve as funcionalidades de impressão em lote e deploy manual nativo implementadas no ecossistema AXIS-NIDDHI.

---

## ✅ Funcionalidades Entregues

### 1. Estética e Tipografia ("Walt Disney Magic")
*   **Links Clássicos**: Por padrão, os links são renderizados em **azul** (`#2b5fac`), seguindo o padrão conservador do PureDhamma original para facilitar a leitura.
*   **Magia ao Toque**: Ao passar o mouse sobre os links, eles transicionam suavemente para o **Verde Axioma** (`#00ff00`), proporcionando uma experiência imersiva e interativa.
*   **Menu Flutuante Resiliente**: O seletor de temas e o botão de impressão acompanham perfeitamente a rolagem da página, livres de interferências das animações de entrada.

### 2. Impressão Perfeita em Papel (Modo A4)
*   **Força Padrão A4**: Adicionada a regra estrita `@page { size: A4; }` no CSS. Agora, tanto a navegação nativa do usuário quanto o robô Headless gerarão PDFs formatados exatamente para papel A4, ignorando o padrão americano "Letter".
*   **Conservação de Cores**: O botão de impressão permite manter ativamente as cores do site (como as marcações em verde/azul e destaques em vermelho), substituindo configurações rascunho de predefinições do navegador.

### 3. Batch Print Engine (O Motor Cuidadoso de Revisão)
Um script robusto (`print_batch.py`) foi desenvolvido para ler a planilha central de traduções (`Print_Translation_Control_Center.csv`) e coordenar as impressões físicas massivas:
*   Filtra automaticamente os Ensaios aguardando atenção (onde `Status` = "DONE" mas `Printed?` ainda está vazio).
*   Levanta um servidor HTTP fantasma interno.
*   Usa o Google Chrome oculto (Headless) para fotografar perfeitamente as páginas mantendo todo o estilo original e gerando as páginas de PDF A4.
*   Oferece ao Revisor o modelo desejado antes de iniciar: Impressão de Frente Única (boa para rabiscar o verso) ou Frente e Verso (modo encadernação).
*   Envia diretamente os documentos via Daemon de Impressão Linux (CUPS) para a Epson L4260.
*   Respeita e entende o limite de 90 folhas por bandeja da L4260, pausando no momento certo para reabastecimento de papel.
*   Marca um carimbo de conformidade ("DONE (data) ") na planilha inicial quando impresso com sucesso.

### 4. Deploy Express (Com todos os Áudios)
*   Criação de rota expressa de Deploy nativo pelo terminal via `deploy_netlify.sh`.
*   Ultrapassa limitações de 1GB do Git LFS e das cotas do Netlify para o envio perfeito da montanha de 1.2 GB de áudios das pronúncias de Pali nativo.

---

## 🎮 Comandos do Terminal de Comando

| Ação | Comando a ser rodado no terminal raiz (bengyond-playground) |
|------|---------|
| Visualizar site temporário no seu computador | `cd pipeline/13-static-site && python3 -m http.server 8000` |
| Preparar PDFs do Lote 1 na pasta do computador | `python3 pipeline/scripts/tools/print_batch.py --lote 1 --pdf-only` |
| Gerar os PDFs do Lote 1 + Iniciar a impressora Epson L4260 | `python3 pipeline/scripts/tools/print_batch.py --lote 1` |
| Enviar todo o sistema ao Ar (Netlify Production com Áudios) | `bash pipeline/scripts/tools/deploy_netlify.sh` |
