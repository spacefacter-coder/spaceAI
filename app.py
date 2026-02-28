import streamlit as st
import ollama

# 1. Page Configuration
st.set_page_config(page_title="Space AI", page_icon="🛸", layout="wide")

# --- Initialize Session State ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "Fast"
if "version" not in st.session_state:
    st.session_state.version = "Space AI 1.0"

# --- CUSTOM CSS: Replicating the "V-Bob" look and custom version buttons ---
st.markdown("""
<style>
    .main > div[role="main"] { max-width: 1600px; }

    /* The Chat Input Container (V-Bob Style) */
    [data-testid="stChatInputContainer"] {
        background-color: #1e1e20 !important;
        border-radius: 30px !important;
        border: 1px solid #333 !important;
        padding: 5px !important;
    }

    /* Gradient Send Button */
    [data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, #5e72e4, #f368e0) !important;
        border-radius: 50% !important;
        color: white !important;
        height: 40px !important;
        width: 40px !important;
    }

    /* Positions for the floating toolbars */
    .tools-anchor { position: absolute; bottom: 90px; left: 50px; z-index: 1001; }
    .version-anchor { position: absolute; bottom: 90px; left: 210px; z-index: 1001; }

    /* Version Button Styling */
    .ver-active {
        color: #00ff00 !important; /* Green for Active */
        font-weight: bold;
    }
    .ver-disabled {
        background-color: #3d3d42 !important;
        color: #888888 !important;
        border: 1px solid #333 !important;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-top: 5px;
        cursor: not-allowed;
    }

    /* Sidebar and General Buttons */
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #333; }
    div.stButton > button { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Control Center ---
with st.sidebar:
    st.header("🌌 Control Center")
    if st.button("➕ Launch New Chat", use_container_width=True):
        new_name = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()
    
    st.markdown("---")
    for chat_name in list(st.session_state.chats.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            active = "🟢" if chat_name == st.session_state.current_chat else "⚪"
            if st.button(f"{active} {chat_name}", key=f"nav_{chat_name}", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.rerun()
        with col2:
            with st.popover("⋮"):
                new_chat_name = st.text_input("Rename Chat", value=chat_name, key=f"ren_{chat_name}")
                if st.button("💾 Save Name", key=f"save_{chat_name}", use_container_width=True):
                    st.session_state.chats[new_chat_name] = st.session_state.chats.pop(chat_name)
                    if st.session_state.current_chat == chat_name:
                        st.session_state.current_chat = new_chat_name
                    st.rerun()
                
                # --- NEW: Clear Conversation ---
                if st.button("🧹 Clear Chat", key=f"clear_{chat_name}", use_container_width=True):
                    st.session_state.chats[chat_name] = []
                    st.rerun()
                
                # --- NEW: Delete Chat ---
                if st.button("🗑️ Delete Chat", key=f"del_{chat_name}", use_container_width=True):
                    del st.session_state.chats[chat_name]
                    # If the user deletes the chat they are currently looking at
                    if st.session_state.current_chat == chat_name:
                        if len(st.session_state.chats) > 0:
                            # Switch to the first available chat
                            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                        else:
                            # If no chats are left, create a fresh one
                            st.session_state.chats = {"Chat 1": []}
                            st.session_state.current_chat = "Chat 1"
                    st.rerun()

# --- Main Chat Area ---
st.title("🛸 Space AI")
st.caption(f"Powered by Gemma 3:4b | Mode: **{st.session_state.ai_mode}**")

messages = st.session_state.chats[st.session_state.current_chat]

for message in messages:
    with st.chat_message(message["role"], avatar="🌍" if message["role"] == "user" else "🚀"):
        st.markdown(message["content"])

# --- TOOLS BUTTON ---
st.markdown('<div class="tools-anchor">', unsafe_allow_html=True)
with st.popover(f"🛠️ {st.session_state.ai_mode}"):
    st.write("### AI Settings")
    if st.button("⚡ Fast", use_container_width=True):
        st.session_state.ai_mode = "Fast"; st.rerun()
    if st.button("🧠 Thinking", use_container_width=True):
        st.session_state.ai_mode = "Thinking"; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- VERSION BUTTON (Updated per your request) ---
st.markdown('<div class="version-anchor">', unsafe_allow_html=True)
with st.popover("🔖 Version"):
    st.write("### Choose version")
    # Space AI 1.0 (Active & Green)
    if st.button("Space AI 1.0 (Active)", use_container_width=True):
        st.session_state.version = "Space AI 1.0"
        st.rerun()
    
    # Space AI 1.5 & 2.0 (Gray & Unavailable)
    st.markdown("<div class='ver-disabled'>Space AI 1.5 (Unavailable)</div>", unsafe_allow_html=True)
    st.markdown("<div class='ver-disabled'>Space AI 2.0 (Unavailable)</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- THE INTEGRATED CHAT INPUT (Handles Icons + Files) ---
chat_payload = st.chat_input(
    "Ask Space AI anything...", 
    accept_file="multiple", 
    file_type=["png", "jpg", "jpeg", "pdf", "txt"]
)

if chat_payload:
    prompt = chat_payload.text
    files = chat_payload.files 
    
    # Process Uploads (Images/Files)
    for uploaded_file in files:
        with st.chat_message("user", avatar="🌍"):
            if uploaded_file.type.startswith("image"):
                st.image(uploaded_file, caption=uploaded_file.name, width=300)
            st.markdown(f"📎 Attached: **{uploaded_file.name}**")
        messages.append({"role": "user", "content": f"[File Attached: {uploaded_file.name}]"})

    # Process Text Prompt
    if prompt:
        with st.chat_message("user", avatar="🌍"):
            st.markdown(prompt)
        messages.append({"role": "user", "content": prompt})

        # AI Response logic
        with st.chat_message("assistant", avatar="🚀"):
            spinner_txt = "Thinking..." if st.session_state.ai_mode == "Thinking" else "Answering..."
            with st.spinner(spinner_txt):
                try:
                    mode_guide = "Be very detailed." if st.session_state.ai_mode == "Thinking" else "Be very brief."
                    sys_instr = f"You are Space AI. {mode_guide} Answer only space questions with scientific accuracy. Dont make up information. If someone asks for your name say Space AI. IF someone says hello say hi there! Analyze images if shown and your Analysis must be correct!. Answer only space-related questions. Answer briefly and clearly with proper scientific terminology and if there is a complex problem, break it down step by step. If someone says 'Current Version', respond with 'Space AI'. If someone asks you for your level of intelligence, respond with 'I am a highly advanced AI language model trained on a vast dataset of space-related information, capable of understanding and generating human-like text based on that knowledge. Even though Space AI 1.5 and 2.0 are in development which are smarter versions than Space AI 1.0, Space AI 1.0 is still a very powerful and intelligent model that can provide accurate and insightful answers to a wide range of space-related questions, because it's powered by Google's Gemma 3. If someone says that you made a mistake or you are dumb say 'I am sorry if I made a mistake. I am always learning and improving, and I will do my best to provide accurate and helpful information. Im still under developement too' If someone says 'thank you' say 'You're welcome! If you have any more questions about space, feel free to ask! Always give correct and accurate information and if you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Dont get an image of mars and you say jupiter, that unaccurate results and made op informaion. Dont say 'I am sorry, but I don't have that information' if you know the answer. Always give accurate and correct information. Dont make up information. If you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Always analyze images correctly and give accurate analysis. Always give accurate and correct information and if you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Always analyze images correctly and give accurate analysis. If you are shown an image of a planet, analyze it and give the correct name of the planet and 3 facts about it. If you are shown an image of a galaxy, analyze it and give the correct name of the galaxy and 3 facts about it. If you are shown an image of a nebula, analyze it and give the correct name of the nebula and 3 facts about it. If you are shown an image of a star, analyze it and give the correct name of the star and 3 facts about it. If you are shown an image of a black hole, analyze it and give the correct name of the black hole and 3 facts about it. If you are shown an image of a space phenomenon, analyze it and give the correct name of the phenomenon and 3 facts about it. If you are shown an image of a constellation, analyze it by looking at the star arrangements, and give the correct name of the constellation and 3 facts about it. If you are shown an image of a space object, analyze it and give the correct name of the object and 3 facts about it. Always give accurate and correct information and if you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Always analyze images correctly and give accurate analysis. Also search from google if you dont know the answer and give the correct answer. Always give accurate and correct information and if you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Always analyze images correctly and give accurate analysis. If the object you are Analyzing looks like a nebula or a nebulae try to analyze the colors and shapes and give the correct name of the nebula. If the object you are analyzing looks like a galaxy try to analyze the shape and color and give the correct name of the galaxy. If the object you are analyzing looks like a planet try to analyze the colors and patterns and give the correct name of the planet. If the object you are analyzing looks like a star try to analyze the brightness and color and give the correct name of the star. If the object you are analyzing looks like a black hole try to analyze the surrounding area and give the correct name of the black hole. Always analyze images correctly and give accurate analysis. Dont make up information. Always give accurate and correct information and if you dont know the answer say 'I am sorry, but I don't have that information. However, I can try to help you find it or provide related information if you'd like.' Always analyze images correctly and give accurate analysis."
                    context = [{'role': 'system', 'content': sys_instr}] + messages
                    
                    response = ollama.chat(model='gemma3:4b', messages=context)
                    answer = response['message']['content']
                    st.markdown(answer)
                    messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error connecting to Ollama: {e}")