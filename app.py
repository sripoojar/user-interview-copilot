import streamlit as st
import anthropic

st.set_page_config(page_title="User Interview Copilot", page_icon="🎯", layout="wide")

st.title("🎯 User Interview Copilot")
st.caption("Paste your interview notes and get a connected PM story — persona, strategy, metrics, and stakeholder narrative.")

st.divider()

# ── SIDEBAR: Context Questions ──────────────────────────────────────────────
with st.sidebar:
    st.header("📋 Interview Context")
    st.caption("Help the tool understand your product before analysing.")

    product_description = st.text_input(
        "What is your product?",
        placeholder="e.g. A B2B SaaS tool that helps HR teams manage onboarding"
    )

    business_model = st.selectbox(
        "Business model",
        ["Select one", "B2C", "B2B", "B2B2C", "Marketplace"]
    )

    product_stage = st.selectbox(
        "Product stage",
        ["Select one", "0→1 (Building)", "Early Growth", "Scaling", "Maturity"]
    )

    interview_goal = st.selectbox(
        "Goal of this interview",
        ["Select one", "Discovery", "Usability Testing", "Churn Analysis", "Satisfaction / NPS", "Feature Validation"]
    )

    interviewee_type = st.selectbox(
        "Who did you interview?",
        ["Select one", "Existing User", "Churned User", "Prospect / Non-user", "Internal Stakeholder"]
    )

    product_docs = st.text_area(
        "Product vision / strategy (optional)",
        placeholder="Paste your product vision, OKRs, or strategy notes here. The more context, the better the output.",
        height=120
    )

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-..."
    )

# ── MAIN AREA: Transcript Input ──────────────────────────────────────────────
st.subheader("📝 Paste Your Interview")

input_type = st.radio(
    "Input format",
    ["Raw transcript", "Bullet point notes"],
    horizontal=True
)

transcript = st.text_area(
    "Interview content",
    placeholder="Paste your transcript or notes here...",
    height=250
)

analyse_button = st.button("✨ Analyse Interview", type="primary", use_container_width=True)

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if analyse_button:

    # Validation
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()
    if not transcript:
        st.error("Please paste your interview transcript or notes.")
        st.stop()
    if business_model == "Select one" or product_stage == "Select one":
        st.error("Please fill in the context questions in the sidebar.")
        st.stop()
    if not product_description:
        st.error("Please describe your product in the sidebar.")
        st.stop()

    # Build the prompt
    prompt = f"""You are an expert product manager coach helping a PM extract deep insights from a user interview.

PRODUCT CONTEXT:
- Product: {product_description}
- Business Model: {business_model}
- Stage: {product_stage}
- Interview Goal: {interview_goal}
- Interviewee Type: {interviewee_type}
- Product Vision / Strategy: {product_docs if product_docs else "Not provided"}

INTERVIEW {input_type.upper()}:
{transcript}

Analyse this interview and produce exactly 4 sections:

## 1. Persona Signal
Who is this user really? Go beyond demographics. What do they care about, what are their underlying motivations, what job are they trying to get done? If B2B, what is their role-based context and decision-making power?

## 2. Strategic Connection
How does what this user said connect to the product vision and strategy provided? What does this validate, challenge, or reveal about the current strategic direction? Be specific — reference actual things the user said.

## 3. Metric Recommendations
Given the business model ({business_model}), product stage ({product_stage}), and what this user revealed, what metrics should the PM track? Recommend:
- 1 North Star metric this interview speaks to
- 2-3 supporting metrics to watch
- 1 metric that might be misleading right now and why

## 4. The Stakeholder Story
Write a crisp, 3-paragraph narrative the PM can use to present this interview to their team or leadership. Structure: (1) What we heard, (2) What it means for our strategy, (3) What we should do next.

Be direct, specific, and PM-native in your language. No generic advice."""

    # Call Claude API
    with st.spinner("Connecting the dots..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response = message.content[0].text

            st.divider()
            st.subheader("✅ Your Interview Analysis")

            # Split and display sections
            sections = response.split("## ")
            for section in sections:
                if section.strip():
                    lines = section.strip().split("\n", 1)
                    title = lines[0].strip()
                    content = lines[1].strip() if len(lines) > 1 else ""

                    color_map = {
                        "1. Persona Signal": "🧠",
                        "2. Strategic Connection": "🎯",
                        "3. Metric Recommendations": "📊",
                        "4. The Stakeholder Story": "📣"
                    }

                    icon = color_map.get(title, "•")

                    with st.expander(f"{icon} {title}", expanded=True):
                        st.markdown(content)

            # Download button
            st.divider()
            st.download_button(
                label="📥 Download Analysis",
                data=response,
                file_name="interview_analysis.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.caption("Double-check your API key and try again.")