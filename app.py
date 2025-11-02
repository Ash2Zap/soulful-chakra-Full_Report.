import streamlit as st
from fpdf import FPDF
import datetime
import re
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Soulful Chakra Report", page_icon="🪬", layout="centered")

LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
LOGO_FILE = "soulful_logo.jpg"   # we will try to download; if not, we skip

# --------------------------------------------------
# CHAKRA DEFINITIONS
# --------------------------------------------------
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

CHAKRA_COLORS = {
    "Root (Muladhara)": (220, 38, 38),
    "Sacral (Svadhisthana)": (249, 115, 22),
    "Solar Plexus (Manipura)": (234, 179, 8),
    "Heart (Anahata)": (34, 197, 94),
    "Throat (Vishuddha)": (59, 130, 246),
    "Third Eye (Ajna)": (79, 70, 229),
    "Crown (Sahasrara)": (168, 85, 247),
}

STATUS_SCORE = {
    "Balanced / Radiant": 100,
    "Slightly Weak": 75,
    "Blocked / Underactive": 40,
    "Overactive / Dominant": 55,
}

# --------------------------------------------------
# TEXT CLEANER
# --------------------------------------------------
def clean_txt(text: str) -> str:
    if not text:
        return ""
    text = text.replace("•", "- ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"[^\x00-\xFF]", "", text)
    return text

# --------------------------------------------------
# PREDEFINED INFO
# --------------------------------------------------
PREDEFINED_INFO = {
    "Root (Muladhara)": {
        "Balanced / Radiant": {
            "notes": "Grounded, safe, present in the body. Money and home energy are stable.",
            "remedies": "Continue grounding, mindful walks, red-color energy and money gratitude.",
        },
        "Slightly Weak": {
            "notes": "Mild insecurity about money/safety, a little rushing in life.",
            "remedies": "Walk barefoot, chant LAM 108x, Ho'oponopono for parents/lineage.",
        },
        "Blocked / Underactive": {
            "notes": "Feeling unsafe, overthinking about survival, lower-back/leg fatigue.",
            "remedies": "Do Root Chakra meditation daily, money forgiveness, physical grounding.",
        },
        "Overactive / Dominant": {
            "notes": "Too much control, anger bursts, rigid around family/money.",
            "remedies": "Slow breathing, trust practices, yin yoga, soften control.",
        },
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": {
            "notes": "Creative, emotionally expressive, open to pleasure and relationships.",
            "remedies": "Dance, water meditation, creative expression.",
        },
        "Slightly Weak": {
            "notes": "Little guilt, emotional waves, may postpone joy.",
            "remedies": "Ho'oponopono for past partners, mirror work, womb blessing.",
        },
        "Blocked / Underactive": {
            "notes": "Suppressed emotion, relationship blocks, difficulty receiving.",
            "remedies": "Womb healing, sacral Reiki, self-nurture ritual, art/dance.",
        },
        "Overactive / Dominant": {
            "notes": "Emotional dependency, drama loops, intensity in relationships.",
            "remedies": "Boundaries, emotional detox, self-love affirmations.",
        },
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": {
            "notes": "Confident, speaks needs clearly, takes action.",
            "remedies": "Power pose, gratitude before tasks, citrine work.",
        },
        "Slightly Weak": {
            "notes": "Procrastination, some self-doubt, low motivation.",
            "remedies": "Breath of fire, success journaling, 3 wins a day.",
        },
        "Blocked / Underactive": {
            "notes": "People pleasing, fear of visibility, indecision.",
            "remedies": "Solar breathing, visibility challenge, burn old identity.",
        },
        "Overactive / Dominant": {
            "notes": "Overworking, control, anger, burnout.",
            "remedies": "Cooling breath, rest days, forgiveness, delegate.",
        },
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": {
            "notes": "Loving, compassionate, peaceful, grateful.",
            "remedies": "Green light meditation, heart appreciation.",
        },
        "Slightly Weak": {
            "notes": "Occasional loneliness, fear to receive.",
            "remedies": "Self hug, forgiveness letters, green color therapy.",
        },
        "Blocked / Underactive": {
            "notes": "Grief, heartbreak, rejection, resentment.",
            "remedies": "108x Ho'oponopono, heart Reiki, rose-quartz meditation.",
        },
        "Overactive / Dominant": {
            "notes": "Overgiving, mothering, guilt after saying no.",
            "remedies": "Receive more, boundaries, let others give to you.",
        },
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": {
            "notes": "Clear expression, confident voice, authentic sharing.",
            "remedies": "Blue light visualization, chanting, journaling.",
        },
        "Slightly Weak": {
            "notes": "Hesitation to speak truth, fear of judgment.",
            "remedies": "Mirror talk, 'My voice matters', talk to safe person.",
        },
        "Blocked / Underactive": {
            "notes": "Unspoken truth, throat tightness, suppressed emotion.",
            "remedies": "Singing therapy, voice-note release, emotional expression.",
        },
        "Overactive / Dominant": {
            "notes": "Talking too much, dominating calls, gossip.",
            "remedies": "Mindful silence, blue stones, pause-before-speak ritual.",
        },
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": {
            "notes": "Intuitive, sees patterns, calm mind.",
            "remedies": "Meditation, candle gazing, dream journaling.",
        },
        "Slightly Weak": {
            "notes": "Mild confusion, too much screen.",
            "remedies": "Third-eye breathing, reduce screens, nature time.",
        },
        "Blocked / Underactive": {
            "notes": "Overthinking, self-doubt, no clear direction.",
            "remedies": "Trust practice, guided visualization, surrender journaling.",
        },
        "Overactive / Dominant": {
            "notes": "Too many ideas, mental exhaustion, floating.",
            "remedies": "Grounding, root work, simple daily routine.",
        },
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": {
            "notes": "Spiritually connected, peaceful, gratitude.",
            "remedies": "Silence, prayer, seva.",
        },
        "Slightly Weak": {
            "notes": "Some doubt or disconnection from Divine.",
            "remedies": "White light meditation, gratitude, chanting.",
        },
        "Blocked / Underactive": {
            "notes": "Loss of purpose, spiritual fatigue, 'why me' feeling.",
            "remedies": "Daily prayer, gratitude journal, crown Reiki.",
        },
        "Overactive / Dominant": {
            "notes": "Too much in upper chakras, not grounded in life.",
            "remedies": "Earthing, grounding meals, body movement.",
        },
    },
}

CRYSTAL_REMEDIES = {
    "Root (Muladhara)": {
        "Balanced / Radiant": "Red Jasper / Lava Rock. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Slightly Weak": "Black Tourmaline, Hematite. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Blocked / Underactive": "Obsidian, 7-Chakra bracelet. Visit: https://myaurabliss.com/product/lava-rock-7-chakra-strand-bracelet/",
        "Overactive / Dominant": "Smoky Quartz to soften. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": "Carnelian, Peach Moonstone. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Slightly Weak": "Carnelian bracelet, Sunstone. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Blocked / Underactive": "Peach Moonstone, Rose Quartz. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Overactive / Dominant": "Moonstone, Amethyst. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": "Citrine, Tiger Eye. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Slightly Weak": "Citrine tumble, Pyrite. Visit: https://myaurabliss.com/product/natural-citrine-bracelet/",
        "Blocked / Underactive": "Golden calcite, Tiger eye. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Overactive / Dominant": "Yellow calcite + Lepidolite. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": "Rose Quartz, Green Aventurine. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Slightly Weak": "Rose Quartz bracelet. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Blocked / Underactive": "Malachite, Rhodochrosite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Overactive / Dominant": "Pink Opal, Amethyst. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": "Blue Lace Agate, Aquamarine. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Slightly Weak": "Sodalite, Amazonite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Blocked / Underactive": "Lapis pendant. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Overactive / Dominant": "Celestite, Blue calcite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": "Amethyst, Lapis. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Slightly Weak": "Fluorite, Labradorite. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Blocked / Underactive": "Chevron Amethyst. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Overactive / Dominant": "Obsidian + Amethyst. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": "Clear Quartz, Selenite. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Slightly Weak": "Selenite bowl, Angel aura. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Blocked / Underactive": "Clear Quartz point, Crown kit. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Overactive / Dominant": "Smoky Quartz + Selenite. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
    },
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def download_logo():
    # safe download; if it fails, we silently continue
    if os.path.exists(LOGO_FILE):
        return
    try:
        import requests
        r = requests.get(LOGO_URL, timeout=8)
        if r.status_code == 200:
            with open(LOGO_FILE, "wb") as f:
                f.write(r.content)
    except Exception:
        pass


def build_quick_reading(chakras: dict) -> str:
    """Builds a more detailed 'Quick Reading' paragraph based on which chakras are weak/blocked."""
    blocked_parts = []
    weak_parts = []
    overactive_parts = []

    for ch, info in chakras.items():
        stt = info["status"]
        if stt == "Blocked / Underactive":
            blocked_parts.append(ch)
        elif stt == "Slightly Weak":
            weak_parts.append(ch)
        elif stt == "Overactive / Dominant":
            overactive_parts.append(ch)

    lines = []
    if not blocked_parts and not weak_parts and not overactive_parts:
        return "All 7 chakras are currently flowing well. Maintain your present rituals, keep your emotions clean, and continue crystal support weekly."

    if blocked_parts:
        lines.append(
            "The following chakras are showing energy blocks or past emotional residue: "
            + ", ".join(blocked_parts)
            + ". This usually happens when we carry old stories, fear, or unprocessed pain in those areas."
        )
    if weak_parts:
        lines.append(
            "These chakras are a little under-energized or not used enough: "
            + ", ".join(weak_parts)
            + ". Activate them with daily movement, color therapy and breathwork."
        )
    if overactive_parts:
        lines.append(
            "These chakras are working too hard or compensating for another area: "
            + ", ".join(overactive_parts)
            + ". Soften them with grounding, slow breathing and better boundaries."
        )

    lines.append(
        "Start with the root or the lowest blocked chakra first, then move upwards. Use the crystal suggestions given in this report and pair it with 108x Ho'oponopono on the main person/event connected to that chakra."
    )
    return " ".join(lines)


def build_follow_up_text() -> str:
    return (
        "1) Day 1-2: Chakra awareness – 7 to 11 minutes morning meditation (Root to Crown). "
        "2) Day 3-4: Emotional cleaning – journal on 'Who or what am I still holding in this chakra?' and do 108x Ho'oponopono. "
        "3) Day 5: Crystal activation – wear / hold / place the suggested MyAuraBliss crystal on the body for 11 minutes. "
        "4) Day 6: Relationship repair – speak your truth to at least one person (Throat/Heart). "
        "5) Day 7: Integration – repeat the chakra meditation and note the shift. "
        "Track progress inside Soulful Academy app / workbook."
    )


def build_affirmations() -> str:
    return (
        "I am safe in my body. "
        "I allow myself to receive love, support and money. "
        "My inner power is gentle and firm. "
        "My heart forgives and moves forward. "
        "My voice is heard. "
        "My mind is clear. "
        "I am divinely guided and supported."
    )


# --------------------------------------------------
# PDF
# --------------------------------------------------
def make_pdf(data):
    download_logo()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    chakras = data["chakras"]
    # score calc
    chakra_scores = {}
    blocked = 0
    for ch, info in chakras.items():
        s = info["status"]
        score = STATUS_SCORE.get(s, 60)
        chakra_scores[ch] = score
        if s == "Blocked / Underactive":
            blocked += 1
    blocked_pct = round((blocked / 7.0) * 100, 1)

    # ---------- PAGE 1 ----------
    pdf.add_page()
    # header strip
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 15, "F")

    # logo (if downloaded)
    if os.path.exists(LOGO_FILE):
        try:
            pdf.image(LOGO_FILE, x=10, y=2, w=14)
        except Exception:
            pass

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(28, 3)
    pdf.cell(0, 6, clean_txt("Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_txt("Chakra & Crystal Healing Report"), ln=True)

    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt(f"Client: {data['client_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Gender: {data['gender']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Date: {data['date']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Healer: {data['coach_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Intent: {data['goal']}"), ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Overall Chakra Health"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, clean_txt(f"Blocked chakras: {blocked} of 7 ({blocked_pct}%)"), ln=True)

    # bars
    y = pdf.get_y() + 2
    max_bar = 120
    for ch in CHAKRAS:
        score = chakra_scores[ch]
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_xy(15, y)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt(ch), ln=0)
        pdf.set_fill_color(r, g, b)
        pdf.rect(75, y + 1, max_bar * (score / 100.0), 4, "F")
        pdf.set_xy(165, y)
        pdf.cell(0, 5, clean_txt(f"{score}%"), ln=1)
        y += 7

    # quick reading
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Quick Reading"), ln=True)
    pdf.set_font("Arial", "", 9)
    qr_text = build_quick_reading(chakras)
    pdf.multi_cell(0, 5, clean_txt(qr_text))

    # ---------- PAGE 2: SUMMARY ----------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Chakra Summary (Coach View)"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, clean_txt("Use this to explain the current energy story to the client. Focus first on the root-most blocked chakra, then move upwards."))

    for ch in CHAKRAS:
        info = chakras[ch]
        status = info["status"]
        crystal_line = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
        if "Visit:" in crystal_line and len(crystal_line) > 120:
            before, after = crystal_line.split("Visit:", 1)
            crystal_line = before.strip() + " Visit: " + after.strip()[:75] + " ..."
        r, g, b = CHAKRA_COLORS[ch]
        pdf.ln(2)
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt("Energy Status: " + status), ln=True)
        pdf.multi_cell(0, 5, clean_txt("Crystal Suggestion: " + crystal_line))

    # ---------- PAGE 3 & 4: DETAILED ----------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "", 10)

    for ch in CHAKRAS:
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance (contd.)"), ln=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)

        info = chakras[ch]
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, clean_txt("Status: " + info["status"]), ln=True)
        pdf.multi_cell(0, 5, clean_txt("Notes / Symptoms: " + info["notes"]))
        pdf.multi_cell(0, 5, clean_txt("Energy Remedies: " + info["remedies"]))
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, clean_txt("Crystal Remedies: " + info["crystals"]))
        pdf.ln(2)

    # ---------- PAGE 5: FOLLOW-UP ----------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Follow-up and Home Practice"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["follow_up"]))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Affirmations for Client"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["affirmations"]))

    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Crystal Support from MyAuraBliss"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt("Visit https://myaurabliss.com and choose the bracelet / crystal set for the chakras that showed Blocked or Overactive. Wear it daily for 21 days, cleanse it every full moon, and charge it with the affirmation given above."))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, clean_txt("Generated by Soulful Academy | What You Seek is Seeking You."))

    return pdf.output(dest="S").encode("latin-1", "ignore")


# --------------------------------------------------
# EMAIL (kept, but won’t crash if no secrets)
# --------------------------------------------------
def send_email_with_pdf(to_email: str, pdf_bytes: bytes, filename: str, client_name: str):
    try:
        import smtplib
        from email.message import EmailMessage
    except Exception:
        st.warning("Email libraries not available on this runtime.")
        return

    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
    except Exception:
        st.warning("Add email_user and email_pass in Streamlit secrets to send emails.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"Chakra & Crystal Report for {client_name}"
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content("Your Soulful Chakra & Crystal report is attached.")
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

    st.success("Report emailed successfully.")


# --------------------------------------------------
# MAIN UI
# --------------------------------------------------
def main():
    # show logo in UI
    st.image(LOGO_URL, width=180)
    st.title("Soulful Academy – Chakra + Crystal Scanning")
    st.caption("A diagnostic template for your clients. Fill → download → email.")

    c1, c2, c3 = st.columns(3)
    with c1:
        client_name = st.text_input("Client Name", "")
    with c2:
        coach_name = st.text_input("Coach / Healer", "Rekha Babulkar")
    with c3:
        date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))

    gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True)
    goal = st.text_input("Client Intent / Focus", "Relationship healing / Money flow / Health")

    st.markdown("---")
    st.subheader("Chakra Observations")

    chakra_data = {}
    for ch in CHAKRAS:
        with st.expander(ch, expanded=(ch == "Root (Muladhara)")):
            status_key = f"{ch}_status"
            notes_key = f"{ch}_notes"
            remedies_key = f"{ch}_remedies"
            crystals_key = f"{ch}_crystals"
            prev_key = f"{ch}_prev"

            if status_key not in st.session_state:
                st.session_state[status_key] = STATUS_OPTIONS[0]
            if prev_key not in st.session_state:
                st.session_state[prev_key] = st.session_state[status_key]

            status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=status_key)

            # auto update when status changes
            if st.session_state[prev_key] != status:
                st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
                st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
                st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
                st.session_state[prev_key] = status

            if notes_key not in st.session_state:
                st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            if remedies_key not in st.session_state:
                st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            if crystals_key not in st.session_state:
                st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")

            notes = st.text_area(f"Notes / Symptoms – {ch}", st.session_state[notes_key], key=notes_key)
            remedies = st.text_area(f"Remedies – {ch}", st.session_state[remedies_key], key=remedies_key)
            crystals = st.text_area(f"Crystal Remedies – {ch}", st.session_state[crystals_key], key=crystals_key)

            chakra_data[ch] = {
                "status": status,
                "notes": notes,
                "remedies": remedies,
                "crystals": crystals,
            }

    st.markdown("---")
    st.subheader("Session Summary")
    follow_up = st.text_area("Follow-up Plan", build_follow_up_text())
    affirmations = st.text_area("Affirmations", build_affirmations())

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        generate_btn = st.button("Create & Download PDF", use_container_width=True)
    with col2:
        email_to = st.text_input("Email report to", "")
        email_btn = st.button("Send PDF to Email", use_container_width=True)

    if generate_btn or email_btn:
        if not client_name:
            st.error("Please enter client name.")
        else:
            payload = {
                "client_name": client_name,
                "gender": gender,
                "coach_name": coach_name,
                "date": date_val,
                "goal": goal,
                "chakras": chakra_data,
                "follow_up": follow_up,
                "affirmations": affirmations,
            }
            pdf_bytes = make_pdf(payload)

            if generate_btn:
                st.success("PDF ready. Download below.")
                st.download_button(
                    "Download Chakra Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{client_name}_chakra_report.pdf",
                    mime="application/pdf"
                )

            if email_btn:
                if not email_to:
                    st.error("Please enter an email.")
                else:
                    send_email_with_pdf(email_to, pdf_bytes, f"{client_name}_chakra_report.pdf", client_name)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("App crashed. See details below.")
        st.exception(e)
