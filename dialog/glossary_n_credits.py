import streamlit as st

@st.dialog('Glossary & Credits')
def dialog_glossary_n_credits(glossary):

    st.write('### Glossary')
    st.write(glossary)

    st.markdown('''
        ### Credits
        - Architecture: **Jee Lee**
        - Code: **Yongjun Kim** ([GitHub](https://github.com/kimiroo))
    ''')