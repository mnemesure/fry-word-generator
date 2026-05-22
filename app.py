import streamlit as st
import random
from datagetter import get_list_names, get_words_from_list

# Page configuration
st.set_page_config(
    page_title="Fry Word Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Fry Word List Generator")
st.write("Select one or multiple Fry word lists and generate random words from each.")

# Sidebar for list selection
st.sidebar.header("Configuration")

# Get available lists
available_lists = get_list_names()

# Multi-select for word lists
selected_lists = st.sidebar.multiselect(
    "Select word lists:",
    available_lists,
    default=[available_lists[0]] if available_lists else []
)

if not selected_lists:
    st.warning("⚠️ Please select at least one word list.")
    st.stop()

# For each selected list, let user choose how many words
st.sidebar.subheader("Words per list")

word_counts = {}
errors = []

for list_name in selected_lists:
    total_words = len(get_words_from_list(list_name))
    count = st.sidebar.number_input(
        f"{list_name} (max: {total_words}):",
        min_value=1,
        value=min(10, total_words),
        key=f"input_{list_name}"
    )
    
    # Validate
    if count > total_words:
        errors.append(f"❌ {list_name}: {count} words requested, but only {total_words} available.")
        word_counts[list_name] = None
    else:
        word_counts[list_name] = count

# Display errors if any
if errors:
    for error in errors:
        st.sidebar.error(error)
    st.stop()

# Generate button
if st.sidebar.button("🎲 Generate Words", use_container_width=True):
    st.divider()
    
    # Generate random words from each list
    all_generated = {}
    total_words_generated = 0
    
    for list_name in selected_lists:
        words = get_words_from_list(list_name)
        num_words = word_counts[list_name]
        random_words = random.sample(words, num_words)
        all_generated[list_name] = random_words
        total_words_generated += num_words
    
    # Display results
    st.success(f"✓ Generated {total_words_generated} words!")
    st.divider()
    
    # Show results in columns for each list
    cols = st.columns(len(selected_lists))
    
    for col, list_name in zip(cols, selected_lists):
        with col:
            st.subheader(list_name)
            # Display words in boxes
            words = all_generated[list_name]
            word_cols = st.columns(2)
            for idx, word in enumerate(words):
                with word_cols[idx % 2]:
                    st.info(f"**{word.upper()}**", icon="📝")
    
    st.divider()
    
    # Show all words in a single line for easy copying
    all_words = []
    for list_name in selected_lists:
        all_words.extend(all_generated[list_name])
    random.shuffle(all_words)
    
    st.subheader("All words (shuffled):")
    st.code(" ".join(all_words))

