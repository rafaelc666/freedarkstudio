import base64
import os
import platform
import sys
from uuid import uuid4
import streamlit as st
from loguru import logger


# Add the root directory of the project to the system path to allow importing modules from the project
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)
    print("******** sys.path ********")
    print(sys.path)
    print("")

from app.config import config
from app.models.schema import (
    MaterialInfo,
    VideoAspect,
    VideoConcatMode,
    VideoParams,
    VideoTransitionMode,
)
from app.services import llm, voice
from app.services import task as tm
from app.utils import utils

st.set_page_config(
    page_title="FreeDarkStudio",
    page_icon="\u2728",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": "# FreeDarkStudio V0.6\nEstúdio local de criação de vídeos curtos: "
        "dê um tema, escolha os clipes (pasta do PC, Pexels ou Pixabay) e monte o vídeo "
        "com narração Supertonic3, legendas automáticas e trilha. Gratuito e código "
        "aberto (MIT).",
    },
)


streamlit_style = """
<style>
h1 {
    padding-top: 0 !important;
}

/* ════ FreeDarkStudio premium — 3 cores: preto base, vermelho ação, verde apoio ════ */

/* ── Botões: hierarquia por tipo (primary=vermelho, secondary=verde, tertiary=ghost) ── */
.stButton>button { border-radius:10px; font-weight:600; letter-spacing:.02em;
                   transition:transform .16s ease, box-shadow .2s ease, background .2s ease, border-color .2s ease; }
/* vermelho = ação principal (Gerar vídeo) */
.stButton>button[kind="primary"] {
    background:linear-gradient(135deg,#ff3b3b 0%,#c81e1e 100%) !important;
    border:2px solid #ff6a6a !important; color:#fff !important;
    box-shadow:0 0 18px rgba(255,43,43,.45), inset 0 1px 0 rgba(255,255,255,.25) !important;
    text-shadow:0 1px 2px rgba(0,0,0,.45); }
.stButton>button[kind="primary"]:hover:not(:disabled) {
    transform:translateY(-1px);
    box-shadow:0 0 28px rgba(255,43,43,.8), inset 0 1px 0 rgba(255,255,255,.35) !important;
    border-color:#ffb3b3 !important; }
/* verde = ações de IA / apoio */
.stButton>button[kind="secondary"] {
    background:rgba(34,197,94,.10) !important;
    border:2px solid rgba(34,197,94,.65) !important; color:#b9f6cd !important;
    box-shadow:0 0 10px rgba(34,197,94,.18); }
.stButton>button[kind="secondary"]:hover:not(:disabled) {
    background:rgba(34,197,94,.24) !important; border-color:#22c55e !important; color:#eafff2 !important;
    box-shadow:0 0 20px rgba(34,197,94,.55); transform:translateY(-1px); }
/* preto fantasma = controles da linha do tempo e utilitários */
.stButton>button[kind="tertiary"] {
    background:rgba(10,10,12,.65) !important;
    border:2px solid rgba(255,43,43,.35) !important; color:#d8d8dc !important; }
.stButton>button[kind="tertiary"]:hover:not(:disabled) {
    background:rgba(255,43,43,.14) !important; border-color:#ff2b2b !important; color:#fff !important;
    box-shadow:0 0 12px rgba(255,43,43,.5); }
.stButton>button:disabled { opacity:.32 !important; box-shadow:none !important; }
.stButton>button:focus-visible { outline:none !important;
    box-shadow:0 0 0 2px #0a0a0c, 0 0 0 4px #22c55e !important; }

/* ── Campos de texto SEMPRE visíveis (caixa com borda, nunca invisível) ── */
[data-baseweb="input"], [data-baseweb="textarea"] {
    background:rgba(10,10,12,.78) !important;
    border:1px solid rgba(255,43,43,.55) !important; border-radius:10px !important;
    transition:border-color .18s ease, box-shadow .18s ease; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
    border-color:#22c55e !important; box-shadow:0 0 14px rgba(34,197,94,.45) !important; }
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color:#f5f5f5 !important; caret-color:#22c55e; }
[data-baseweb="input"] input::placeholder, [data-baseweb="textarea"] textarea::placeholder { color:#96777d !important; }

/* ── Cards (containers com borda) com moldura neon ── */
[data-testid="stContainer"] { border:1px solid rgba(255,43,43,.32) !important;
    border-radius:14px !important; background:rgba(255,255,255,.022) !important;
    box-shadow:0 0 22px rgba(255,43,43,.10); }
/* título dos cards: caixa alta, tracking, barra verde à esquerda */
[data-testid="stContainer"] [data-testid="stMarkdownContainer"]:first-of-type > p > strong {
    font-size:1.02rem; letter-spacing:.12em; text-transform:uppercase; color:#fff;
    border-left:3px solid #22c55e; padding-left:9px;
    text-shadow:0 0 10px rgba(34,197,94,.45); }
[data-testid="stSidebar"] { background:#0d0507; border-right:1px solid rgba(255,43,43,.35); }
[data-testid="stHeader"], [data-testid="stToolbar"] { background:rgba(10,10,12,.72); }
h1, h2, h3 { text-shadow:0 0 12px rgba(255,43,43,.35); }
[data-testid="stExpander"] { border:1px solid rgba(255,43,43,.30); }
[data-testid="stSuccess"] { color:#22c55e; border-color:#22c55e; }
div[data-testid="stMetricValue"] { color:#22c55e; }

/* ── Marca FreeDarkStudio (neon) ── */
.fds-brand { display:inline-flex; gap:8px; align-items:baseline; margin:.2rem 0 .6rem; line-height:1.1; }
.fds-brand > span { font-size:2.9rem; font-weight:800; letter-spacing:.01em; }
.fds-free { color:#22c55e; text-shadow:0 0 6px rgba(34,197,94,.95), 0 0 18px rgba(34,197,94,.6), 0 0 38px rgba(34,197,94,.35); }
.fds-dark { color:var(--text-color); background:var(--background-color); padding:0 10px; border-radius:8px;
            border:1px solid rgba(255,43,43,.40); box-shadow:0 0 14px rgba(255,43,43,.25);
            text-shadow:0 0 8px rgba(255,255,255,.35); }
.fds-studio { color:#ff2b2b; text-shadow:0 0 6px rgba(255,43,43,.95), 0 0 20px rgba(255,43,43,.65), 0 0 44px rgba(255,43,43,.4); }
.fds-ver { font-size:1.05rem !important; font-weight:600; color:#9aa0a6; letter-spacing:.14em; align-self:flex-start; margin-left:6px; }
/* ── Ícones do topo (direita) no tema ── */
[data-testid="stAppDeployButton"] { display:none !important; }
header [data-testid="stAppDeployButton"] { display:none !important; }

/* ── uploader 100% em português (textos internos do Streamlit) ── */
[data-testid="stFileUploaderDropzoneInstructions"] > div > span { display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > small { display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
    content:"Arraste e solte os arquivos aqui"; display:block; font-weight:600;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div::after {
    content:"Limite de 200MB por arquivo · MP4, MOV, AVI, FLV, MKV, JPG, JPEG, PNG";
    display:block; font-size:.72rem; opacity:.75; margin-top:2px;
}
[data-testid="stFileUploaderDropzone"] > button { font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] > button::after { content:"Escolher arquivos"; font-size:.85rem; }
#MainMenu button { background:rgba(255,43,43,.10)!important; border:1px solid rgba(255,43,43,.55)!important;
                   border-radius:8px!important; box-shadow:0 0 8px rgba(255,43,43,.30); }
#MainMenu svg { fill:#ff2b2b!important; }
[data-testid="stToolbar"] { background:transparent!important; }

/* ── Verde de apoio nas outras partes da tela ── */
a { color:#22c55e !important; }
a:hover { text-shadow:0 0 10px rgba(34,197,94,.6); }
hr { border-color:rgba(34,197,94,.35); }
/* checkbox marcada em verde */
[data-testid="stCheckbox"] label > div[data-checked="true"],
[data-testid="stCheckbox"] input:checked + span { background:#22c55e !important; border-color:#22c55e !important; }
[data-testid="stCheckbox"] svg { stroke:#0a0a0c !important; }
/* slider com thumb neon verde */
[data-testid="stSlider"] [role="slider"] { border:2px solid #22c55e !important; background:#0d0507 !important;
    box-shadow:0 0 12px rgba(34,197,94,.55) !important; }
/* selects com borda esverdeada (hover/foco) */
[data-testid="stSelectbox"] > div > div { border:1px solid rgba(34,197,94,.30); }
[data-testid="stSelectbox"] > div > div:hover { border-color:#22c55e; box-shadow:0 0 10px rgba(34,197,94,.35); }
/* uploader de arquivo (vídeo/imagem/música) com traço verde */
[data-testid="stFileUploaderDropzone"] { border:1px dashed rgba(34,197,94,.55) !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color:#22c55e !important; box-shadow:0 0 12px rgba(34,197,94,.30); }
/* expander: ícone e título ganham verde no hover */
[data-testid="stExpander"] summary:hover { color:#22c55e; }
/* sidebar: item ativo/links em verde */
[data-testid="stSidebar"] a, [data-testid="stSidebar"] p { color:#c9f2d9; }
[data-testid="stSidebar"] [data-testid="stDecoration"] { background-image:none; }
/* caption/instruções em verde-claro */
[data-testid="stCaptionContainer"], small { color:#7dd3a0 !important; }

/* ══════════ Rodada 2 — definição pesada: bordas grossas, botões grandes, respiro ══════════ */

/* ── Cards: moldura 2px, cantos largos, muito ar dentro ── */
[data-testid="stVerticalBlockBorderWrapper"].st-emotion-cache-gc283c {
    border:2px solid rgba(255,43,43,.50) !important;
    border-radius:18px !important;
    padding:28px 26px !important;
    background:linear-gradient(180deg, rgba(255,43,43,.055) 0%, rgba(255,255,255,.015) 45%, rgba(34,197,94,.03) 100%) !important;
    box-shadow:0 0 28px rgba(255,43,43,.16), inset 0 0 0 1px rgba(255,255,255,.04) !important;
}
[data-testid="stVerticalBlockBorderWrapper"].st-emotion-cache-gc283c [data-testid="stVerticalBlock"] { gap:24px !important; }

/* ── Título de cada card: maior, grosso, caixa alta com barra verde ── */
[data-testid="stVerticalBlockBorderWrapper"].st-emotion-cache-gc283c [data-testid="stMarkdownContainer"] > p > strong {
    font-size:1.18rem !important; font-weight:800 !important; letter-spacing:.14em !important;
    text-transform:uppercase !important; color:#ffffff !important;
    border-left:4px solid #22c55e !important; padding-left:12px !important;
    display:inline-block !important; line-height:1.3 !important;
    text-shadow:0 0 12px rgba(34,197,94,.55) !important; }

/* ── Botões GRANDES e bem definidos: 2px, altos, título forte ── */
.stButton>button {
    min-height:52px !important;
    padding:10px 24px !important;
    font-size:1.03rem !important; font-weight:800 !important;
    border-width:2px !important; border-radius:13px !important;
    line-height:1.3 !important; white-space:normal !important;
    letter-spacing:.03em; }
.stButton>button[kind="primary"] {
    min-height:60px !important; font-size:1.2rem !important;
    text-transform:uppercase !important; letter-spacing:.09em !important;
    background:linear-gradient(135deg,#ff3b3b 0%,#c81e1e 60%,#8f0f0f 100%) !important;
    border-color:#ff8a8a !important;
    box-shadow:0 0 26px rgba(255,43,43,.55), inset 0 2px 0 rgba(255,255,255,.28) !important; }
.stButton>button[kind="primary"]:hover:not(:disabled) {
    box-shadow:0 0 40px rgba(255,43,43,.95), inset 0 2px 0 rgba(255,255,255,.4) !important;
    transform:translateY(-2px); }
.stButton>button[kind="secondary"] {
    background:linear-gradient(180deg, rgba(34,197,94,.18), rgba(34,197,94,.06)) !important;
    border-color:#22c55e !important; color:#eafff2 !important;
    box-shadow:0 0 14px rgba(34,197,94,.28), inset 0 1px 0 rgba(255,255,255,.10) !important; }
.stButton>button[kind="secondary"]:hover:not(:disabled) {
    background:linear-gradient(180deg, rgba(34,197,94,.34), rgba(34,197,94,.14)) !important;
    box-shadow:0 0 26px rgba(34,197,94,.7) !important; transform:translateY(-2px); }
.stButton>button[kind="tertiary"] {
    min-height:48px !important; font-size:1.1rem !important;
    background:rgba(10,10,12,.75) !important;
    border-color:rgba(255,43,43,.55) !important; color:#ffd9d9 !important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.05) !important; }
.stButton>button[kind="tertiary"]:hover:not(:disabled) {
    background:rgba(255,43,43,.20) !important; border-color:#ff2b2b !important; color:#fff !important;
    box-shadow:0 0 18px rgba(255,43,43,.7) !important; }

/* ── Campos: borda 2px, altura generosa, texto maior ── */
[data-baseweb="input"], [data-baseweb="textarea"] {
    border-width:2px !important; border-radius:12px !important;
    min-height:50px; background:rgba(10,10,12,.85) !important; }
[data-baseweb="textarea"] { min-height:160px; }
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    font-size:1.05rem !important; padding:14px 16px !important; min-height:46px; }
[data-baseweb="textarea"] textarea { min-height:150px; }

/* ── Selects: borda 2px e altura maior ── */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    border:2px solid rgba(34,197,94,.45) !important; border-radius:12px !important;
    min-height:50px !important; font-size:1.02rem !important; background:rgba(10,10,12,.85) !important; }
[data-testid="stSelectbox"] > div > div:hover,
[data-baseweb="select"] > div:hover { border-color:#22c55e !important;
    box-shadow:0 0 16px rgba(34,197,94,.45) !important; }

/* ── Rótulos: maiores e em negrito ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    font-size:1.02rem !important; font-weight:700 !important; color:#f0f2f3 !important;
    margin-bottom:2px !important; }

/* ── Espaço entre blocos (colunas do Streamlit usam % — NÃO aumentar gap
   aqui, senão as 3 colunas e a timeline quebram linha) ── */
[data-testid="stVerticalBlock"] { gap:20px !important; }
/* respiro entre os 3 cards principais, sem mexer nas colunas da timeline */
[data-testid="stColumn"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"].st-emotion-cache-gc283c) {
    padding:0 10px !important; }

/* ── Expander mais imponente ── */
[data-testid="stExpander"] { border:2px solid rgba(255,43,43,.45) !important;
    border-radius:14px !important; background:rgba(255,43,43,.05) !important; }
[data-testid="stExpander"] summary { font-size:1.05rem !important; font-weight:800 !important; letter-spacing:.05em; }

/* ── Banner do topo: enxuto, não domina a tela ── */
[data-testid="stImage"] img { max-height:300px !important; object-fit:cover !important;
    border-radius:14px !important; border:2px solid rgba(255,43,43,.45) !important;
    box-shadow:0 0 24px rgba(255,43,43,.20); }

/* ── Botão principal: respiro em cima ── */
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child { margin-top:18px !important; }

/* ── Rótulo colado no campo ── */
[data-testid="stWidgetLabel"] { margin-bottom:10px !important; }

/* ════ Rodada 3 — ajustes finos (pedido do Rafael 09/10) ════ */

/* ── Setas da timeline (▲▼✕): padding enxuto p/ não esbarrarem entre si ── */
.stButton>button[kind="tertiary"] { padding:10px 14px !important; }

/* ── Sidebar da esquerda removida: sem rail, sem seta, mais largura útil ── */
[data-testid="stSidebar"] { display:none !important; }
</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

# ── Ícone neon no lugar do menu "⋮" (descaracteriza o Streamlit) ──
try:
    with open(os.path.join(root_dir, "resource", "brand", "menu_icon.gif"), "rb") as _f:
        _menu_b64 = base64.b64encode(_f.read()).decode()
    st.markdown(
        f"""<style>
        #MainMenu button {{
            background: transparent url(data:image/gif;base64,{_menu_b64}) center/24px 24px no-repeat !important;
            width: 34px !important; height: 34px !important; border-radius: 9px !important;
        }}
        #MainMenu svg {{ display: none !important; }}
        #MainMenu button:hover {{ box-shadow: 0 0 14px rgba(34,197,94,.55) !important; border-color: #22c55e !important; }}
        </style>""",
        unsafe_allow_html=True,
    )
except Exception:
    pass

# 定义资源目录
font_dir = os.path.join(root_dir, "resource", "fonts")
song_dir = os.path.join(root_dir, "resource", "songs")
i18n_dir = os.path.join(root_dir, "webui", "i18n")
config_file = os.path.join(root_dir, "webui", ".streamlit", "webui.toml")
system_locale = utils.get_system_locale()


if "video_subject" not in st.session_state:
    st.session_state["video_subject"] = ""
if "video_script" not in st.session_state:
    st.session_state["video_script"] = ""
if "video_terms" not in st.session_state:
    st.session_state["video_terms"] = ""
# ── Textos gerados pela IA entram nos campos via pending (botões ficam DEBAIXO
# dos text areas; setar depois da criação do widget daria erro no Streamlit) ──
st.session_state.setdefault("fds_script_area", st.session_state.get("video_script", ""))
st.session_state.setdefault("fds_terms_area", st.session_state.get("video_terms", ""))
if "fds_pending_script" in st.session_state:
    st.session_state["fds_script_area"] = st.session_state.pop("fds_pending_script")
if "fds_pending_terms" in st.session_state:
    st.session_state["fds_terms_area"] = st.session_state.pop("fds_pending_terms")
if "ui_language" not in st.session_state:
    st.session_state["ui_language"] = config.ui.get("language", system_locale)

# 加载语言文件
locales = utils.load_locales(i18n_dir)

# 创建一个顶部栏，包含标题和语言选择
title_col, lang_col = st.columns([3, 1])

with title_col:
    st.markdown(
        '<div class="fds-brand">'
        '<span class="fds-free">Free</span>'
        '<span class="fds-dark">Dark</span>'
        '<span class="fds-studio">Studio</span>'
        f'<span class="fds-ver">V{config.project_version}</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Imagens da marca: banner hero + logo na sidebar ──
try:
    _hero = os.path.join(root_dir, "resource", "brand", "hero_banner.jpg")
    if os.path.isfile(_hero):
        st.image(_hero, use_container_width=True)
    # Sidebar removida (pedido do Rafael 09/10): o logo já aparece no banner
    # e na timeline; o rail da esquerda só ocupava espaço.
except Exception:
    pass

with lang_col:
    display_languages = []
    selected_index = 0
    for i, code in enumerate(locales.keys()):
        display_languages.append(f"{code} - {locales[code].get('Language')}")
        if code == st.session_state.get("ui_language", ""):
            selected_index = i

    selected_language = st.selectbox(
        "Idioma",
        options=display_languages,
        index=selected_index,
        key="top_language_selector",
        label_visibility="collapsed",
    )
    if selected_language:
        code = selected_language.split(" - ")[0].strip()
        st.session_state["ui_language"] = code
        config.ui["language"] = code

support_locales = [
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "de-DE",
    "en-US",
    "fr-FR",
    "vi-VN",
    "th-TH",
]


def get_all_fonts():
    fonts = []
    for root, dirs, files in os.walk(font_dir):
        for file in files:
            if file.endswith(".ttf") or file.endswith(".ttc"):
                fonts.append(file)
    fonts.sort()
    return fonts


def get_all_songs():
    songs = []
    for root, dirs, files in os.walk(song_dir):
        for file in files:
            if file.endswith(".mp3"):
                songs.append(file)
    return songs


def open_task_folder(task_id):
    try:
        sys = platform.system()
        path = os.path.join(root_dir, "storage", "tasks", task_id)
        if os.path.exists(path):
            if sys == "Windows":
                os.system(f"start {path}")
            if sys == "Darwin":
                os.system(f"open {path}")
    except Exception as e:
        logger.error(e)


def scroll_to_bottom():
    js = """
    <script>
        console.log("scroll_to_bottom");
        function scroll(dummy_var_to_force_repeat_execution){
            var sections = parent.document.querySelectorAll('section.main');
            console.log(sections);
            for(let index = 0; index<sections.length; index++) {
                sections[index].scrollTop = sections[index].scrollHeight;
            }
        }
        scroll(1);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)


def init_log():
    logger.remove()
    _lvl = "DEBUG"

    def format_record(record):
        # 获取日志记录中的文件全路径
        file_path = record["file"].path
        # 将绝对路径转换为相对于项目根目录的路径
        relative_path = os.path.relpath(file_path, root_dir)
        # 更新记录中的文件路径
        record["file"].path = f"./{relative_path}"
        # 返回修改后的格式字符串
        # 您可以根据需要调整这里的格式
        record["message"] = record["message"].replace(root_dir, ".")

        _format = (
            "<green>{time:%Y-%m-%d %H:%M:%S}</> | "
            + "<level>{level}</> | "
            + '"{file.path}:{line}":<blue> {function}</> '
            + "- <level>{message}</>"
            + "\n"
        )
        return _format

    logger.add(
        sys.stdout,
        level=_lvl,
        format=format_record,
        colorize=True,
    )


init_log()

locales = utils.load_locales(i18n_dir)


def tr(key):
    loc = locales.get(st.session_state["ui_language"], {})
    return loc.get("Translation", {}).get(key, key)


# 创建基础设置折叠框
if not config.app.get("hide_config", False):
    with st.expander(tr("Basic Settings"), expanded=False):
        config_panels = st.columns(3)
        left_config_panel = config_panels[0]
        middle_config_panel = config_panels[1]
        right_config_panel = config_panels[2]

        # 左侧面板 - 日志设置
        with left_config_panel:
            # 是否隐藏配置面板
            hide_config = st.checkbox(
                tr("Hide Basic Settings"), value=config.app.get("hide_config", False)
            )
            config.app["hide_config"] = hide_config

            # 是否禁用日志显示
            hide_log = st.checkbox(
                tr("Hide Log"), value=config.ui.get("hide_log", False)
            )
            config.ui["hide_log"] = hide_log

        # 中间面板 - LLM 设置

        with middle_config_panel:
            st.write(tr("LLM Settings"))
            # (rótulo mostrado na tela, chave usada no config.toml)
            llm_providers = [
                ("OpenAI", "openai"),
                ("Moonshot", "moonshot"),
                ("Azure", "azure"),
                ("Qwen", "qwen"),
                ("DeepSeek", "deepseek"),
                ("Gemini (Google)", "gemini"),
                ("Ollama (local)", "ollama"),
                ("G4f", "g4f"),
                ("OneAPI", "oneapi"),
                ("Cloudflare", "cloudflare"),
                ("ERNIE", "ernie"),
                ("Pollinations", "pollinations"),
                ("Genérico — NVIDIA / Groq / OpenRouter", "generic"),
            ]
            provider_keys = [p[1] for p in llm_providers]
            saved_llm_provider = config.app.get("llm_provider", "openai").lower()
            if saved_llm_provider in provider_keys:
                saved_llm_provider_index = provider_keys.index(saved_llm_provider)
            else:
                saved_llm_provider_index = 0

            selected_provider_index = st.selectbox(
                tr("LLM Provider"),
                options=range(len(llm_providers)),
                index=saved_llm_provider_index,
                format_func=lambda x: llm_providers[x][0],
            )
            llm_helper = st.container()
            llm_provider = llm_providers[selected_provider_index][1]
            config.app["llm_provider"] = llm_provider

            llm_api_key = config.app.get(f"{llm_provider}_api_key", "")
            llm_secret_key = config.app.get(
                f"{llm_provider}_secret_key", ""
            )  # only for baidu ernie
            llm_base_url = config.app.get(f"{llm_provider}_base_url", "")
            llm_model_name = config.app.get(f"{llm_provider}_model_name", "")
            llm_account_id = config.app.get(f"{llm_provider}_account_id", "")

            tips = ""
            if llm_provider == "ollama":
                if not llm_model_name:
                    llm_model_name = "qwen:7b"
                if not llm_base_url:
                    llm_base_url = "http://localhost:11434/v1"

                with llm_helper:
                    tips = """
                            ##### Ollama配置说明
                            - **API Key**: 随便填写，比如 123
                            - **Base Url**: 一般为 http://localhost:11434/v1
                                - 如果 `FreeDarkStudio` 和 `Ollama` **不在同一台机器上**，需要填写 `Ollama` 机器的IP地址
                                - 如果 `FreeDarkStudio` 是 `Docker` 部署，建议填写 `http://host.docker.internal:11434/v1`
                            - **Model Name**: 使用 `ollama list` 查看，比如 `qwen:7b`
                            """

            if llm_provider == "openai":
                if not llm_model_name:
                    llm_model_name = "gpt-3.5-turbo"
                with llm_helper:
                    tips = """
                            ##### OpenAI 配置说明
                            > 需要VPN开启全局流量模式
                            - **API Key**: [点击到官网申请](https://platform.openai.com/api-keys)
                            - **Base Url**: 可以留空
                            - **Model Name**: 填写**有权限**的模型，[点击查看模型列表](https://platform.openai.com/settings/organization/limits)
                            """

            if llm_provider == "moonshot":
                if not llm_model_name:
                    llm_model_name = "moonshot-v1-8k"
                with llm_helper:
                    tips = """
                            ##### Moonshot 配置说明
                            - **API Key**: [点击到官网申请](https://platform.moonshot.cn/console/api-keys)
                            - **Base Url**: 固定为 https://api.moonshot.cn/v1
                            - **Model Name**: 比如 moonshot-v1-8k，[点击查看模型列表](https://platform.moonshot.cn/docs/intro#%E6%A8%A1%E5%9E%8B%E5%88%97%E8%A1%A8)
                            """
            if llm_provider == "oneapi":
                if not llm_model_name:
                    llm_model_name = (
                        "claude-3-5-sonnet-20240620"  # 默认模型，可以根据需要调整
                    )
                with llm_helper:
                    tips = """
                        ##### OneAPI 配置说明
                        - **API Key**: 填写您的 OneAPI 密钥
                        - **Base Url**: 填写 OneAPI 的基础 URL
                        - **Model Name**: 填写您要使用的模型名称，例如 claude-3-5-sonnet-20240620
                        """

            if llm_provider == "qwen":
                if not llm_model_name:
                    llm_model_name = "qwen-max"
                with llm_helper:
                    tips = """
                            ##### 通义千问Qwen 配置说明
                            - **API Key**: [点击到官网申请](https://dashscope.console.aliyun.com/apiKey)
                            - **Base Url**: 留空
                            - **Model Name**: 比如 qwen-max，[点击查看模型列表](https://help.aliyun.com/zh/dashscope/developer-reference/model-introduction#3ef6d0bcf91wy)
                            """

            if llm_provider == "g4f":
                if not llm_model_name:
                    llm_model_name = "gpt-3.5-turbo"
                with llm_helper:
                    tips = """
                            ##### gpt4free 配置说明
                            > [GitHub开源项目](https://github.com/xtekky/gpt4free)，可以免费使用GPT模型，但是**稳定性较差**
                            - **API Key**: 随便填写，比如 123
                            - **Base Url**: 留空
                            - **Model Name**: 比如 gpt-3.5-turbo，[点击查看模型列表](https://github.com/xtekky/gpt4free/blob/main/g4f/models.py#L308)
                            """
            if llm_provider == "azure":
                with llm_helper:
                    tips = """
                            ##### Azure 配置说明
                            > [点击查看如何部署模型](https://learn.microsoft.com/zh-cn/azure/ai-services/openai/how-to/create-resource)
                            - **API Key**: [点击到Azure后台创建](https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI)
                            - **Base Url**: 留空
                            - **Model Name**: 填写你实际的部署名
                            """

            if llm_provider == "gemini":
                if not llm_model_name:
                    llm_model_name = "gemini-3.8-flash"

                with llm_helper:
                    tips = """
                            ##### Configuração do Gemini (Google)
                            - **Chave da API**: peça em https://ai.google.dev/
                            - **URL Base**: deixe em branco
                            - **Nome do Modelo**: `gemini-3.8-flash` (recomendado),
                              `gemini-3.5-flash`, `gemini-3.5-flash-lite`,
                              `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`
                              — o antigo `gemini-1.0-pro` foi desligado pelo Google
                            """

            if llm_provider == "deepseek":
                if not llm_model_name:
                    llm_model_name = "deepseek-chat"
                if not llm_base_url:
                    llm_base_url = "https://api.deepseek.com"
                with llm_helper:
                    tips = """
                            ##### DeepSeek 配置说明
                            - **API Key**: [点击到官网申请](https://platform.deepseek.com/api_keys)
                            - **Base Url**: 固定为 https://api.deepseek.com
                            - **Model Name**: 固定为 deepseek-chat
                            """

            if llm_provider == "ernie":
                with llm_helper:
                    tips = """
                            ##### 百度文心一言 配置说明
                            - **API Key**: [点击到官网申请](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
                            - **Secret Key**: [点击到官网申请](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
                            - **Base Url**: 填写 **请求地址** [点击查看文档](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/jlil56u11#%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)
                            """

            if llm_provider == "pollinations":
                if not llm_model_name:
                    llm_model_name = "default"
                with llm_helper:
                    tips = """
                            ##### Pollinations AI Configuration
                            - **API Key**: Optional - Leave empty for public access
                            - **Base Url**: Default is https://text.pollinations.ai/openai
                            - **Model Name**: Use 'openai-fast' or specify a model name
                            """

            if llm_provider == "generic":
                with llm_helper:
                    tips = """
                            ##### Provedor genérico (padrão OpenAI)
                            Funciona com NVIDIA, Groq, OpenRouter e qualquer serviço compatível — preencha os 3 campos:
                            - **Chave da API**: a chave do serviço escolhido
                            - **URL Base**:
                                - NVIDIA: `https://integrate.api.nvidia.com/v1`
                                - Groq: `https://api.groq.com/openai/v1`
                                - OpenRouter: `https://openrouter.ai/api/v1`
                            - **Nome do Modelo**: `meta/llama-3.3-70b-instruct` (NVIDIA),
                              `llama-3.3-70b-versatile` (Groq), `openai/gpt-4o-mini` (OpenRouter)
                            """

            if tips and (
                config.ui["language"] == "zh"
                or llm_provider in ("generic", "gemini")
            ):
                if config.ui["language"] == "zh":
                    st.warning(
                        "中国用户建议使用 **DeepSeek** 或 **Moonshot** 作为大模型提供商\n- 国内可直接访问，不需要VPN \n- 注册就送额度，基本够用"
                    )
                st.info(tips)

            st_llm_api_key = st.text_input(
                tr("API Key"), value=llm_api_key, type="password"
            )
            st_llm_base_url = st.text_input(tr("Base Url"), value=llm_base_url)
            st_llm_model_name = ""
            if llm_provider != "ernie":
                st_llm_model_name = st.text_input(
                    tr("Model Name"),
                    value=llm_model_name,
                    key=f"{llm_provider}_model_name_input",
                )
                if st_llm_model_name:
                    config.app[f"{llm_provider}_model_name"] = st_llm_model_name
            else:
                st_llm_model_name = None

            if st_llm_api_key:
                config.app[f"{llm_provider}_api_key"] = st_llm_api_key
            if st_llm_base_url:
                config.app[f"{llm_provider}_base_url"] = st_llm_base_url
            if st_llm_model_name:
                config.app[f"{llm_provider}_model_name"] = st_llm_model_name
            if llm_provider == "ernie":
                st_llm_secret_key = st.text_input(
                    tr("Secret Key"), value=llm_secret_key, type="password"
                )
                config.app[f"{llm_provider}_secret_key"] = st_llm_secret_key

            if llm_provider == "cloudflare":
                st_llm_account_id = st.text_input(
                    tr("Account ID"), value=llm_account_id
                )
                if st_llm_account_id:
                    config.app[f"{llm_provider}_account_id"] = st_llm_account_id

        # 右侧面板 - API 密钥设置
        with right_config_panel:

            def get_keys_from_config(cfg_key):
                api_keys = config.app.get(cfg_key, [])
                if isinstance(api_keys, str):
                    api_keys = [api_keys]
                api_key = ", ".join(api_keys)
                return api_key

            def save_keys_to_config(cfg_key, value):
                value = value.replace(" ", "")
                if value:
                    config.app[cfg_key] = value.split(",")

            st.write(tr("Video Source Settings"))

            pexels_api_key = get_keys_from_config("pexels_api_keys")
            pexels_api_key = st.text_input(
                tr("Pexels API Key"),
                value=pexels_api_key,
                type="password",
                help="Pegue em https://www.pexels.com/api/ — é grátis.",
            )
            save_keys_to_config("pexels_api_keys", pexels_api_key)

            pixabay_api_key = get_keys_from_config("pixabay_api_keys")
            pixabay_api_key = st.text_input(
                tr("Pixabay API Key"),
                value=pixabay_api_key,
                type="password",
                help="Pegue em https://pixabay.com/api/docs/ — é grátis.",
            )
            save_keys_to_config("pixabay_api_keys", pixabay_api_key)

llm_provider = config.app.get("llm_provider", "").lower()
panel = st.columns(3)
left_panel = panel[0]
middle_panel = panel[1]
right_panel = panel[2]

params = VideoParams(video_subject="")
uploaded_files = []

# ── FreeDarkStudio: mídias locais ──
FDS_MEDIA_EXTS = {".mp4", ".mov", ".avi", ".flv", ".mkv", ".jpg", ".jpeg", ".png"}
FDS_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".flv", ".mkv"}


def fds_materials():
    if "fds_local_materials" not in st.session_state:
        st.session_state["fds_local_materials"] = []
    return st.session_state["fds_local_materials"]


def fds_move(idx, delta):
    mats = fds_materials()
    j = idx + delta
    if 0 <= idx < len(mats) and 0 <= j < len(mats):
        mats[idx], mats[j] = mats[j], mats[idx]


def fds_remove(idx):
    mats = fds_materials()
    if 0 <= idx < len(mats):
        item = mats.pop(idx)
        # permite voltar a enviar/remover o mesmo upload depois (limpa o dedupe)
        fid = item.get("file_id")
        if fid and "fds_saved_ids" in st.session_state:
            st.session_state["fds_saved_ids"].discard(fid)


def fds_clear():
    st.session_state["fds_local_materials"] = []
    # marca a pasta como já varrida: sem isso a próxima execução reenche a timeline
    st.session_state["fds_loaded_folder"] = st.session_state.get("fds_local_folder", "")


@st.cache_data(show_spinner=False)
def fds_media_info(file_path):
    """(rótulo, duração em segundos ou None) de um arquivo local."""
    ext = os.path.splitext(file_path)[1].lower()
    kind = "vídeo" if ext in FDS_VIDEO_EXTS else "imagem"
    duration = None
    if kind == "vídeo":
        try:
            import av

            with av.open(file_path) as container:
                stream = next((s for s in container.streams if s.type == "video"), None)
                if stream is not None and stream.duration and stream.time_base:
                    duration = float(stream.duration * stream.time_base)
        except Exception:
            duration = None
    return kind, duration


def fds_add_folder(folder):
    """Adiciona à linha do tempo os mídias de uma pasta do PC. Retorna (n, erro)."""
    folder = (folder or "").strip()
    if not folder:
        return 0, "Digite o caminho de uma pasta primeiro."
    folder = os.path.abspath(os.path.expanduser(folder))
    if not os.path.isdir(folder):
        return 0, f"Pasta não encontrada: {folder}"
    mats = fds_materials()
    known = {m["path"] for m in mats}
    added = 0
    for nome in sorted(os.listdir(folder)):
        if added >= 300:
            return added, "Limite de 300 arquivos por pasta: só os 300 primeiros (por ordem alfabética) foram adicionados."
        caminho = os.path.join(folder, nome)
        if not os.path.isfile(caminho):
            continue
        if os.path.splitext(nome)[1].lower() not in FDS_MEDIA_EXTS:
            continue
        if caminho in known:
            continue
        mats.append({"path": caminho, "name": nome})
        known.add(caminho)
        added += 1
    return added, None


def fds_render_timeline():
    st.write("Linha do tempo")
    mats = fds_materials()
    if not mats:
        st.caption("Nenhum material ainda — envie arquivos ou carregue uma pasta.")
        return
    st.caption(
        "A ordem abaixo é a ordem dos clipes no vídeo final (modo **Sequential** do "
        "*Video Concat Mode*; **Random** embaralha)."
    )
    for i, m in enumerate(mats):
        kind, duration = fds_media_info(m["path"])
        c_num, c_thumb, c_info, c_up, c_down, c_del = st.columns(
            [0.5, 1.2, 6.4, 1.6, 1.6, 1.6]
        )
        c_num.markdown(f"**{i + 1}**")
        if kind == "imagem":
            c_thumb.image(m["path"], width=72)
        else:
            c_thumb.markdown("🎞️")
        detalhe = f"{kind} · {duration:.0f} s" if duration else kind
        c_info.caption(f"{m['name']} — {detalhe}")
        c_up.button(
            "▲",
            key=f"fds_up_{i}",
            disabled=(i == 0),
            on_click=fds_move,
            args=(i, -1),
            type="tertiary",
            use_container_width=True,
        )
        c_down.button(
            "▼",
            key=f"fds_down_{i}",
            disabled=(i == len(mats) - 1),
            on_click=fds_move,
            args=(i, 1),
            type="tertiary",
            use_container_width=True,
        )
        c_del.button(
            "✕",
            key=f"fds_del_{i}",
            on_click=fds_remove,
            args=(i,),
            type="tertiary",
            use_container_width=True,
        )
    st.button(
        "Limpar linha do tempo",
        key="fds_clear_timeline",
        on_click=fds_clear,
        type="tertiary",
    )


with left_panel:
    with st.container(border=True):
        st.write(tr("Video Script Settings"))
        params.video_subject = st.text_input(
            tr("Video Subject"),
            value=st.session_state["video_subject"],
            key="video_subject_input",
            help="A IA usa este tema para escrever o roteiro e as palavras-chave.",
        ).strip()

        video_languages = [
            (tr("Auto Detect"), ""),
        ]
        for code in support_locales:
            video_languages.append((code, code))

        selected_index = st.selectbox(
            tr("Script Language"),
            index=0,
            options=range(                len(video_languages)
            ),  # Use the index as the internal option value
            format_func=lambda x: video_languages[x][
                0
            ],  # The label is displayed to the user
        )
        params.video_language = video_languages[selected_index][1]

        params.video_script = st.text_area(
            tr("Video Script"),
            key="fds_script_area",
            height=280,
            help="Deixe em branco para a IA escrever. Pontuação ajuda na quebra das legendas.",
        )
        params.video_terms = st.text_area(
            tr("Video Keywords"),
            key="fds_terms_area",
            help="Opcional — vazio a IA gera. Separe por vírgula, em inglês.",
        )

        # Ações de IA agrupadas no fim do card (ordem nova — só nossas cores)
        ai_cols = st.columns(2)
        with ai_cols[0]:
            if st.button(
                tr("Generate Video Script and Keywords"),
                key="auto_generate_script",
                use_container_width=True,
            ):
                with st.spinner(tr("Generating Video Script and Keywords")):
                    script = llm.generate_script(
                        video_subject=params.video_subject,
                        language=params.video_language,
                    )
                    terms = llm.generate_terms(params.video_subject, script)
                    if "Error: " in script:
                        st.error(tr(script))
                    elif "Error: " in terms:
                        st.error(tr(terms))
                    else:
                        st.session_state["video_script"] = script
                        st.session_state["video_terms"] = ", ".join(terms)
                        st.session_state["fds_pending_script"] = script
                        st.session_state["fds_pending_terms"] = ", ".join(terms)
                        st.rerun()
        with ai_cols[1]:
            if st.button(
                tr("Generate Video Keywords"),
                key="auto_generate_terms",
                use_container_width=True,
            ):
                if not params.video_script:
                    st.error(tr("Please Enter the Video Subject"))
                else:
                    with st.spinner(tr("Generating Video Keywords")):
                        terms = llm.generate_terms(
                            params.video_subject, params.video_script
                        )
                        if "Error: " in terms:
                            st.error(tr(terms))
                        else:
                            st.session_state["video_terms"] = ", ".join(terms)
                            st.session_state["fds_pending_terms"] = ", ".join(terms)
                            st.rerun()

with middle_panel:
    with st.container(border=True):
        st.write(tr("Video Settings"))
        video_concat_modes = [
            (tr("Sequential"), "sequential"),
            (tr("Random"), "random"),
            (tr("Semantic Text Alignment"), "semantic"),
        ]
        video_sources = [
            (tr("Local file"), "local"),
            (tr("Pexels"), "pexels"),
            (tr("Pixabay"), "pixabay"),
        ]

        source_values = [v[1] for v in video_sources]
        saved_video_source_name = config.app.get("video_source", "local")
        saved_video_source_index = (
            source_values.index(saved_video_source_name)
            if saved_video_source_name in source_values
            else 0
        )

        selected_index = st.selectbox(
            tr("Video Source"),
            options=range(len(video_sources)),
            format_func=lambda x: video_sources[x][0],
            index=saved_video_source_index,
        )
        params.video_source = video_sources[selected_index][1]
        config.app["video_source"] = params.video_source

        search_theme = st.text_input(
            "Tema de pesquisa",
            key="fds_search_theme",
            help="Palavras em inglês separadas por vírgula, usadas para buscar os vídeos "
            "no Pexels/Pixabay. Deixe vazio para usar as Palavras-chave do Vídeo "
            "(painel da esquerda).",
        )
        if search_theme.strip():
            params.video_terms = search_theme.strip()
        if params.video_source in ("pexels", "pixabay"):
            fonte = "Pexels" if params.video_source == "pexels" else "Pixabay"
            st.caption(
                f"{fonte} é uma API online: informe a chave em "
                "**Configurações Básicas → Configurações da Fonte do Vídeo** "
                "(topo da página)."
            )
        else:
            st.caption(
                "Com **Arquivo local** a busca é ignorada: os clipes vêm da sua "
                "pasta e da linha do tempo abaixo."
            )

        if params.video_source == "local":
            st.caption(
                "Um único ponto de entrada: solte os arquivos na área grande abaixo ou "
                "informe uma pasta do PC e tecle Enter. A ordem se organiza na linha do "
                "tempo (setas ▲▼)."
            )

            local_folder = st.text_input(
                "Pasta de vídeos/imagens",
                value=config.app.get("local_media_folder", ""),
                key="fds_local_folder",
                help="Caminho de uma pasta deste computador, ex.: /home/rafael/videos. "
                "Digite o caminho e tecle Enter — os arquivos são lidos direto dela, sem copiar.",
            )
            config.app["local_media_folder"] = local_folder
            # varre a pasta automaticamente quando o caminho muda (ou na 1ª execução)
            if local_folder and st.session_state.get("fds_loaded_folder") != local_folder:
                added, erro = fds_add_folder(local_folder)
                st.session_state["fds_loaded_folder"] = local_folder
                if added:
                    st.toast(f"{added} arquivo(s) adicionado(s) à linha do tempo")
                if erro:
                    st.warning(erro)
                elif not added:
                    st.info(
                        "Nenhum arquivo novo (aceitos: MP4, MOV, AVI, FLV, MKV, JPG, JPEG, PNG)."
                    )

            uploaded_files = st.file_uploader(
                "Envie vídeos ou imagens do PC",
                type=["mp4", "mov", "avi", "flv", "mkv", "jpg", "jpeg", "png"],
                accept_multiple_files=True,
            )
            if uploaded_files:
                if "fds_saved_ids" not in st.session_state:
                    st.session_state["fds_saved_ids"] = set()
                saved_ids = st.session_state["fds_saved_ids"]
                mats = fds_materials()
                known = {m["path"] for m in mats}
                local_videos_dir = utils.storage_dir("local_videos", create=True)
                for file in uploaded_files:
                    if file.file_id in saved_ids:
                        continue
                    file_path = os.path.join(
                        local_videos_dir, f"{file.file_id}_{file.name}"
                    )
                    if file_path in known:
                        saved_ids.add(file.file_id)
                        continue
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_ids.add(file.file_id)
                    mats.append(
                        {"path": file_path, "name": file.name, "file_id": file.file_id}
                    )

        selected_index = st.selectbox(
            tr("Video Concat Mode"),
            index=0 if params.video_source == "local" else 1,
            options=range(
                len(video_concat_modes)
            ),  # Use the index as the internal option value
            format_func=lambda x: video_concat_modes[x][
                0
            ],  # The label is displayed to the user
        )
        params.video_concat_mode = VideoConcatMode(
            video_concat_modes[selected_index][1]
        )


        # Semantic Video Matching Settings - only show when semantic mode is selected
        if params.video_concat_mode.value == "semantic":
            with st.container(border=True):
                st.write(tr("Semantic Video Matching Settings"))
                st.info(tr("Semantic mode analyzes script content to intelligently match video clips with spoken words for better relevance."))
                
                # Check if sentence-transformers is available
                try:
                    import sentence_transformers
                    st.success("✅ Dependências da busca semântica instaladas e prontas.")
                except ImportError:
                    st.warning("⚠️ A busca semântica requer o pacote sentence-transformers.")
                    st.code("pip install sentence-transformers scikit-learn")
                
                # Script Segmentation Method
                segmentation_methods = [
                    (tr("Split by Sentences"), "sentences"),
                    (tr("Split by Paragraphs"), "paragraphs"),
                ]
                segmentation_index = st.selectbox(
                    tr("Script Segmentation Method"),
                    options=range(len(segmentation_methods)),
                    format_func=lambda x: segmentation_methods[x][0],
                    index=0,
                )
                params.segmentation_method = segmentation_methods[segmentation_index][1]
                
                # Minimum Segment Length
                params.min_segment_length = st.slider(
                    tr("Minimum Segment Length"),
                    min_value=10,
                    max_value=100,
                    value=config.app.get("minimum_segment_length", 25),
                    step=5,
                    help=tr("Minimum character length for each script segment")
                )
                
                # Similarity Threshold
                params.similarity_threshold = st.slider(
                    tr("Similarity Threshold"),
                    min_value=0.0,
                    max_value=1.0,
                    value=config.app.get("semantic_similarity_threshold", 0.5),
                    step=0.05,
                    help=tr("Minimum similarity score required for video-text matching")
                )
                
                # Video Diversity Threshold
                params.diversity_threshold = st.slider(
                    tr("Video Diversity Threshold"),
                    min_value=1,
                    max_value=20,
                    value=config.app.get("video_diversity_threshold", 5),
                    step=1,
                    help=tr("Controls how often the same video can be reused")
                )
                
                # Max Video Reuse
                params.max_video_reuse = st.slider(
                    tr("Max Video Reuse"),
                    min_value=1,
                    max_value=10,
                    value=2,
                    step=1,
                    help=tr("Maximum number of times a single video can be reused in the final output")
                )
                
                # Search Pool Size
                params.search_pool_size = st.slider(
                    tr("Search Pool Size"),
                    min_value=10,
                    max_value=200,
                    value=config.app.get("semantic_search_pool_size", 50),
                    step=10,
                    help=tr("Number of videos to consider for semantic matching")
                )
                
                # Semantic Search Model
                semantic_models = [
                    ("MPNet Base V2 (Recommended)", "all-mpnet-base-v2"),
                    ("MiniLM L6 V2 (Faster)", "all-MiniLM-L6-v2"),
                    ("MiniLM L12 V2 (Balanced)", "all-MiniLM-L12-v2"),
                ]
                
                # Find the index of the saved semantic model
                saved_semantic_model = config.app.get("semantic_search_model", "all-mpnet-base-v2")
                saved_semantic_model_index = 0
                for i, (_, model_value) in enumerate(semantic_models):
                    if model_value == saved_semantic_model:
                        saved_semantic_model_index = i
                        break
                
                model_index = st.selectbox(
                    tr("Semantic Search Model"),
                    options=range(len(semantic_models)),
                    format_func=lambda x: semantic_models[x][0],
                    index=saved_semantic_model_index,
                )
                params.semantic_model = semantic_models[model_index][1]
                
                # Image Similarity Settings
                st.markdown("---")
                st.subheader(tr("Image Similarity Settings"))
                
                # Check if image similarity dependencies are available
                image_sim_available = False
                image_sim_info = {"available": False, "dependencies": ["transformers", "torch", "pillow"]}
                
                try:
                    # Test direct imports of required dependencies
                    from transformers import CLIPProcessor, CLIPModel
                    from PIL import Image
                    import torch
                    image_sim_available = True
                    image_sim_info = {"available": True, "dependencies": []}
                except ImportError as e:
                    image_sim_available = False
                    # Try to determine which specific dependency is missing
                    missing_deps = []
                    try:
                        from transformers import CLIPProcessor, CLIPModel
                    except ImportError:
                        missing_deps.append("transformers")
                    
                    try:
                        import torch
                    except ImportError:
                        missing_deps.append("torch")
                    
                    try:
                        from PIL import Image
                    except ImportError:
                        missing_deps.append("pillow")
                    
                    if not missing_deps:
                        missing_deps = ["transformers", "torch", "pillow"]
                    
                    image_sim_info = {"available": False, "dependencies": missing_deps}
                
                if image_sim_available:
                    st.success("✅ Dependências de similaridade de imagens instaladas e prontas.")
                    
                    # Enable Image Similarity - use config default
                    params.enable_image_similarity = st.checkbox(
                        tr("Enable Image Similarity"),
                        value=config.app.get("enable_image_similarity", False),
                        help=tr("Compare text with video thumbnails and preview images for better matching")
                    )
                    
                    if params.enable_image_similarity:
                        # Image Similarity Threshold - use config default
                        params.image_similarity_threshold = st.slider(
                            tr("Image Similarity Threshold"),
                            min_value=0.0,
                            max_value=1.0,
                            value=config.app.get("image_similarity_threshold", 0.7),
                            step=0.05,
                            help=tr("Minimum image similarity score required for video-text matching")
                        )
                        
                        # Image Similarity Model - use config default
                        image_models = [
                            ("CLIP ViT-B/32 (Recommended)", "clip-vit-base-patch32"),
                            ("CLIP ViT-B/16 (Higher Quality)", "clip-vit-base-patch16"),
                            ("CLIP ViT-L/14 (Best Quality)", "clip-vit-large-patch14"),
                        ]
                        
                        # Find the index of the saved model
                        saved_model = config.app.get("image_similarity_model", "clip-vit-base-patch32")
                        saved_model_index = 0
                        for i, (_, model_value) in enumerate(image_models):
                            if model_value == saved_model:
                                saved_model_index = i
                                break
                        
                        image_model_index = st.selectbox(
                            tr("Image Similarity Model"),
                            options=range(len(image_models)),
                            format_func=lambda x: image_models[x][0],
                            index=saved_model_index,
                            help=tr("CLIP model for text-image similarity comparison")
                        )
                        params.image_similarity_model = image_models[image_model_index][1]
                        
                        st.info(tr("Image similarity analyzes video thumbnails and preview frames to find videos that visually match the script content."))
                    else:
                        # Set default values when image similarity is disabled
                        params.image_similarity_threshold = config.app.get("image_similarity_threshold", 0.7)
                        params.image_similarity_model = config.app.get("image_similarity_model", "clip-vit-base-patch32")
                else:
                    st.warning("⚠️ A similaridade de imagens requer dependências adicionais.")
                    missing_deps = ", ".join(image_sim_info.get("dependencies", []))
                    st.code(f"pip install {missing_deps}")
                    params.enable_image_similarity = False
                    params.image_similarity_threshold = 0.7
                    params.image_similarity_model = "clip-vit-base-patch32"
        else:
            # Set default values when not in semantic mode
            params.segmentation_method = "sentences"
            params.min_segment_length = config.app.get("minimum_segment_length", 25)
            params.similarity_threshold = config.app.get("semantic_similarity_threshold", 0.5)
            params.diversity_threshold = config.app.get("video_diversity_threshold", 5)
            params.max_video_reuse = 2
            params.search_pool_size = config.app.get("semantic_search_pool_size", 50)
            params.semantic_model = config.app.get("semantic_search_model", "all-mpnet-base-v2")
            # Image similarity defaults
            params.enable_image_similarity = config.app.get("enable_image_similarity", False)
            params.image_similarity_threshold = config.app.get("image_similarity_threshold", 0.7)
            params.image_similarity_model = config.app.get("image_similarity_model", "clip-vit-base-patch32")

        # 视频转场模式
        video_transition_modes = [
            (tr("None"), VideoTransitionMode.none.value),
            (tr("Shuffle"), VideoTransitionMode.shuffle.value),
            (tr("FadeIn"), VideoTransitionMode.fade_in.value),
            (tr("FadeOut"), VideoTransitionMode.fade_out.value),
            (tr("SlideIn"), VideoTransitionMode.slide_in.value),
            (tr("SlideOut"), VideoTransitionMode.slide_out.value),
        ]
        selected_index = st.selectbox(
            tr("Video Transition Mode"),
            options=range(len(video_transition_modes)),
            format_func=lambda x: video_transition_modes[x][0],
            index=0,
        )
        params.video_transition_mode = VideoTransitionMode(
            video_transition_modes[selected_index][1]
        )

        video_aspect_ratios = [
            (tr("Portrait"), VideoAspect.portrait.value),
            (tr("Landscape"), VideoAspect.landscape.value),
        ]
        selected_index = st.selectbox(
            tr("Video Ratio"),
            options=range(
                len(video_aspect_ratios)
            ),  # Use the index as the internal option value
            format_func=lambda x: video_aspect_ratios[x][
                0
            ],  # The label is displayed to the user
        )
        params.video_aspect = VideoAspect(video_aspect_ratios[selected_index][1])

        # Formatos de entrada/saída visíveis (pedido do Rafael)
        st.caption(
            "🎬 **Entrada e saída**: mesma proporção (**9:16** ou **16:9**) na entrada e no vídeo final"
        )
        st.caption(
            "📥 **Formatos aceitos**: MP4 · MOV · AVI · FLV · MKV (vídeo) · JPG · JPEG · PNG (imagem)"
        )
        st.caption("📤 **Saída**: MP4 (H.264) — formato mais usado, abre em qualquer lugar")

        params.video_clip_duration = st.selectbox(
            tr("Clip Duration"), options=[2, 3, 4, 5, 6, 7, 8, 9, 10], index=1
        )
        # Sempre 1 vídeo por vez (pedido do Rafael)
        params.video_count = 1

    with st.container(border=True):
        st.write(tr("Audio Settings"))

        # Motor de fala único: Supertonic3 (edge/azure removidos - pedido do Rafael)
        tts_servers = [
            ("supertonic", "Supertonic3 (local, CPU)"),
            ("chatterbox", "Chatterbox (local, clonagem de voz)"),
        ]

        saved_tts_server = config.ui.get("tts_server", "supertonic")
        saved_tts_server_index = 0
        for i, (server_value, _) in enumerate(tts_servers):
            if server_value == saved_tts_server:
                saved_tts_server_index = i
                break

        selected_tts_server_index = st.selectbox(
            tr("TTS Servers"),
            options=range(len(tts_servers)),
            format_func=lambda x: tts_servers[x][1],
            index=saved_tts_server_index,
        )

        selected_tts_server = tts_servers[selected_tts_server_index][0]
        config.ui["tts_server"] = selected_tts_server

        # 根据选择的TTS服务器获取声音列表
        filtered_voices = []

        if selected_tts_server == "siliconflow":
            # 获取硅基流动的声音列表
            filtered_voices = voice.get_siliconflow_voices()
        elif selected_tts_server == "chatterbox":
            # 获取Chatterbox的声音列表
            filtered_voices = voice.get_chatterbox_voices()
        elif selected_tts_server == "supertonic":
            filtered_voices = voice.get_supertonic_voices()
        else:
            # 获取Azure的声音列表
            all_voices = voice.get_all_azure_voices(filter_locals=None)

            # 根据选择的TTS服务器筛选声音
            for v in all_voices:
                if selected_tts_server == "azure-tts-v2":
                    # V2版本的声音名称中包含"v2"
                    if "V2" in v:
                        filtered_voices.append(v)
                else:
                    # V1版本的声音名称中不包含"v2"
                    if "V2" not in v:
                        filtered_voices.append(v)

        friendly_names = {
            v: v.replace("Female", tr("Female"))
            .replace("Male", tr("Male"))
            .replace("Neural", "")
            for v in filtered_voices
        }

        saved_voice_name = config.ui.get("voice_name", "")
        saved_voice_name_index = 0

        # 检查保存的声音是否在当前筛选的声音列表中
        if saved_voice_name in friendly_names:
            saved_voice_name_index = list(friendly_names.keys()).index(saved_voice_name)
        else:
            # 如果不在，则根据当前UI语言选择一个默认声音
            for i, v in enumerate(filtered_voices):
                if v.lower().startswith(st.session_state["ui_language"].lower()):
                    saved_voice_name_index = i
                    break

        # 如果没有找到匹配的声音，使用第一个声音
        if saved_voice_name_index >= len(friendly_names) and friendly_names:
            saved_voice_name_index = 0

        voice_name = ""

        # 确保有声音可选
        if friendly_names:
            selected_friendly_name = st.selectbox(
                tr("Speech Synthesis"),
                options=list(friendly_names.values()),
                index=min(saved_voice_name_index, len(friendly_names) - 1)
                if friendly_names
                else 0,
            )

            voice_name = list(friendly_names.keys())[
                list(friendly_names.values()).index(selected_friendly_name)
            ]
            params.voice_name = voice_name
            config.ui["voice_name"] = voice_name
        else:
            # 如果没有声音可选，显示提示信息
            if selected_tts_server == "chatterbox" and not getattr(
                voice, "CHATTERBOX_AVAILABLE", False
            ):
                st.warning(
                    "Chatterbox TTS não está instalado neste ambiente. Instale com "
                    "`pip install chatterbox-tts whisperx` e reinicie a WebUI para "
                    "usar a clonagem de voz."
                )
            else:
                st.warning(
                    tr(
                        "No voices available for the selected TTS server. Please select another server."
                    )
                )
            params.voice_name = ""
            config.ui["voice_name"] = ""

        # Chatterbox TTS特殊设置
        if selected_tts_server == "chatterbox" and friendly_names:
            st.write("---")
            st.write("**Chatterbox TTS Settings**")
            
            # 显示当前选择的声音类型
            if voice_name.startswith("chatterbox:default:"):                    st.info("🎙️ Usando a voz padrão do Chatterbox")
            elif voice_name.startswith("chatterbox:clone:"):
                voice_base_name = voice_name.split(":")[-1].split("-")[0]
                if voice_base_name == "Voice Clone":
                    st.info("🎯 Modo de clonagem de voz — adicione áudios de referência na pasta reference_audio/")
                else:
                    st.success(f"🎭 Voice cloning with: {voice_base_name}")
            
            # 显示参考音频文件夹信息
            import os
            from app.utils import utils
            reference_audio_dir = os.path.join(utils.root_dir(), "reference_audio")
            
            if not os.path.exists(reference_audio_dir):
                with st.expander("📁 Clonagem de Voz — configuração", expanded=False):
                    st.warning("Pasta de áudios de referência não encontrada. Crie-a para ativar a clonagem de voz:")
                    st.code(f"mkdir {reference_audio_dir}")
                    st.info("Coloque seus áudios de referência (.wav, .mp3, .flac, .m4a) nesta pasta.")
            else:
                audio_files = [f for f in os.listdir(reference_audio_dir) 
                             if f.lower().endswith(('.wav', '.mp3', '.flac', '.m4a'))]
                
                with st.expander(f"📁 Arquivos de clonagem de voz ({len(audio_files)} encontrados)", expanded=False):
                    if audio_files:
                        st.success(f"{len(audio_files)} áudio(s) de referência encontrado(s):")
                        for file in audio_files:
                            st.write(f"• {file}")
                    else:
                        st.info("Nenhum áudio de referência. Adicione arquivos .wav, .mp3, .flac ou .m4a nesta pasta.")
            


        # 当选择V2版本或者声音是V2声音时，显示服务区域和API key输入框
        if selected_tts_server == "azure-tts-v2" or (
            voice_name and voice.is_azure_v2_voice(voice_name)
        ):
            saved_azure_speech_region = config.azure.get("speech_region", "")
            saved_azure_speech_key = config.azure.get("speech_key", "")
            azure_speech_region = st.text_input(
                tr("Speech Region"),
                value=saved_azure_speech_region,
                key="azure_speech_region_input",
            )
            azure_speech_key = st.text_input(
                tr("Speech Key"),
                value=saved_azure_speech_key,
                type="password",
                key="azure_speech_key_input",
            )
            config.azure["speech_region"] = azure_speech_region
            config.azure["speech_key"] = azure_speech_key

        # 当选择硅基流动时，显示API key输入框和说明信息
        if selected_tts_server == "siliconflow" or (
            voice_name and voice.is_siliconflow_voice(voice_name)
        ):
            saved_siliconflow_api_key = config.siliconflow.get("api_key", "")

            siliconflow_api_key = st.text_input(
                tr("SiliconFlow API Key"),
                value=saved_siliconflow_api_key,
                type="password",
                key="siliconflow_api_key_input",
            )

            # 显示硅基流动的说明信息
            st.info(
                tr("SiliconFlow TTS Settings")
                + ":\n"
                + "- "
                + tr("Speed: Range [0.25, 4.0], default is 1.0")
                + "\n"
                + "- "
                + tr("Volume: Uses Speech Volume setting, default 1.0 maps to gain 0")
            )

            config.siliconflow["api_key"] = siliconflow_api_key

        params.voice_volume = st.selectbox(
            tr("Speech Volume"),
            options=[0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0],
            index=2,
            help="1.0 = 100% do volume original da voz.",
        )

        params.voice_rate = st.selectbox(
            tr("Speech Rate"),
            options=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0],
            index=2,
            help="1.0 = ritmo normal.",
        )

        # 试听 DEPOIS de volume/velocidade — senão o preview usa os valores velhos
        if friendly_names and st.button(tr("Play Voice"), use_container_width=True):
            play_content = params.video_subject
            if not play_content:
                play_content = params.video_script
            if not play_content:
                play_content = tr("Voice Example")
            with st.spinner(tr("Synthesizing Voice")):
                temp_dir = utils.storage_dir("temp", create=True)
                audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid4())}.mp3")
                sub_maker = voice.tts(
                    text=play_content,
                    voice_name=voice_name,
                    voice_rate=params.voice_rate,
                    voice_file=audio_file,
                    voice_volume=params.voice_volume,
                )
                # if the voice file generation failed, try again with a default content.
                if not sub_maker:
                    play_content = "This is a example voice. if you hear this, the voice synthesis failed with the original content."
                    sub_maker = voice.tts(
                        text=play_content,
                        voice_name=voice_name,
                        voice_rate=params.voice_rate,
                        voice_file=audio_file,
                        voice_volume=params.voice_volume,
                    )

                if sub_maker and os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3")
                    if os.path.exists(audio_file):
                        os.remove(audio_file)

        bgm_options = [
            (tr("No Background Music"), ""),
            (tr("Random Background Music"), "random"),
            (tr("Custom Background Music"), "custom"),
        ]
        selected_index = st.selectbox(
            tr("Background Music"),
            index=1,
            options=range(
                len(bgm_options)
            ),  # Use the index as the internal option value
            format_func=lambda x: bgm_options[x][
                0
            ],  # The label is displayed to the user
        )
        # Get the selected background music type
        params.bgm_type = bgm_options[selected_index][1]

        # Show or hide components based on the selection
        if params.bgm_type == "custom":
            custom_bgm_upload = st.file_uploader(
                tr("Custom Background Music File"),
                type=["mp3", "wav", "m4a", "ogg", "flac", "aac"],
                key="custom_bgm_file_input",
            )
            if custom_bgm_upload is not None:
                bgm_dir = utils.storage_dir("bgm", create=True)
                bgm_path = os.path.join(bgm_dir, custom_bgm_upload.name)
                with open(bgm_path, "wb") as f:
                    f.write(custom_bgm_upload.getbuffer())
                params.bgm_file = bgm_path
                st.success(f"🎵 {tr('Custom Background Music File')}: {custom_bgm_upload.name}")
        params.bgm_volume = st.selectbox(
            tr("Background Music Volume"),
            options=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            index=2,
            help="0.2 = 20% — não deixe alto demais, senão cobre a narração.",
        )

with right_panel:
    with st.container(border=True):
        st.write(tr("Timeline"))
        fds_render_timeline()

    with st.container(border=True):
        st.write(tr("Subtitle Settings"))
        params.subtitle_enabled = st.checkbox(
            tr("Enable Subtitles"),
            value=True,
            help="Se desmarcado, as opções abaixo não têm efeito.",
        )
        font_names = get_all_fonts()
        saved_font_name = config.ui.get("font_name", "MicrosoftYaHeiBold.ttc")
        saved_font_name_index = 0
        if saved_font_name in font_names:
            saved_font_name_index = font_names.index(saved_font_name)
        params.font_name = st.selectbox(
            tr("Font"), font_names, index=saved_font_name_index
        )
        config.ui["font_name"] = params.font_name

        subtitle_positions = [
            (tr("Top"), "top"),
            (tr("Center"), "center"),
            (tr("Bottom"), "bottom"),
            (tr("Custom"), "custom"),
        ]
        selected_index = st.selectbox(
            tr("Position"),
            index=2,
            options=range(len(subtitle_positions)),
            format_func=lambda x: subtitle_positions[x][0],
        )
        params.subtitle_position = subtitle_positions[selected_index][1]

        if params.subtitle_position == "custom":
            custom_position = st.text_input(
                tr("Custom Position (% from top)"),
                value="70.0",
                key="custom_position_input",
            )
            try:
                params.custom_position = float(custom_position)
                if params.custom_position < 0 or params.custom_position > 100:
                    st.error(tr("Please enter a value between 0 and 100"))
            except ValueError:
                st.error(tr("Please enter a valid number"))

        font_cols = st.columns([0.3, 0.7])
        with font_cols[0]:
            saved_text_fore_color = config.ui.get("text_fore_color", "#FFFFFF")
            params.text_fore_color = st.color_picker(
                tr("Font Color"), saved_text_fore_color
            )
            config.ui["text_fore_color"] = params.text_fore_color

        with font_cols[1]:
            saved_font_size = config.ui.get("font_size", 60)
            params.font_size = st.slider(tr("Font Size"), 30, 100, saved_font_size)
            config.ui["font_size"] = params.font_size

        stroke_cols = st.columns([0.3, 0.7])
        with stroke_cols[0]:
            params.stroke_color = st.color_picker(tr("Stroke Color"), "#000000")
        with stroke_cols[1]:
            params.stroke_width = st.slider(tr("Stroke Width"), 0.0, 10.0, 1.5)

        # Word highlighting settings
        st.write("**Destaque da Palavra Falada**")
        saved_enable_word_highlighting = config.ui.get("enable_word_highlighting", False)
        params.enable_word_highlighting = st.checkbox(
            tr("Enable Word Highlighting (If unchecked, the settings below will not take effect)"),
            value=saved_enable_word_highlighting,
            help="Se desmarcado, as opções abaixo não têm efeito.",
        )
        config.ui["enable_word_highlighting"] = params.enable_word_highlighting
        
        if params.enable_word_highlighting:
            highlight_cols = st.columns([0.3, 0.7])
            with highlight_cols[0]:
                saved_highlight_color = config.ui.get("highlight_color", "#ff0000")
                params.word_highlight_color = st.color_picker(
                    tr("Highlight Color"), saved_highlight_color
                )
                config.ui["highlight_color"] = params.word_highlight_color
            
            with highlight_cols[1]:
                saved_max_chars_per_line = config.ui.get("max_chars_per_line", 40)
                params.max_chars_per_line = st.slider(
                    tr("Max Characters Per Line"), 20, 80, saved_max_chars_per_line
                )
                config.ui["max_chars_per_line"] = params.max_chars_per_line
            
            saved_max_lines_per_subtitle = config.ui.get("max_lines_per_subtitle", 2)
            params.max_lines_per_subtitle = st.slider(
                tr("Max Lines Per Subtitle"), 1, 4, saved_max_lines_per_subtitle
            )
            config.ui["max_lines_per_subtitle"] = params.max_lines_per_subtitle
        else:
            # Set default values when word highlighting is disabled
            params.word_highlight_color = config.ui.get("highlight_color", "#ff0000")
            params.max_chars_per_line = config.ui.get("max_chars_per_line", 40)
            params.max_lines_per_subtitle = config.ui.get("max_lines_per_subtitle", 2)

start_button = st.button(tr("Generate Video"), use_container_width=True, type="primary")
if start_button:
    config.save_config()
    task_id = str(uuid4())
    if not params.video_subject and not params.video_script:
        st.error(tr("Video Script and Subject Cannot Both Be Empty"))
        scroll_to_bottom()
        st.stop()

    if params.video_source not in ["pexels", "pixabay", "local"]:
        st.error(tr("Please Select a Valid Video Source"))
        scroll_to_bottom()
        st.stop()

    if params.video_source == "pexels" and not config.app.get("pexels_api_keys", ""):
        st.error(tr("Please Enter the Pexels API Key"))
        scroll_to_bottom()
        st.stop()

    if params.video_source == "pixabay" and not config.app.get("pixabay_api_keys", ""):
        st.error(tr("Please Enter the Pixabay API Key"))
        scroll_to_bottom()
        st.stop()

    if params.video_source == "local":
        mats = st.session_state.get("fds_local_materials") or []
        if not mats:
            st.error(
                "Envie arquivos ou carregue uma pasta com vídeos/imagens antes de gerar."
            )
            scroll_to_bottom()
            st.stop()
        if not params.video_materials:
            params.video_materials = []
        for m in mats:
            mi = MaterialInfo()
            mi.provider = "local"
            mi.url = m["path"]
            params.video_materials.append(mi)

    log_container = st.empty()
    log_records = []

    def log_received(msg):
        if config.ui["hide_log"]:
            return
        with log_container:
            log_records.append(msg)
            st.code("\n".join(log_records))

    logger.add(log_received)

    st.toast(tr("Generating Video"))
    logger.info(tr("Start Generating Video"))
    logger.info(utils.to_json(params))
    scroll_to_bottom()

    result = tm.start(task_id=task_id, params=params)
    if not result or "videos" not in result:
        st.error(tr("Video Generation Failed"))
        logger.error(tr("Video Generation Failed"))
        scroll_to_bottom()
        st.stop()

    video_files = result.get("videos", [])
    st.success(tr("Video Generation Completed"))
    try:
        if video_files:
            player_cols = st.columns(len(video_files) * 2 + 1)
            for i, url in enumerate(video_files):
                player_cols[i * 2 + 1].video(url)
    except Exception:
        pass

    open_task_folder(task_id)
    logger.info(tr("Video Generation Completed"))
    scroll_to_bottom()

config.save_config()
