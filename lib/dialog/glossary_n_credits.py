import streamlit as st

@st.dialog('Glossary & Credits')
def dialog_glossary_n_credits(glossary):

    st.write('### Glossary')
    st.write(glossary)

    st.markdown('''
        ### Credits
        - Architecture: **Jee Lee** (your@email.here)
        - Code: **Yongjun Kim** (me@yongjun.kim)
    ''')