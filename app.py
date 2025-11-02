import streamlit as st
from fpdf import FPDF
import datetime
import os
import requests
import re
import smtplib
from email.message import EmailMessage

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Soulful Academy – Chakra + Crystal Report",
    page_icon="🪬",
    layout="centered"
)

# -------------------- CONSTANTS --------------------
LOGO_URL = "https://ik.imagekit.io/86edsgbur/Untitled%20design%20(73)%20(3)%20(1).jpg?updatedAt=1759258123716"
LOGO_FILE = "soulful_logo.jpg"

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

# chakra colors for PDF bars
CHAKRA_COLORS = {
    "Root (Muladhara)": (220, 38, 38),       # red
    "Sacral (Svadhisthana)": (249, 115, 22), # orange
    "Solar Plexus (Manipura)": (234, 179, 8),# yellow
    "Heart (Anahata)": (34, 197, 94),        # green
    "Throat (Vishuddha)": (59, 130, 246),    # blue
    "Third Eye (Ajna)": (79, 70, 229),       # indigo
    "Crown (Sahasrara)": (168, 85, 247),     # violet
}

# map energy status to score
STATUS_SCORE = {
    "Balanced / Radiant": 100,
    "Slightly Weak": 75,
    "Blocked / Underactive": 40,
    "Overactive / Dominant": 55,
}

# -------------------- CLEANER --------------------
def clean_txt(text: str) -> str:
    if not text:
        return ""
    text = text.replace("•", "- ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")
    text = text.replace("‘", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    # remove non latin
    text = re.sub(r"[^\x00-\xFF]", "", text)
    return text

# -------------------- PREDEFINED NOTES / REMEDIES --------------------
PREDEFINED_INFO = {
    "Root (Muladhara)": {
        "Balanced / Radiant": {
            "notes": "Grounded, stable, calm, connected to body and finances aligned.",
            "remedies": "Gratitude journaling, red color grounding, mindful walks."
        },
        "Slightly Weak": {
            "notes": "Mild insecurity about money or safety.",
            "remedies": "Walk barefoot, chant LAM, do Root Reiki healing."
        },
        "Blocked / Underactive": {
            "notes": "Chronic fear, instability, low energy in legs or lower back.",
            "remedies": "Red color therapy, money forgiveness, Ho'oponopono for parents."
        },
        "Overactive / Dominant": {
            "notes": "Control, anger bursts, attachment to material comfort.",
            "remedies": "Trust meditation, slow breathwork, grounding yin yoga."
        },
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": {
            "notes": "Creative, emotionally expressive, open to intimacy.",
            "remedies": "Dance therapy, water visualization, orange candle meditation."
        },
        "Slightly Weak": {
            "notes": "Mild guilt or emotional waves.",
            "remedies": "Ho'oponopono for past partners, sacral journaling."
        },
        "Blocked / Underactive": {
            "notes": "Suppressed emotions, relationship blocks, disconnection from pleasure.",
            "remedies": "Womb healing, mirror work, sacral Reiki."
        },
        "Overactive / Dominant": {
            "notes": "Emotional dependency, drama loops, over-attachment.",
            "remedies": "Boundaries, creative solitude, self love affirmations."
        },
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": {
            "notes": "Confident, decisive, action oriented.",
            "remedies": "Citrine work, power pose, gratitude before tasks."
        },
        "Slightly Weak": {
            "notes": "Procrastination, self doubt, low motivation.",
            "remedies": "Breath of fire, success journaling, power affirmations."
        },
        "Blocked / Underactive": {
            "notes": "People pleasing, fear of visibility, indecision.",
            "remedies": "Solar breathing, mirror visibility practice."
        },
        "Overactive / Dominant": {
            "notes": "Overwork, aggression, control, burnout.",
            "remedies": "Cooling breath, forgiveness, balanced rest."
        },
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": {
            "notes": "Loving, compassionate, peaceful, grateful.",
            "remedies": "Green light visualization, kindness journaling."
        },
        "Slightly Weak": {
            "notes": "Occasional loneliness or fear to receive love.",
            "remedies": "Self hug, forgiveness letters, green color therapy."
        },
        "Blocked / Underactive": {
            "notes": "Grief, heartbreak, resentment, rejection wound.",
            "remedies": "Heart Reiki, rose quartz meditation, 108x Ho'oponopono."
        },
        "Overactive / Dominant": {
            "notes": "Overgiving, martyr pattern, guilt after saying no.",
            "remedies": "Receiving practice, loving boundaries."
        },
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": {
            "notes": "Clear communication, confident expression.",
            "remedies": "Blue light visualization, chanting, journaling emotions."
        },
        "Slightly Weak": {
            "notes": "Hesitation to speak, fear of judgment.",
            "remedies": "Mirror talk, 'My voice matters', short voice practice."
        },
        "Blocked / Underactive": {
            "notes": "Unspoken truth, throat tightness, holding back.",
            "remedies": "Singing therapy, public speaking, emotional release."
        },
        "Overactive / Dominant": {
            "notes": "Talking too much, dominating or gossip.",
            "remedies": "Mindful silence, blue stones, pause before speaking."
        },
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": {
            "notes": "Intuitive, clear seeing, calm mind.",
            "remedies": "Meditation, visualization, dream journaling."
        },
        "Slightly Weak": {
            "notes": "Mild confusion or scattered thoughts.",
            "remedies": "Third eye breathing, reduce screen time."
        },
        "Blocked / Underactive": {
            "notes": "Overthinking, self doubt, cannot see path.",
            "remedies": "Trust practice, candle gazing, Ho'oponopono for clarity."
        },
        "Overactive / Dominant": {
            "notes": "Too many ideas, mental exhaustion, not grounded.",
            "remedies": "Grounding meditation, simple routines."
        },
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": {
            "notes": "Spiritually connected, peaceful, open to guidance.",
            "remedies": "Silence meditation, gratitude, service."
        },
        "Slightly Weak": {
            "notes": "Some doubt or disconnection from Divine.",
            "remedies": "Crown breathing, white light meditation."
        },
        "Blocked / Underactive": {
            "notes": "Loss of purpose, spiritual fatigue.",
            "remedies": "Prayer, gratitude journal, grounding spiritual rituals."
        },
        "Overactive / Dominant": {
            "notes": "Too much in upper chakras, not grounded.",
            "remedies": "Earthing, grounding meals, body work."
        },
    },
}

# -------------------- CRYSTAL REMEDIES + LINKS --------------------
CRYSTAL_REMEDIES = {
    "Root (Muladhara)": {
        "Balanced / Radiant": "Red Jasper, Lava Rock, Sulemani Hakik bracelet. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Slightly Weak": "Black Tourmaline, Hematite. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
        "Blocked / Underactive": "Obsidian, Red Jasper wand, 7 Chakra strand bracelet. Visit: https://myaurabliss.com/product/lava-rock-7-chakra-strand-bracelet/",
        "Overactive / Dominant": "Smoky Quartz and Hematite. Visit: https://myaurabliss.com/product-category/chakra/root-chakra/",
    },
    "Sacral (Svadhisthana)": {
        "Balanced / Radiant": "Carnelian, Peach Moonstone, Orange Calcite. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Slightly Weak": "Carnelian bracelet and Sunstone. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Blocked / Underactive": "Peach Moonstone and Rose Quartz. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
        "Overactive / Dominant": "Moonstone and Amethyst to cool emotions. Visit: https://myaurabliss.com/product-category/chakra/sacral-chakra/",
    },
    "Solar Plexus (Manipura)": {
        "Balanced / Radiant": "Citrine, Tiger Eye, 7 Chakra bracelet. Visit: https://myaurabliss.com/product/natural-citrine-bracelet/",
        "Slightly Weak": "Citrine tumble and Pyrite. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Blocked / Underactive": "Golden calcite, Tiger eye. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
        "Overactive / Dominant": "Yellow calcite and Lepidolite. Visit: https://myaurabliss.com/product-category/chakra/solar-plexus-chakra/",
    },
    "Heart (Anahata)": {
        "Balanced / Radiant": "Rose Quartz heart, Green Aventurine, Rhodonite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Slightly Weak": "Rose Quartz bracelet, Prehnite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Blocked / Underactive": "Malachite, Rhodochrosite. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
        "Overactive / Dominant": "Pink Opal, Mangano calcite, Amethyst. Visit: https://myaurabliss.com/product-category/chakra/heart-chakra/",
    },
    "Throat (Vishuddha)": {
        "Balanced / Radiant": "Blue Lace Agate, Aquamarine. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Slightly Weak": "Sodalite and Amazonite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Blocked / Underactive": "Lapis Lazuli tower, Aquamarine pendant. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
        "Overactive / Dominant": "Celestite and Blue calcite. Visit: https://myaurabliss.com/product-category/chakra/throat-chakra/",
    },
    "Third Eye (Ajna)": {
        "Balanced / Radiant": "Amethyst and Lapis Lazuli. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Slightly Weak": "Fluorite tower, Labradorite. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Blocked / Underactive": "Chevron Amethyst, Sodalite. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
        "Overactive / Dominant": "Black Obsidian and Amethyst. Visit: https://myaurabliss.com/product-category/chakra/third-eye-chakra/",
    },
    "Crown (Sahasrara)": {
        "Balanced / Radiant": "Clear Quartz, Selenite wand. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Slightly Weak": "Selenite bowl, Angel aura quartz. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Blocked / Underactive": "Clear Quartz point on crown. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
        "Overactive / Dominant": "Smoky Quartz and Selenite. Visit: https://myaurabliss.com/product-category/chakra/crown-chakra/",
    },
}

# -------------------- DOWNLOAD LOGO --------------------
def download_logo():
    if not os.path.exists(LOGO_FILE):
        try:
            r = requests.get(LOGO_URL, timeout=10)
            if r.status_code == 200:
                with open(LOGO_FILE, "wb") as f:
                    f.write(r.content)
        except:
            pass

# -------------------- EMAIL SENDER --------------------
def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_bytes: bytes, filename: str):
    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
    except Exception:
        st.warning("Email not sent: add email_user and email_pass in Streamlit secrets.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content(body)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

# -------------------- PDF CREATOR (5 PAGES) --------------------
def make_pdf(data):
    download_logo()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    chakras = data["chakras"]

    # compute scores
    chakra_scores = {}
    blocked_count = 0
    for ch, info in chakras.items():
        status = info["status"]
        score = STATUS_SCORE.get(status, 60)
        chakra_scores[ch] = score
        if status == "Blocked / Underactive":
            blocked_count += 1

    blocked_pct = round((blocked_count / 7.0) * 100, 1)

    # ------------- PAGE 1: COVER + GRAPH -------------
    pdf.add_page()
    pdf.set_fill_color(139, 92, 246)
    pdf.rect(0, 0, 210, 18, "F")
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 18, 6, 275, "F")
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=2, w=16)
    pdf.set_xy(30, 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 7, clean_txt("Soulful Academy"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, clean_txt("Chakra and Crystal Healing Report"), ln=True)

    pdf.ln(12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt(f"Client Name: {data['client_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Gender: {data['gender']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Date: {data['date']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Coach: {data['coach_name']}"), ln=True)
    pdf.cell(0, 6, clean_txt(f"Intent: {data['goal']}"), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Overall Chakra Health"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, clean_txt(f"Blocked chakras: {blocked_count} of 7 ({blocked_pct}%)"), ln=True)

    # draw bars
    y = pdf.get_y() + 3
    max_bar_width = 120
    for ch in CHAKRAS:
        score = chakra_scores[ch]
        bar_w = max_bar_width * (score / 100.0)
        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_xy(20, y)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, clean_txt(ch), ln=0)
        pdf.set_xy(80, y + 1)
        pdf.set_fill_color(r, g, b)
        pdf.rect(80, y + 1, bar_w, 4, "F")
        pdf.set_xy(165, y)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 5, clean_txt(f"{score}%"), ln=1)
        y += 7

    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 5, clean_txt("Quick Reading"), ln=True)
    pdf.set_font("Arial", "", 9)
    if blocked_count == 0:
        pdf.multi_cell(0, 5, clean_txt("All chakras are open and flowing. Maintain current rituals."))
    else:
        pdf.multi_cell(0, 5, clean_txt("There are some energy blocks. Focus on the chakras marked as Blocked or Overactive. Use the crystal and energy remedies suggested in the next pages."))

    # ------------- PAGE 2: SUMMARY TABLE -------------
    pdf.add_page()
    pdf.set_fill_color(236, 72, 153)
    pdf.rect(0, 0, 210, 7, "F")
    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Chakra Summary"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 6, clean_txt("Chakra"), border=1)
    pdf.cell(45, 6, clean_txt("Energy Status"), border=1)
    pdf.cell(85, 6, clean_txt("Crystal Suggestion"), border=1, ln=1)
    pdf.set_font("Arial", "", 9)
    for ch in CHAKRAS:
        info = chakras[ch]
        cryst = CRYSTAL_REMEDIES.get(ch, {}).get(info["status"], "")
        pdf.cell(60, 6, clean_txt(ch), border=1)
        pdf.cell(45, 6, clean_txt(info["status"]), border=1)
        pdf.cell(85, 6, clean_txt(cryst[:70]), border=1, ln=1)

    # ------------- PAGES 3-4: DETAILED CHAKRA PAGES -------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "", 10)

    for idx, ch in enumerate(CHAKRAS):
        info = chakras[ch]
        text_height = pdf.get_y()
        # if page is almost full, add page
        if text_height > 250:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, clean_txt("Detailed Chakra Guidance (contd.)"), ln=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)

        r, g, b = CHAKRA_COLORS[ch]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, clean_txt(ch), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, clean_txt(f"Status: {info['status']}"), ln=True)
        pdf.multi_cell(0, 5, clean_txt(f"Notes / Symptoms: {info['notes']}"))
        pdf.multi_cell(0, 5, clean_txt(f"Energy Remedies: {info['remedies']}"))
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, clean_txt(f"Crystal Remedies: {info['crystals']}"))
        pdf.ln(2)

    # ------------- PAGE 5: FOLLOW UP -------------
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Follow-up and Home Practice"), ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["follow_up"]))
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, clean_txt("Affirmations For This Client"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt(data["affirmations"]))

    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, clean_txt("Crystal Support From MyAuraBliss"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, clean_txt("Visit https://myaurabliss.com and pick the bracelet or crystal set for the chakras that showed Blocked or Overactive status in this report."))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 4, clean_txt("Generated by Soulful Academy | What You Seek is Seeking You."))

    return pdf.output(dest="S").encode("latin-1", "ignore")

# -------------------- UI (REACTIVE) --------------------
st.image(LOGO_URL, width=160)
st.title("Soulful Academy Chakra + Crystal Scanning Template")

c1, c2, c3 = st.columns(3)
with c1:
    client_name = st.text_input("Client Name", "")
with c2:
    coach_name = st.text_input("Coach / Healer", "Rekha Babulkar")
with c3:
    date_val = st.text_input("Session Date", datetime.date.today().strftime("%d-%m-%Y"))

gender = st.radio("Gender", ["Female", "Male", "Other"], horizontal=True)
goal = st.text_input("Client Intent / Focus", "Relationship Healing")

st.markdown("---")
st.subheader("Chakra Observations (dynamic)")

chakra_data = {}

for ch in CHAKRAS:
    with st.expander(ch, expanded=(ch == "Root (Muladhara)")):
        status_key = f"{ch}_status"
        notes_key = f"{ch}_notes"
        remedies_key = f"{ch}_remedies"
        crystals_key = f"{ch}_crystals"
        prev_status_key = f"{ch}_prev_status"

        if status_key not in st.session_state:
            st.session_state[status_key] = STATUS_OPTIONS[0]
        if prev_status_key not in st.session_state:
            st.session_state[prev_status_key] = st.session_state[status_key]

        status = st.selectbox(f"Energy Status – {ch}", STATUS_OPTIONS, key=status_key)

        if st.session_state[prev_status_key] != status:
            st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
            st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
            st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")
            st.session_state[prev_status_key] = status

        if notes_key not in st.session_state:
            st.session_state[notes_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("notes", "")
        if remedies_key not in st.session_state:
            st.session_state[remedies_key] = PREDEFINED_INFO.get(ch, {}).get(status, {}).get("remedies", "")
        if crystals_key not in st.session_state:
            st.session_state[crystals_key] = CRYSTAL_REMEDIES.get(ch, {}).get(status, "")

        notes = st.text_area(f"Notes / Symptoms – {ch}", value=st.session_state[notes_key], key=notes_key)
        remedies = st.text_area(f"Remedies – {ch}", value=st.session_state[remedies_key], key=remedies_key)
        crystals = st.text_area(f"Crystal Remedies – {ch}", value=st.session_state[crystals_key], key=crystals_key)

        chakra_data[ch] = {
            "status": status,
            "notes": notes,
            "remedies": remedies,
            "crystals": crystals,
        }

st.markdown("---")
st.subheader("Session Summary")
follow_up = st.text_area("Follow-up Plan", "Follow-up in 7 days. Practice chakra meditation. Wear the recommended crystal bracelet from MyAuraBliss. Do 108x Ho'oponopono on the main person or event.")
affirmations = st.text_area("Affirmations", "I am safe. I receive. My power is safe. My heart is open. I speak my truth. I trust my guidance. I am connected to the Divine.")

st.markdown("---")
st.subheader("Download or Email Report")

col_a, col_b = st.columns(2)
with col_a:
    generate_pdf = st.button("Create and Download PDF", use_container_width=True)
with col_b:
    email_to = st.text_input("Send report to email", "")
    send_email_btn = st.button("Send PDF to Email", use_container_width=True)

if generate_pdf or send_email_btn:
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
            "affirmations": affirmations
        }
        pdf_bytes = make_pdf(payload)

        if generate_pdf:
            st.success("PDF ready. Download below.")
            st.download_button(
                label="Download Chakra Report (PDF)",
                data=pdf_bytes,
                file_name=f"{client_name}_chakra_report.pdf",
                mime="application/pdf"
            )

        if send_email_btn:
            if not email_to:
                st.error("Enter an email to send.")
            else:
                send_email_with_pdf(
                    to_email=email_to,
                    subject=f"Chakra and Crystal Report for {client_name}",
                    body="Your Soulful Academy chakra and crystal report is attached.",
                    pdf_bytes=pdf_bytes,
                    filename=f"{client_name}_chakra_report.pdf"
                )
                st.success("If email credentials are set in Streamlit secrets, the report has been sent.")
