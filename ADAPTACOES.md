# FreeDarkStudio — plano de adaptação e distribuição gratuita

> Missão (Rafael, 2026-10-06): **adaptar** este projeto (alterações a definir),
> **distribuir de graça como FreeDarkStudio**.
> Origem: cópia local `ProgramasDYU/MoneyPrinterTurbo-Extended`
> (fork https://github.com/Asad-Ismail/MoneyPrinterTurbo-Extended, v1.2.6)
> do MoneyPrinterTurbo original (huoju/MoneyPrinterTurbo).

## Gate de licença — LIBERADO (verificado 2026-10-06)

- **MIT License**, Copyright (c) 2024 Harry — dá pra usar, modificar,
  distribuir e vender de graça.
- O `M LICENSE` no git era **só CRLF** (conteúdo idêntico ao original) —
  nada de licença adulterada.
- **Obrigação da MIT**: manter o aviso de copyright e a licença em toda
  cópia → **nunca apagar o `LICENSE`** + creditar no README
  ("Baseado em MoneyPrinterTurbo (MIT), de Harry, e no fork
  MoneyPrinterTurbo-Extended, de Asad-Ismail").

## Checklist ANTES de distribuir

- [x] **Vibe (arte do Rafael, `freedarkstudio.png`)**: tema freedark na vibe
      da arte — preto `#0a0a0c`, vermelho neon `#ff2b2b` dominante, branco,
      verde de apoio `#22c55e`; CSS neon (botões/sidebar/títulos) injetado no
      `streamlit_style`; logo oficial virou ícone do menu e imagem do projeto.
      Screenshot da tela real: título FreeDarkStudio + vibe ok.
- [x] **Rastros do programa antigo FORA** (pedido do Rafael): varredura final
      0 ocorrências de harry0703/MoneyPrinter em py/md/toml/html/json
      (fora LICENSE — obrigação MIT — e este ADAPTACOES que documenta a
      origem). Menu "Report a bug", URLs do About/FAQ/README removidos.
- [x] **Motor de narração Supertonic3 integrado**: seletor TTS ganhou
      "Supertonic3 (local, CPU)", 10 vozes **com nome de pessoa**
      (Maria/Ana/Clara/Beatriz/Helena · João/Ricardo/José/Pedro/Carlos);
      branch `supertonic_tts` provado (rc=0, WAV 5,3 s em 3 s de CPU);
      legendas rodam via whisper (transcrição). Engine vem do BBS por path
      fixo (`FREEDARK_SUPERTONIC_ENGINE`/`_SUPERTONIC_ENGINE_DIR`) — para
      distribuir: empacotar supertonic3 (venv+onnx) ou deixar opcional.
- [x] **Crash do watcher corrigido**: faltava `torchvision` (transformers
      puxou) → `uv pip install torchvision` rc=0 (0.29.1+cu130 com torch
      2.14.1 intacto); 1º boot também exigiu `~/.streamlit/credentials.toml`.
- [x] **Imagens extras**: usar o **navegador flow** (orientação do Rafael).
- [x] **Rebrand**: feito 2026-10-06 — 22 arquivos no total, `page_title`/
      `st.title`/`project_name` → FreeDarkStudio (py_compile rc=0).
      Mantidas só as URLs do upstream (crédito + link funcional) e o
      `LICENSE` (obrigação MIT).
- [x] **Temas**: dark · light · **freedark** (preto `#0b0b0d`, branco
      `#f8fafc`, vermelho `#3a1114`, verde `#22c55e`) em
      `.streamlit/themes/*.toml`; seletor no lançador
      (`./iniciar_freedarkstudio.sh [dark|light|freedark]`, padrão freedark).
- [x] **Formatos de vídeo**: 9:16 (1080×1920) e 16:9 (1920×1080) — já
      existiam (`VideoAspect` + seletor "Video Ratio" no webui).
- [x] **Mídia local do PC**: já existia — fonte "Local file" com upload de
      mp4/mov/avi/flv/mkv **e** jpg/jpeg/png → `storage/local_videos`.
- [x] **Sanear `config.toml`** — feito 2026-10-07: `pexels_api_keys`,
      `pollinations_api_key` e `gemini_api_key` zerados (grep de varredura
      rc=1 = nenhuma das 3 chaves sobrou em config/README/example).
      Backup do config com as chaves: `~/.freedarkstudio/config.com-chaves.toml`
      (fora do projeto — não distribuir). Distribuir só `config.example.toml`.
- [ ] Limpar a cópia de distribuição: `venv/` antigo do **Windows**
      (venv\Scripts), `teste.mp3`, saídas de `storage/`, `.git` se for
      empacotar como ZIP.
- [x] README rebrand feito (8 ocorrências FreeDarkStudio).
- [ ] Empacotar: instalação para iniciantes (venv + requirements) — mesma
      receita que funcionou aqui (Python 3.12 + `uv pip install -r`).
- [x] **Alterações de produto do Rafael (2026-10-07)**:
      1 vídeo só (seletor de nº de vídeos removido) · motor de fala **só
      Supertonic3** (Azure/Edge/SiliconFlow/Chatterbox tirados do seletor) ·
      upload de **vídeo+imagem do PC** na fonte local · upload de **música
      de fundo** (mp3/wav/m4a/ogg/flac/aac) · marca V0.6 no topo com estilo
      neon (Free verde · Dark branco-em-preto e inverso no light · Studio
      vermelho · glow) · vozes com nome de pessoa · temas dark/light/freedark.
- [x] **Legendas sem Edge**: `subtitle_provider = "whisper"` + `model_size =
      "small"` (modelo já em cache HF, int8/CPU) — prova rc=0 gerando SRT.
      PyAV 19 quebrou o faster-whisper 1.1.0 (`metadata_errors`) → fixado
      `av==14.2.0` no requirements (rc=0).

## Imagens da marca (2026-10-07)

- `resource/brand/hero_banner.jpg` — arte oficial como banner no topo da UI.
- `resource/brand/logo_side.png` — logo na sidebar.
- `resource/brand/menu_icon.gif` — GIF neon animado (F no losango) que
  **substitui o "⋮" do Streamlit** no canto superior direito (descaracteriza);
  o botão Deploy continua escondido e o ícone do navegador virou ✨.
- Fonte: `/home/rafael/Downloads/freedarkstudio.png` (arte do Rafael; se
  precisar de mais, usar o navegador flow).

## O que já está feito (2026-10-06)

- Renomeado de `MoneyPrinterTurbo-Extended` para **`freedarkstudio`** (rc=0).
- Instalado no Linux: `.venv` Python 3.12.14 + `uv pip install -r
  requirements.txt` (rc=0) — streamlit 1.45/moviepy/fastapi/faster-whisper ok.
- Webui no ar provada: **HTTP 200** em `http://localhost:8501`
  (launcher `iniciar_freedarkstudio.sh`; primeira execução exigiu
  `~/.streamlit/credentials.toml` vazio — já criado).
- Ícone no menu: `~/.local/share/applications/freedarkstudio.desktop`
  (`desktop-file-validate` rc=0) + `freedarkstudio.svg` (xmllint rc=0).
- Aviso conhecido: `Chatterbox TTS` **não instalado** (opcional, degrada
  com aviso; voz padrão via edge-tts funciona).

## Pedido do Rafael (07/10): fontes, pasta local e linha do tempo

- **Fonte do vídeo = só 3 opções**: `Arquivo local`, `Pexels`, `Pixabay`
  (TikTok/Douyin, Bilibili e Xiaohongshu removidos; o índice salvo no config
  cai para `local` se apontar fonte que já não existe). Provado no DOM:
  dropdown com exatamente essas 3 opções.
- **Pasta de origem no modo local**: campo "Pasta de vídeos/imagens" + botão
  **"Carregar pasta"** varre o diretório do PC (MP4/MOV/AVI/FLV/MKV/JPG/JPEG/PNG,
  teto 300 arquivos) e adiciona os arquivos **sem copiar**; o caminho fica salvo
  em `local_media_folder` no config.toml.
- **Linha do tempo**: cards numerados com miniatura (imagens), tipo e duração
  (lida via PyAV), setas **▲▼** para reordenar, **✕** para remover e botão
  "Limpar linha do tempo". A ordem vira a ordem dos clipes no vídeo (modo
  **Sequential**), e no modo local o Video Concat Mode agora já começa em
  Sequential. Provado na tela: carga da pasta brand (GIF ignorado), reorder
  (logo_header foi p/ posição 1), limpar e guard de lista vazia.
- **Tema de pesquisa** (Pexels/Pixabay): campo novo em "Configurações do
  Vídeo" que sobrescreve as palavras-chave quando preenchido; caption orienta
  que a chave da API fica em Basic Settings → Video Source Settings. Provado:
  com Pexels e sem chave, "Gerar Vídeo" cai em "Por favor, insira a Chave da
  API do Pexels" (nada é gerado).
- Guard: gerar com linha do tempo vazia → erro "Envie arquivos ou carregue uma
  pasta..." + `st.stop()` (provado na tela).
- Ajustes: `help=` no botão ✕ duplicava o botão no DOM (Streamlit 1.45) —
  removido; upload removido da timeline agora pode ser reenviado (dedupe limpa
  o `file_id` ao remover).
- Arquivos: `webui/Main.py` (helpers `fds_*`, fontes, pasta, timeline, tema).
  Compilação `py_compile` rc=0; webui reiniciado (HTTP 200) e validado na UI.

## Rodada 07/10 (tarde): PT total, sem rastro do MoneyPrinter, LLM moderno

- **Tudo em português**: `webui/i18n/pt.json` reescrito (138 linhas) — todos os
  valores em pt-BR, com wording próprio do FreeDarkStudio (varredura: 0 chaves
  com "money/printer/tiktok/bilibili/xiaohongshu/douyin"). Textos fixos do
  `Main.py` também traduzidos (About do menu, rótulos dos widgets, toasts e
  erros). Textos internos do Streamlit ("Drag and drop…", "Browse files",
  "Deploy") cobertos por CSS — verificado no DOM: o botão do uploader tem
  font-size 0 e mostra só "Escolher arquivos"; Deploy escondido.
- **Campo "Tema de pesquisa" sempre visível** na coluna Mídia e Montagem (não
  só em Pexels/Pixabay); quando preenchido sobrescreve as palavras-chave.
- **Carga de mídia unificada**: sumiu o botão "Carregar pasta" — a pasta é
  varrida automaticamente ao digitar o caminho + Enter (varredura por rerun,
  pois `on_change` não dispara quando o valor não muda); sobra **1 único**
  uploader (validado: `stFileUploader` count = 1 na página).
- **Gemini atualizado**: modelo padrão `gemini-3.8-flash` (+ dicas em PT com
  `gemini-3.5-flash`/`3.5-flash-lite`/`3.1-flash-lite`/`3.1-pro-preview`; o
  antigo `gemini-1.0-pro` foi desligado pelo Google).
- **Provedor genérico LLM**: opção "Genérico — NVIDIA / Groq / OpenRouter" na
  UI, usando o caminho OpenAI-compatível já existente no `llm.py`
  (base_url/chave/modelo); dicas com os 3 base_url e nomes de modelo de cada
  serviço. `config.example.toml` atualizado.
- **Chave Pexels (pedido do Rafael p/ teste)**: testada via API em 07/10 →
  **HTTP 401 "Invalid API key"** — a chave `AQ.Ab8RN6J…` não é válida no
  Pexels; não gravada no config. Pendente chave válida (pexels.com → API
  Key) para provar o download de vídeo.
- Verificação da rodada: `py_compile` rc=0; import de todos os módulos do
  webui rc=0; UI aberta no navegador: campo Tema de pesquisa + Pasta + linha
  do tempo presentes, fontes = Local/Pexels/Pixabay, labels todos em PT.

## Rodada 07/10 (noite): design premium + rótulos de 1 linha

- **Sistema de botões nas 3 cores** (`kind` do Streamlit = hierarquia):
  - `primary` → **vermelho** (gradiente + glow, 60px, caixa alta): só o
    "🎬 CRIAR VÍDEO".
  - `secondary` → **verde** (52px, borda 2px): ações de IA (✨ Escrever
    roteiro / ✨ Só palavras-chave) e "▶️ Ouvir a voz".
  - `tertiary` → **fantasma preto** (borda 2px vermelha): setas ▲▼, ✕ da
    linha do tempo e "Limpar linha do tempo".
  - Todos com `border-width:2px`, `min-height:52px`, raio 13px.
- **Ordem do card Roteiro trocada**: campos primeiro (Tema → Idioma →
  Roteiro → Palavras-chave), **ações de IA agrupadas embaixo** em 2 colunas.
  Como os botões agora ficam DEBAIXO dos text areas, o texto gerado entra via
  **pending + `st.rerun()`** (`fds_pending_script`/`fds_pending_terms` lidos no
  topo antes de os widgets existirem — setar depois daria erro do Streamlit).
- **"Ouvir a voz" movido para depois** de Volume/Velocidade — antes ele usava
  os valores do passo anterior (bug silencioso).
- **Campos sempre visíveis**: `input`/`textarea` com borda 2px vermelha + fundo
  preto + foco verde. O "quadrado invisível" (só aparecia ao clicar) acabou.
- **Cards**: moldura 2px, raio 18px, padding 28px, gradiente sutil; título em
  **caixa alta com barra verde à esquerda**.
- **Rótulos de 1 linha**: encurtei os que quebravam em 2–3 linhas e passei as
  explicações para o ícone `?` (`help=`) — 12 tooltips, **0 rótulos >36 chars**
  nos 27 campos (eram vários, ex. "Tema do vídeo (a IA usa isto…)" → "Tema do
  vídeo").
- **Banner do topo**: 716px → **145px** (`max-height:300px` + `object-fit:cover`
  + moldura vermelha) — parou de dominar a tela.
- **CTA com respiro**: `margin-top:18px` (estava 0, colado no card).
- Atenção: aumentar `gap` de `stHorizontalBlock` **quebra as 3 colunas e a
  timeline** (Streamlit usa largura %) — medições confirmaram, não fazer.
- Verificação: `py_compile` rc=0 · JSON rc=0 · DOM: 3 colunas lado a lado,
  0 rótulos longos, banner 145px, CTA 18px, bordas 2px. **Limitação**: a
  captura de frames do preview do Freebuff parou de funcionar nesta sessão
  (webview não compõe) — validação feita por medição no DOM, não por screenshot.

## Como subir

```bash
# pelo menu: ícone "FreeDarkStudio"
# ou direto:
"/run/media/rafael/Novo volume/ProgramasDYU/freedarkstudio/iniciar_freedarkstudio.sh"
# → http://localhost:8501  (rede: http://192.168.1.13:8501)
```
