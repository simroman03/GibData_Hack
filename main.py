import streamlit as st
import streamlit_shadcn_ui as ui
import re
import ast
import json
import requests
from bs4 import BeautifulSoup
import re
import ast
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class HHParser:
    def __init__(self, url: str):
        self.url = url

    def get_vacancy_info(self, vacancy):
        vacancy_id = vacancy.get("id")
        vacancy_title = vacancy.get("name")
        vacancy_url = vacancy.get("alternate_url")
        vacancy_exp = vacancy.get("experience", {}).get("name")
        vacancy_empl = vacancy.get("employment", {}).get("name")
        company_name = vacancy.get("employer", {}).get("name")
        professional_roles = vacancy.get("professional_roles")
        salary = vacancy.get("salary")
        key_skills = vacancy.get("key_skills")
        vacancy_desc = vacancy.get("description")
        return (
                f"ID: {vacancy_id}\nНазвание: {vacancy_title}"
                + f"\nКомпания: {company_name}\nURL: {vacancy_url}"
                + f"\nОпыт: {vacancy_exp}\nЗанятость: {vacancy_empl}"
                + f"\nЗП: {salary}\nРоль:{professional_roles}"
                + f"\nКлючевые навыки: {key_skills}\n"
                + f"\nОписание: {vacancy_desc}\n"
        )

    def get_vacancy_info_from_url(self) -> str:
        vacancy_id = self.url.split("/")[-1]
        url = f"https://api.hh.ru/vacancies/{vacancy_id}"
        response = requests.get(url)
        if response.status_code == 200:
            vacancy_info = response.json()
            return self.get_vacancy_info(vacancy_info)
        else:
            return f"Request failed with status code: {response.status_code}"

    def get_name_from_hh(self, text: str) -> str:
        if "Название:" not in text:
            return ""
        name_start = text.index("Название:") + len("Название:")
        name_end = text.find("\n", name_start)
        if name_end == -1:
            name_end = len(text)
        return text[name_start:name_end].strip()

    def get_key_skils(self, text):
        if "Ключевые навыки" not in text:
            return ""
        match = re.search(r'\[.*?\]', text.split('Ключевые навыки:')[1])
        if match:
            result = match.group()
            skils = [d['name'] for d in ast.literal_eval(result)]
            return skils
        return None

    def get_job_info(self):
        job_text = self.get_vacancy_info_from_url()
        job_name = self.get_name_from_hh(job_text)
        job_key_skils = self.get_key_skils(job_text)
        job_info = [job_name] + job_key_skils
        return job_info


class GeekBrainsParser:
    def __init__(self):
        self.course_dict = {}

    def get_course_links(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            links_on_course = [link['href'] for link in links]
            pattern = r'https://gb\.ru/geek_university/.+'
            filtered_links = [link for link in links_on_course if re.match(pattern, link)]
            return filtered_links
        else:
            st.write("Ошибка при загрузке страницы:", response.status_code)
            return []

    def get_html_from_url(self, url):
        response = requests.get(url)
        return response.text

    def clean_html(self, html):
        cleaned_text = re.sub(r'<[^>]*>', '', html)  # Удаление HTML-тегов
        return cleaned_text

    def extract_text_between_phrases(self, url, start_phrase, end_phrase):
        html = self.get_html_from_url(url)
        cleaned_text = self.clean_html(html)

        start_index = cleaned_text.find(start_phrase)
        end_index = cleaned_text.find(end_phrase, start_index)

        if start_index != -1 and end_index != -1:
            extracted_text = cleaned_text[start_index + len(start_phrase):end_index].strip()
            extracted_list = extracted_text.split('\n')
            extracted_list = [line.strip() for line in extracted_list if line.strip()]
            if len(extracted_list) > 20:
                extracted_list = extracted_list[1:21]
            else:
                extracted_list = extracted_list[1:-1]
            return extracted_list
        else:
            return []

    def extract_text_after_phrase(self, url, start_phrase, limit):
        html = self.get_html_from_url(url)
        cleaned_text = self.clean_html(html)

        start_index = cleaned_text.find(start_phrase)

        if start_index != -1:
            extracted_text = cleaned_text[start_index + len(start_phrase):].strip()
            extracted_list = extracted_text.split('\n')
            extracted_list = [line.strip() for line in extracted_list if line.strip()]
            if len(extracted_list) > limit:
                extracted_list = extracted_list[:limit]
            return extracted_list
        else:
            return []

    def extract_program_track(self, url, start_phrase, end_phrase):
        html = self.get_html_from_url(url)
        cleaned_text = self.clean_html(html)

        start_index = cleaned_text.find(start_phrase)
        end_index = cleaned_text.find(end_phrase, start_index)

        if start_index != -1 and end_index != -1:
            extracted_text = cleaned_text[start_index + len(start_phrase):end_index].strip()
            extracted_list = extracted_text.split('\n')
            extracted_list = [line.strip() for line in extracted_list if line.strip()]
            return extracted_list
        else:
            return ["Не нашлось"]

    def title_and_description(self, url):
        html = self.get_html_from_url(url)
        cleaned_text = self.clean_html(html)
        soup = BeautifulSoup(html, 'html.parser')
        title = ''
        promo_text = ''
        try:
            title = re.search(r'«(.*?)»', str(soup.find('meta', property='og:title'))).group(1)
            promo_description = soup.find('div', class_='gkb-promo__description')
            promo_text = promo_description.find('p', class_='gkb-promo__text').get_text(strip=True)
        except AttributeError:
            pass
        return title, promo_text

    def get_courses_dict(self):
        url = "https://gb.ru/courses/all"
        course_links = self.get_course_links(url)
        for link in sorted(course_links):
            self.course_dict[link] = []
            title, description = self.title_and_description(link)
            self.course_dict[link] += [title]
            courses1 = self.extract_text_between_phrases(link, "Изучаемые ", "Диплом")
            courses2 = self.extract_text_between_phrases(link, "Технологии и инструменты", "Диплом")
            courses3 = self.extract_text_between_phrases(link, "Научитесь работать с основными инструментами", "Диплом")
            courses4 = self.extract_text_between_phrases(link, "Что вы изуч", "Диплом")
            courses5 = self.extract_text_after_phrase(link, 'Получите все', 20)
            courses6 = self.extract_text_after_phrase(link, 'Чему вы научитесь', 20)
            courses7 = self.extract_text_after_phrase(link, "Уверенное владение", 20)
            # courses8 = extract_text_after_phrase(link,"Результаты после обучения", 10)
            # program_track1 = extract_program_track(link, 'Основной бл','Запросить полную')
            # program_track2 = extract_program_track(link, 'Курс','Запросить полную')
            skills = courses1 + courses2 + courses3 + courses4 + courses5 + courses6 + courses7
            self.course_dict[link] += skills
        return self.course_dict


class Recommender:
    def __init__(self, k: int):
        self.k = k
        self.init_modules()

    def init_modules(self):
        # Парсер GeekBrains
        st.write("[INFO]: Парсинг данных с GeekBrains.ru...")
        self.geek_brain_parser = GeekBrainsParser()
        self.courses_dict = self.geek_brain_parser.get_courses_dict()
        st.write("[SUCCESS]: Парсинг данных успешен.")

        self.geekbrains_embeddings = {}
        self.reshaped_geekbrains_embeddings = {}

        # Bert Base NLI Mean Tokens
        st.write("[INFO]: Загрузка берта с GeekBrains.ru...")
        self.bert = SentenceTransformer('bert-base-nli-mean-tokens')
        st.write("[SUCCESS]: Берт загружен.")

    def get_embeddings_bert_base_nli_mean_tokens(self, text):
        sen_embeddings = self.bert.encode(text)
        return sen_embeddings

    def calc_geekbrains_embs(self):
        for url, info in self.courses_dict.items():
            self.geekbrains_embeddings[url] = self.get_embeddings_bert_base_nli_mean_tokens(
                self.courses_dict.get(url, None)
            )

    def semantic_similarity_bert_base_nli_mean_tokens(self, job, course):
        score = 0
        sen = job + course
        sen_embeddings = self.bert.encode(sen)
        for i in range(len(job)):
            if job[i] in course:
                score += 1
            else:
                if max(cosine_similarity([sen_embeddings[i]], sen_embeddings[len(job):])[0]) >= 0.4:
                    score += max(cosine_similarity([sen_embeddings[i]], sen_embeddings[len(job):])[0])
        score = score / len(job)
        return round(score, 3)

    def recommend(self, url: str, k: int or None = None):
        if k is None:
            k = self.k
        st.write("[INFO]: Парсинг данных с hh.ru...")
        self.hh_parser = HHParser(url=url)
        self.job_info = self.hh_parser.get_job_info()
        st.write("[SUCCESS]: Парсинг данных успешен.")

        recomendations = {}
        for url, course_info in self.courses_dict.items():
            recomendations[url] = self.semantic_similarity_bert_base_nli_mean_tokens(
                self.job_info, course_info
            )
        recomendations_df = pd.DataFrame({"url": recomendations.keys(), "sim": recomendations.values()})
        recomendations_df = recomendations_df.sort_values(by="sim", ascending=False)
        return {
            "recommendations": list(recomendations_df.iloc[:k, 0].values),
            "job_info": self.job_info,
        }


def set_visual_components():
    recommender = Recommender(k=5)    
    st.write(recommender.recommend("https://hh.ru/vacancy/97976633", k=3))
    st.empty().markdown("&nbsp;")
    with st.sidebar:
        option = st.radio(
            label='Выберите способ ввода',
            options=[
                'URL-ссылка',
                'PDF-файл',
                'Текстовое описание'
            ]
        )

        if option == 'PDF-файл':
            input_media = st.file_uploader(label='', type='pdf')

        else:
            mssg = "Прикрепите текстовое описание вакансии или URL-ссылку"

            """ Плашка для загрузки текста """
            input_media = st.text_input(
                mssg,
                label_visibility='visible'
            )
           

    with st.sidebar:
        st.markdown("### :orange[Требования по вакансии:]")
        switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch1")
        switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch2")
        switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch3")


    choice = ui.select(options=["Ссылка на вакансию", "PDF на вакансию"])
    if choice == "Ссылка на вакансию":
        textarea_value = ui.textarea(placeholder="https://hh.ru/vacancy/00000000",
                                     key="textarea1")
    elif choice == "PDF на вакансию":
        uploaded_file = st.file_uploader("Choose a file")
    cols = st.columns(3)
    with cols[0]:

        recommend_button = ui.button(text="Рекомендовать",
                                     key="styled_btn_tailwind",
                                     className="bg-orange-500 text-white", )
    with cols[1]:
        delete_button = ui.button(text="Сбросить", key="d", className="grey")

    if recommend_button and not delete_button:
        st.empty().markdown('''### {}'''.format("Рекомендованные курсы"),
                            help='Choose either 1 or 2 but not both. If both are selected 1 will be used.')
        cols = st.columns(3)
        with cols[0]:
            switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch1")
        with cols[1]:
            switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch2")
        with cols[2]:
            switch_value = ui.switch(default_checked=True, label="Toggle Switch", key="switch3")

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
       set_visual_components()



# Textarea Component
