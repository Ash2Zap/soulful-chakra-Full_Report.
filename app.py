import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests
import re

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Soulful Aura & Chakra Report",
    page_icon="🪬",
    layout="centered"
)

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
LOGO_FILE = "soulful_logo.jpg"

# If you have 7 chakra icons, put the links here:
CHAKRA_ICONS = {
    "Root (Muladhara)": "",
    "Sacral (Svadhisthana)": "",
    "Solar Plexus (Manipura)": "",
    "Heart (Anahata)": "",
    "Throat (Vishuddha)": "",
    "Third Eye (Ajna)": "",
    "Crown (Sahasrara)": "",
}

CHAKRAS = [
    "Root (Muladhara)",
    "Sacral (Svadhisthana)",
    "Solar Plexus (Manipura)",
    "Heart (Anahata)",
    "Throat (Vishuddha)",
    "Third Eye (Ajna)",
    "Crown (Sahasrara)",
]

STATUS_OPTIONS = [
    "Balanced / Radiant",
    "Slightly Weak",
    "Blocked / Underactive",
    "Overactive / Dominant",
]

AURA_COLORS = [
    "Red / Deep Red",
    "Orange",
    "Yellow",
    "Green",
    "Blue",
    "Indigo",
    "Violet / White",
]

AURA_SIZES = [
    "Large (75-100) – strong outgoing field",
    "Medium (40-75) – good daily radiance",
    "Small (0-40) – low energy / introverted",
]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def clean_txt(t: str) -> str:
    """Remove non-latin chars so fpdf does not break on Streamlit Cloud."""
    if t is None:
        return ""
    t = re.sub(r"[^\x00-\xFF]", "", t)
    t = t.replace("•", "- ").replace("—", "-").replace("–", "-")
    return t


def download_logo():
    if not os.path.exists(LOGO_FILE):
        try:
            r = requests.get(LOGO_URL, timeout=10)
            if r.status_code == 200:
                with open(LOGO_FILE, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass


def get_aura_text(aura_color: str) -> str:
    # inspired by the PDF structure you shared, but rewritten in your voice
    if aura_color == "Red / Deep Red":
        return (
            "Your field is practical, grounded and action oriented. Red/Deep Red often shows a person "
            "who had to become strong early in life and now carries physical willpower. When balanced, "
            "this aura can create money, protect the family and finish work. When stressed, it can slip "
            "into anger, impatience or a 'I must do everything' pattern."
        )
    if aura_color == "Orange":
        return (
            "Your aura shows creativity and emotional expression. This is the business-and-joy color. "
            "Orange people like to build, enjoy, travel, teach. If the sacral is weak, this same color "
            "can show emotional ups and downs or attraction to unavailable partners."
        )
    if aura_color == "Yellow":
        return (
            "Yellow is sunny, curious, learning, young-at-heart. This aura likes to learn tools, join programs, "
            "and teach others. When the solar plexus is tired, yellow can overthink and procrastinate."
        )
    if aura_color == "Green":
        return (
            "Green is the teacher-healer field. It belongs to people who want harmony in the family and community. "
            "They pick up emotions easily. They must protect their heart and not overgive."
        )
    if aura_color == "Blue":
        return (
            "Blue is caring, devotional, service-based. This aura type speaks from the heart and wants to help. "
            "But if the throat is blocked, words stay inside and resentment builds."
        )
    if aura_color == "Indigo":
        return (
            "Indigo is intuitive, inner-knowing, deep-feeling. It belongs to sensitives, empaths and spiritual leaders. "
            "They must ground daily so that intuition can become action."
        )
    if aura_color == "Violet / White":
        return (
            "Violet/White is spiritual, visionary and future-oriented. This field belongs to people who are called "
            "to lead energy work, healing circles or consciousness projects. Grounding, money rituals and body work "
            "must be added so the vision can enter matter."
        )
    return "Your aura reflects sensitivity, awareness and a call to live from your higher self."


def get_chakra_text(chakra: str, status: str) -> str:
    # long readable text per chakra + status
    base_expl = {
        "Root (Muladhara)": (
            "Root holds safety, tribe, money, and body trust. It is formed by childhood home situation, "
            "parents' money beliefs and how much stability you felt growing up."
        ),
        "Sacral (Svadhisthana)": (
            "Sacral is the emotional water centre. It holds relationships, receiving, sexuality and your ability "
            "to enjoy life without guilt."
        ),
        "Solar Plexus (Manipura)": (
            "Solar is personal power, pricing, visibility and the right to act. Many coaches and healers have wounded solar "
            "because they were judged when they shined."
        ),
        "Heart (Anahata)": (
            "Heart is love, forgiveness, self-worth and the bridge between spiritual and physical. Over-givers usually have a tired heart."
        ),
        "Throat (Vishuddha)": (
            "Throat is expression, boundaries, selling, teaching, and saying no. If expression was not safe in childhood, this chakra will hold back."
        ),
        "Third Eye (Ajna)": (
            "Third Eye is clarity, intuition, vision and your inner GPS. Overthinking and spiritual doubt sit here."
        ),
        "Crown (Sahasrara)": (
            "Crown is higher connection, faith, surrender, divine downloads. When strong, it gives guidance. When weak, person feels alone."
        ),
    }
    status_text = {
        "Balanced / Radiant": "Currently flowing well. Maintain with daily meditation and gratitude.",
        "Slightly Weak": "Shows mild fatigue. Client may be doing too much for others. Add energy hygiene.",
        "Blocked / Underactive": "This is the main healing focus. There is an old story, trauma or belief sitting here.",
        "Overactive / Dominant": "Energy is pushing too hard here. Bring grounding, forgiveness and physical rituals.",
    }
    return base_expl.get(chakra, "") + " " + status_text.get(status, "")


def make_pdf(report_data: dict) -> bytes:
    """
    report_data = {
        client_name, coach_name, date, goal, aura_color, aura_size,
        chakras: {ch_name: {"status":.., "notes":.., "remedies":..}},
        follow_up, affirmations
    }
    """
    download_logo()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    # -------------------------------------------------
    # PAGE 1 – COVER / SUMMARY
    # -------------------------------------------------
    pdf.add_page()
    pdf.set_fill_color(139, 92, 246)  # purple
    pdf.rect(0, 0, 210, 22, "F")
    pdf.set_fill_color(236, 72, 153)  # pink
    pdf.rect(0, 22, 7, 275, "F")

    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=3, w=16)

    pdf.set_xy(30, 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 8, "Soulful Academy", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Aura & Chakra Guidance Report", ln=True)

    pdf.ln(14)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean_txt("Client Information"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, clean_txt(f"Client Name: {report_data['client_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Session Date: {report_data['date']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Coach / Healer: {report_data['coach_name']}"), ln=True)
    if report_data.get("goal"):
        pdf.multi_cell(0, 6, clean_txt(f"Primary Intent: {report_data['goal']}"))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Aura & Field"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, clean_txt(f"Aura Color Type: {report_data['aura_color']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Aura Size: {report_data['aura_size']}"), ln=True)

    # draw chakra quick summary like bars
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Chakra Snapshot"), ln=True)
    pdf.set_font("Arial", "", 10)
    for ch_name in CHAKRAS:
        ch = report_data["chakras"][ch_name]
        pdf.cell(62, 6, clean_txt(ch_name), border=0)
        # status bar
        x = pdf.get_x()
        y = pdf.get_y()
        # background
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(x, y, 60, 5, "F")
        # fill depending on status
        status = ch["status"]
        fill_w = 20
        if status == "Balanced / Radiant":
            fill_w = 60
            pdf.set_fill_color(110, 231, 183)  # green
        elif status == "Slightly Weak":
            fill_w = 35
            pdf.set_fill_color(252, 211, 77)   # yellow
        elif status == "Blocked / Underactive":
            fill_w = 22
            pdf.set_fill_color(248, 113, 113)  # red
        elif status == "Overactive / Dominant":
            fill_w = 48
            pdf.set_fill_color(129, 140, 248)  # indigo

        pdf.rect(x, y, fill_w, 5, "F")
        pdf.set_xy(x + 62, y)
        pdf.cell(0, 6, clean_txt(status), ln=True)

    # -------------------------------------------------
    # PAGE 2 – AURA & ENERGY EXPLANATION
    # -------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean_txt("2. Your Aura & Energy Expression"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, clean_txt(get_aura_text(report_data["aura_color"])))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Aura Size Meaning"), ln=True)
    pdf.set_font("Arial", "", 11)
    if report_data["aura_size"].startswith("Large"):
        pdf.multi_cell(
            0, 6,
            clean_txt(
                "You currently radiate a powerful field. People can feel you when you enter a room. "
                "Use this for coaching, healing sessions and leadership. Protect your field after group work."
            )
        )
    elif report_data["aura_size"].startswith("Medium"):
        pdf.multi_cell(
            0, 6,
            clean_txt(
                "You are well resourced for day-to-day life. With small upgrades in grounding and breath "
                "you can open into an even wider presence."
            )
        )
    else:
        pdf.multi_cell(
            0, 6,
            clean_txt(
                "Energy is a bit inward right now. This happens after emotional phases or overwork. "
                "Daily energy hygiene, hydration and nature will open the field again."
            )
        )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Important Note from Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        5,
        clean_txt(
            "This report is an energetic and coaching perspective to help you understand patterns. "
            "For medical or psychological diagnosis, please consult an appropriate professional."
        )
    )

    # -------------------------------------------------
    # PAGE 3 – CHAKRA BY CHAKRA
    # -------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean_txt("3. Chakra-by-Chakra Guidance"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        5,
        clean_txt(
            "Each centre below shows what the energy centre holds, what your current status looks like and "
            "what to prioritise in your self-healing or coaching sessions."
        )
    )

    for ch_name in CHAKRAS:
        row = report_data["chakras"][ch_name]
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, clean_txt(ch_name), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, clean_txt(f"Status: {row['status']}"), ln=True)
        # explanation
        pdf.multi_cell(0, 5, clean_txt(get_chakra_text(ch_name, row["status"])))
        # symptoms / notes
        if row["notes"]:
            pdf.set_font("Arial", "I", 9)
            pdf.multi_cell(0, 5, clean_txt("Coach notes: " + row["notes"]))
        # remedies
        if row["remedies"]:
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 5, clean_txt("Suggested remedies: " + row["remedies"]))

    # -------------------------------------------------
    # PAGE 4 – FOLLOW UP / AFFIRMATIONS
    # -------------------------------------------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, clean_txt("4. Follow-up Plan"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 5, clean_txt(report_data.get("follow_up") or
                                   "Next 7 days: 108x Ho'oponopono on the main person/event, "
                                   "5-minute chakra breathing, 1 bold action in money/relationship."))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("5. Affirmations for Daily Alignment"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(report_data.get("affirmations") or
                                   "I am safe. I am allowed to receive. My power is safe. My heart is open. "
                                   "I speak with clarity. I trust my inner guidance. I walk with the Divine."))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, clean_txt("Auto-generated by Soulful Academy Chakra Template. Use this as a coaching aid."))

    return pdf.output(dest="S").encode("latin-1", "ignore")


# ---------------------------------------------------------
# UI – FORM
# ---------------------------------------------------------
st.title("Chakra Scanning Template – Soulful Academy")

with st.form("chakra_form"):
    st.subheader("Client Details")
    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client Name", "")
        coach_name = st.text_input("Coach / Healer Name", "Rekha Babulkar")
    with c2:
        date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))
        goal = st.text_input("Client Intent / Block (money, relationship, health, spiritual)", "")

    st.markdown("---")
    st.subheader("Aura / Energy Reading")
    aura_color = st.selectbox("Aura Color Type (intuitive)", AURA_COLORS)
    aura_size = st.selectbox("Aura Size", AURA_SIZES)

    st.markdown("---")
    st.subheader("Chakra-wise Observations")

    chakra_payload = {}
    for ch_name in CHAKRAS:
        with st.expander(ch_name, expanded=(ch_name in ["Root (Muladhara)", "Sacral (Svadhisthana)"])):
            status = st.selectbox(f"Energy status – {ch_name}", STATUS_OPTIONS, key=f"status_{ch_name}")
            notes = st.text_area(f"Notes / Symptoms – {ch_name}", value="", key=f"notes_{ch_name}")
            remedies = st.text_input(
                f"Remedies – {ch_name} (eg. Reiki, Ho'oponopono 108x, Color therapy, Inner child)",
                value="",
                key=f"rem_{ch_name}"
            )
            chakra_payload[ch_name] = {
                "status": status,
                "notes": notes,
                "remedies": remedies,
            }

    st.markdown("---")
    st.subheader("Session Wrap Up")
    follow_up = st.text_area("Follow-up plan", "Follow-up in 7 days. Track emotions daily. Do chakra meditation.")
    affirmations = st.text_area(
        "Affirmations to print in PDF",
        "Root: I am safe and supported.\nSacral: I allow myself to receive.\nSolar: My power is safe.\n"
        "Heart: I give and receive love.\nThroat: I speak clearly.\nThird Eye: I trust my guidance.\nCrown: I am connected."
    )

    submitted = st.form_submit_button("Create PDF Report", use_container_width=True)

if submitted:
    if not client_name:
        st.error("Please enter client name.")
    else:
        data = {
            "client_name": client_name,
            "coach_name": coach_name,
            "date": date_val,
            "goal": goal,
            "aura_color": aura_color,
            "aura_size": aura_size,
            "chakras": chakra_payload,
            "follow_up": follow_up,
            "affirmations": affirmations,
        }
        pdf_bytes = make_pdf(data)
        st.success("Report created. Download below.")
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{client_name}_aura_chakra_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
