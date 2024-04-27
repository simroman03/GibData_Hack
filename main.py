import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(
        page_title="GibData",
)
def upload():    
    st.set_page_config(
        page_title="Course Recommender",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # st.title("Компетентностный подбор образовательных курсов")
    st.markdown("# :rainbow[Компетентностный подбор образовательных курсов [GibData]]")
    st.empty().markdown("&nbsp;")
    
    st.empty().markdown('''### {}'''.format("Дополнительные фильтры"), 
                        help='Choose either 1 or 2 but not both. If both are selected 1 will be used.')

    title_header_empty = st.empty()
    title_choice_empty = st.empty()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        directions_header_empty = st.empty()
        directions_choice_empty = st.empty()

    with col2:
        knowledge_header_empty = st.empty()
        knowledge_choice_empty = st.empty()

    with col3:
        keys_header_empty = st.empty()
        keys_choice_empty = st.empty()

    directions_header_empty.markdown('''##### Направления''', help='Choose either 1 or 2.')
    directions_choice_empty.selectbox("directions", label_visibility="collapsed",
                                   options=['Все направления',
                                            'ИТ',
                                            'Программирование',
                                            'Дизайн',
                                            'Маркетинг',
                                            'Аналитика',
                                            'Тестирование',
                                            'ИТ-архитектура',
                                            'Машинное обучение',
                                            'Менеджмент', 
                                            'Игры',
                                            'Blockchain',
                                            'Кино и музыка'], key='directions')

    knowledge_header_empty.markdown('''##### Знания на выходе''', help='Choose either 1 or 2.')
    knowledge_choice_empty.selectbox("knowledge", label_visibility="collapsed",
                                     options=['Junior',
                                            'Middle',
                                            'Middle+'], 
                                     key='knowledge',)

    keys_header_empty.markdown('''##### Ключевые слова''', help='Choose either 1 or 2.')
    keys_choice_empty.multiselect('''##### Ключевые слова''',
                                  ["Data Scientist", "PyTorch", "CV", "Аналитика"],
                                  label_visibility='collapsed',
                                  placeholder="Выберите ключевые слова...",)

    cols = st.columns(10)
    with cols[0]:
        free_choice_empty = ui.switch(default_checked=True, label="Бесплатные", key="switch1")
    with cols[1]:
        action_choice_empty = ui.switch(default_checked=True, label="Со скидкой", key="switch2")
    
    ms = st.multiselect('''##### Пройденные курсы''', 
                        ["Специалист по внедрению Искуственного Интеллекта", 
                         "Специалист по внедрению Искуственного Интеллекта"], 
                        placeholder="Выберите курсы, которые уже прошли...",)
    if 1 in ms and 2 in ms:
        ms.remove(2)

    cols = st.columns(10)
    with cols[0]:
        recommend_button = ui.button(text="Рекомендовать", 
                                     key="styled_btn_tailwind", 
                                     className="bg-orange-500 text-white",)
    with cols[1]:
        delete_button = ui.button(text="Сбросить", key="d", className="grey")

    if recommend_button and not delete_button:
    
        st.empty().markdown('''### {}'''.format("Рекомендованные курсы"), 
                            help='Choose either 1 or 2 but not both. If both are selected 1 will be used.')
        cols = st.columns(3)
        with cols[0]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card1")
        with cols[1]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card2")
        with cols[2]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card3")
    
        cols = st.columns(3)
        with cols[0]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card4")
        with cols[1]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card5")
        with cols[2]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card6")
                
if __name__ == "__main__":
       upload()
