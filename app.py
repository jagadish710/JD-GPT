import streamlit as st
from google import genai
from groq import Groq

# ── Load System Instructions ────────────────────────────────────
with open(
    "system_prompt.txt",
    "r",
    encoding="utf-8"
) as f:
    SYSTEM_PROMPT = f.read()

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="JD-GPT | SQL Intelligence",
    page_icon="🧠",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(
            135deg, 
            #0a0a1a 0%, 
            #0d1b2a 50%, 
            #0a0a1a 100%
        );
    }
    
    /* Header glow effect */
    .main-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    
    .main-title {
        font-size: 3.2em;
        font-weight: 900;
        background: linear-gradient(
            90deg, 
            #00d4ff, 
            #7b2fff, 
            #00d4ff
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 6px;
        text-transform: uppercase;
    }
    
    .sub-title {
        color: #00d4ff;
        font-size: 0.9em;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0.8;
    }
    
    .builder-tag {
        color: #7b2fff;
        font-size: 0.75em;
        letter-spacing: 2px;
        opacity: 0.7;
    }

    /* Status messages */
    .status-online {
        background: linear-gradient(
            90deg, 
            rgba(0,212,255,0.1), 
            rgba(123,47,255,0.1)
        );
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 8px;
        padding: 8px 15px;
        color: #00d4ff;
        font-size: 0.8em;
        letter-spacing: 1px;
        text-align: center;
    }

    /* SQL output block */
    .sql-block {
        background: rgba(0,212,255,0.05);
        border-left: 3px solid #00d4ff;
        border-radius: 4px;
        padding: 10px;
    }

    /* Input labels */
    .input-label {
        color: #00d4ff;
        font-size: 0.85em;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    /* Divider color */
    hr {
        border-color: rgba(0,212,255,0.2) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(
            90deg, 
            #00d4ff, 
            #7b2fff
        ) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-size: 0.85em !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 20px rgba(0,212,255,0.4) !important;
    }

    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        background: rgba(0,212,255,0.05) !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stTextArea textarea:focus, 
    .stTextInput input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
    }

    /* Success/info/warning boxes */
    .stSuccess {
        background: rgba(0,212,255,0.1) !important;
        border: 1px solid rgba(0,212,255,0.4) !important;
    }
    
    .stInfo {
        background: rgba(123,47,255,0.1) !important;
        border: 1px solid rgba(123,47,255,0.4) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #00d4ff !important;
        font-size: 0.85em !important;
        letter-spacing: 1px !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: rgba(0,212,255,0.4);
        font-size: 0.7em;
        letter-spacing: 2px;
        padding: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Core Function ─────────────────────────────────────────
def generate_sql(
        schema,
        question,
        dialect,
        complexity):

    prompt = f"""
{SYSTEM_PROMPT}

SQL DIALECT:
{dialect}

OPTIMIZATION MODE:
{complexity}

DATABASE SCHEMA:
{schema}

BUSINESS QUESTION:
{question}
"""

    # ===== GEMINI PRIMARY =====
    try:

        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0,
                "max_output_tokens": 8192
            }
        )

        return response.text, "primary"

    except Exception as gemini_error:

        print("\n===== GEMINI ERROR =====")
        print(gemini_error)

        st.warning(
        """
🧠 JD is busy...

⚡ KD is taking action..

✓ Your query is in good hands.
"""
    )

        # ===== GROQ FALLBACK =====
        try:

            client = Groq(
                api_key=st.secrets["GROQ_API_KEY"]
            )

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content":
                        f"""
SQL DIALECT:
{dialect}

OPTIMIZATION MODE:
{complexity}

DATABASE SCHEMA:
{schema}

BUSINESS QUESTION:
{question}
"""
                    }
                ],
                temperature=0,
                max_completion_tokens=8192
            )

            return (
                response.choices[0].message.content,
                "backup"
            )

        except Exception as groq_error:

            print("\n===== GROQ ERROR =====")
            print(groq_error)

            st.error(
                f"""Both JD and KD are unavailable.

Gemini Error:
{gemini_error}

Groq Error:
{groq_error}
"""
            )

            return None, "failed"

# ── Display Results ───────────────────────────────────────
def display_results(result, system):
    
    # JD-style status
    if system == "primary":
        st.markdown("""
        <div class='status-online'>
        ⚡ NEURAL CORE ONLINE — 
        PRIMARY INTELLIGENCE ACTIVE
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='status-online'>
        🔄 SWITCHING TO BACKUP CORE — 
        SECONDARY INTELLIGENCE ACTIVE
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Parse and display
    if "SQL QUERY:" in result:
        parts = result.split("EXPLANATION:")
        sql_part = parts[0].replace(
            "SQL QUERY:", ""
        ).strip()
        
        # Remove markdown code blocks if present
        sql_clean = sql_part.replace(
            "```sql", ""
        ).replace("```", "").strip()
        
        st.markdown(
            "#### 📋 QUERY OUTPUT",
        )
        st.code(sql_clean, language="sql")
        st.caption(
            "💡 Click copy icon (top right) "
            "to copy SQL"
        )
        
        if len(parts) > 1:
            exp_parts = parts[1].split("ASSUMPTIONS:")
            
            st.markdown("#### 💬 ANALYSIS")
            st.info(exp_parts[0].strip())
            
            if len(exp_parts) > 1:
                assumptions = exp_parts[1].strip()
                if assumptions and len(assumptions) > 5:
                    st.markdown("#### ⚠️ PARAMETERS")
                    st.warning(assumptions)
    else:
        # Clean any markdown
        clean = result.replace(
            "```sql", ""
        ).replace("```", "").strip()
        st.code(clean, language="sql")


# ══════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════

# ── Hero Header ───────────────────────────────
st.markdown("""
<div class='main-header'>
    <div class='main-title'>JD — GPT</div>
    <div class='sub-title'>
        SQL Intelligence System v1.0
    </div>
    <div class='builder-tag'>
        ENGINEERED BY JAGADISH B
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── System Status ─────────────────────────────
st.markdown("""
<div class='status-online'>
🟢 ALL SYSTEMS OPERATIONAL — 
DUAL-CORE AI READY
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ── How It Works ──────────────────────────────
with st.expander("⚡ SYSTEM CAPABILITIES"):
    st.markdown("""
    **JD-GPT converts plain English into SQL instantly.**
    
    🧠 **Dual AI Architecture**
    - Primary Core: JD
    - Backup Core: KD
    - Auto-switches if primary is unavailable
    
    📋 **What It Returns**
    - Production-ready SQL query
    - Plain English explanation
    - Stated assumptions
    
    💡 **How To Use**
    1. Describe your table structure
    2. Ask your business question
    3. Copy and run the SQL
    """)

st.divider()

# ── Schema Input ──────────────────────────────

col1, col2 = st.columns(2)

with col1:
    dialect = st.selectbox(
        "SQL Dialect",
        [
            "PostgreSQL",
            "MySQL",
            "SQL Server",
            "HiveQL",
            "Snowflake",
            "BigQuery"
        ]
    )

with col2:
    complexity = st.selectbox(
        "Optimization",
        [
            "Readable",
            "Balanced",
            "Performance"
        ]
    )
    
    
st.markdown(
    "<div class='input-label'>"
    "▸ STEP 01 — DATABASE SCHEMA"
    "</div>",
    unsafe_allow_html=True
)

schema = st.text_area(
    label="schema_input",
    label_visibility="collapsed",
    placeholder="""Example:
Table: sales
Columns: 
  - product_id (INT)
  - product_name (VARCHAR)
  - category (VARCHAR)
  - revenue (DECIMAL)
  - quantity (INT)
  - sale_date (DATE)
  - region (VARCHAR)""",
    height=180,
)

st.markdown("")

# ── Question Input ────────────────────────────
st.markdown(
    "<div class='input-label'>"
    "▸ STEP 02 — BUSINESS QUERY"
    "</div>",
    unsafe_allow_html=True
)

question = st.text_input(
    label="question_input",
    label_visibility="collapsed",
    placeholder="e.g. Show me top 10 products "
                "by revenue last month"
)

st.markdown("")

# ── Example Queries ───────────────────────────
with st.expander("💡 SAMPLE QUERIES"):
    st.markdown("""
    - *Top 10 products by revenue last 30 days*
    - *Month-over-month revenue growth by category*
    - *Products with sales drop greater than 20%*
    - *Find duplicate records in customer table*
    - *Daily active users for past 7 days*
    - *Which regions are below sales target?*
    - *Calculate running total revenue by month*
    - *Rank sellers by performance within category*
    """)

st.divider()

# ── Generate Button ───────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate = st.button(
        "⚡ ACTIVATE JD-GPT",
        use_container_width=True,
        type="primary"
    )

# ── Handle Generation ─────────────────────────
if generate:
    if not schema.strip():
        st.error(
            "⚠️ Schema input required. "
            "Describe your table structure."
        )
    elif not question.strip():
        st.error(
            "⚠️ Query input required. "
            "Ask your business question."
        )
    else:
        with st.spinner(
            "🧠 Processing query intelligence..."
        ):
            result, system = generate_sql(
                schema,
                question,
                dialect,
                complexity
            )
        
        st.divider()
        
        if result is None:
            st.error(
                "⚠️ ALL CORES UNAVAILABLE — "
                "Both AI systems are temporarily "
                "offline. Please retry shortly."
            )
        else:
            display_results(result, system)

# ── Footer ────────────────────────────────────
st.divider()
st.markdown("""
<div class='footer'>
    JD-GPT v1.0 &nbsp;|&nbsp; 
    DUAL-CORE AI ARCHITECTURE &nbsp;|&nbsp;
    ENGINEERED BY JAGADISH B
    <br><br>
    <a href='https://linkedin.com/in/jagadish-b-814827190' 
       style='color:#00d4ff;text-decoration:none;
       letter-spacing:1px;'>
       LINKEDIN
    </a>
    &nbsp;&nbsp;
    <a href='https://github.com/jagadishb-analyst' 
       style='color:#7b2fff;text-decoration:none;
       letter-spacing:1px;'>
       GITHUB
    </a>
    &nbsp;&nbsp;
    <a href='https://app.powerbi.com/view?r=eyJrIjoiMTkzNzdhMDItYzgwNS00MGU2LTk5Y2EtZjJkN2M4NTczOWNiIiwidCI6ImFjOTNmZDhjLWYwMDgtNDVjNy1iODZiLWExNmIyNTE0OGQ0YiJ9&pageName=e363c65be3d247229a25' 
       style='color:#00d4ff;text-decoration:none;
       letter-spacing:1px;'>
       POWER BI
    </a>
</div>
""", unsafe_allow_html=True)