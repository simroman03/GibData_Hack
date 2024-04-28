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
from PyPDF2 import PdfReader
import cohere


class TextExtractor:
    def __init__(self, text):
        self.text = text
        self.name = self.get_name_with_cohere()
        self.skills = self.get_key_skills_with_cohere()

    def get_name_with_cohere(self):
        if self.text:
            prompt = f"У тебя на вход есть текст {self.text}. Нужно выдать json с названием вакансии. Json в формате 'название': '...'"
            co = cohere.Client("8rP3am6NDcGmGieq6x8E80Wps4nU3xXZSoYSucaw")
            completion = co.chat(
                message=prompt,
                model='command-r-plus',
                temperature=0.01,
            )
            result = completion.text
            return json.loads(result)
        else:
            return "No text provided"

    def get_key_skills_with_cohere(self):
        if self.text:
            prompt = f"У тебя на вход есть текст {self.text}. Нужно выдать json cо всеми ключевыми навыками и технологиями в данном описании. Json в формате 'навыки': ['...', ..., '...']"
            co = cohere.Client("8rP3am6NDcGmGieq6x8E80Wps4nU3xXZSoYSucaw")
            completion = co.chat(
                message=prompt,
                model='command-r-plus',
                temperature=0.01,
            )
            result = completion.text
            return json.loads(result)
        else:
            return "No text provided"

    def get_job_info(self):
        return self.name + self.skills


class FileParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_text = self.read_pdf()
        self.text_extractor = TextExtractor(self.pdf_text)
        self.job_info = self.text_extractor.get_job_info()

    def read_pdf(self, file_path):
        text = ""
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text

    def get_job_info(self):
        return self.job_info


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
    def __init__(self, geek_brains_courses_path=None):
        self.geek_brains_courses_path = geek_brains_courses_path
        if geek_brains_courses_path is not None:
            self.geek_brains_data = pd.read_parquet(self.geek_brains_courses_path)
            self.course_dict = self.geek_brains_data.to_dict()
        else:
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
            print("Ошибка при загрузке страницы:", response.status_code)
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
            return []

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

    def find_price(self, url, target_char):
        # Получаем все цены со страницы
        html = self.get_html_from_url(url)
        cleaned_text = self.clean_html(html)
        currency_positions = [m.start() for m in re.finditer(target_char, cleaned_text)]
        prices = []

        for pos in currency_positions:
            substr = cleaned_text[pos - 8:pos + 5]
            numbers = re.findall(r'\d+', substr)
            price = ''.join(numbers)
            if price:
                prices.append(price)

        if len(prices) == 2:
            prices = [prices[0]]

        if len(prices) == 4:
            prices = [prices[1]]

        if len(prices) == 5:
            prices = [prices[0]]

        if len(prices) == 6:
            prices = ['4049']
        return prices

    def get_courses_dict(self):
        if not self.course_dict:
            url = "https://gb.ru/courses/all"
            course_links = self.get_course_links(url)
            for link in sorted(course_links):
                self.course_dict[link] = {}
                title, description = self.title_and_description(link)
                self.course_dict[link]["title"] = title
                self.course_dict[link]["description"] = description

                courses1 = self.extract_text_between_phrases(link, "Изучаемые ", "Диплом")
                courses2 = self.extract_text_between_phrases(link, "Технологии и инструменты", "Диплом")
                courses3 = self.extract_text_between_phrases(link, "Научитесь работать с основными инструментами",
                                                             "Диплом")
                courses4 = self.extract_text_between_phrases(link, "Что вы изуч", "Диплом")
                courses5 = self.extract_text_after_phrase(link, 'Получите все', 20)
                courses6 = self.extract_text_after_phrase(link, 'Чему вы научитесь', 20)
                courses7 = self.extract_text_after_phrase(link, "Уверенное владение", 20)
                # courses8 = self.extract_text_after_phrase(link,"Результаты после обучения", 10)
                skills = courses1 + courses2 + courses3 + courses4 + courses5 + courses6 + courses7
                self.course_dict[link]["skills"] = skills

                program_track = self.extract_program_track(link, 'Основной бл', 'Запросить полную')
                self.course_dict[link]["program_track"] = program_track

                price = self.find_price(link, '₽/мес') + self.find_price(link, '₽ /мес.')
                self.course_dict[link]["price"] = price

        return self.course_dict


class Recommender:
    def __init__(self, k: int):
        self.k = k
        self.geekbrains_embeddings = {}
        self.reshaped_geekbrains_embeddings = {}
        self.init_gb_parser()
        self.init_bert()

    def init_bert(self):
        print("[INFO]: Загрузка bert-base-nli-mean-tokens...")
        self.bert = SentenceTransformer('bert-base-nli-mean-tokens')
        print("[SUCCESS]: Берт загружен.")

    def init_gb_parser(self):
        print("[INFO]: Парсинг данных с GeekBrains.ru...")
        self.geek_brain_parser = GeekBrainsParser(geek_brains_courses_path="geek_brains_courses_data.parquet")
        courses_dict = self.geek_brain_parser.get_courses_dict()
        result = {}
        for i, row in pd.DataFrame(courses_dict).iterrows():
            result[row["url"]] = [row["title"]] + list(row["skills"])
        self.courses_dict = result
        print("[SUCCESS]: Парсинг данных успешен.")

    def get_job_info_from_text(self, text):
        print("[INFO]: Парсинг данных с текста...")
        self.text_extractor = TextExtractor(text=text)
        job_info = self.text_extractor.get_job_info()
        print("[SUCCESS]: Парсинг данных успешен.")
        return job_info

    def get_job_info_from_pdf(self, file_path):
        print("[INFO]: Парсинг данных с PDF...")
        self.file_parser = FileParser(file_path=file_path)
        job_info = self.file_parser.get_job_info()
        print("[SUCCESS]: Парсинг данных успешен.")
        return job_info

    def get_job_info_from_url(self, url):
        print("[INFO]: Парсинг данных с hh.ru...")
        self.hh_parser = HHParser(url=url)
        job_info = self.hh_parser.get_job_info()
        print("[SUCCESS]: Парсинг данных успешен.")
        return job_info

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
        job = job if type(job) != str else job.split(" ")
        course = course if type(course) != str else course.split(" ")
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

    def get_coverage_mtx(self, recommendations, job_info):
        courses_dict = self.courses_dict
        competencies = job_info[1:]
        coverage_mtx = pd.DataFrame(index=competencies)  # Provide the index here
        # No need to set index separately now
    
        for course_url in recommendations:
            coverage_mtx[course_url] = np.zeros(len(competencies))
            for competence in competencies:
                if len(courses_dict.get(course_url)) < 2:
                    coverage_mtx.loc[:, course_url] = 0.5
                coverage_mtx.loc[competence, course_url] = self.semantic_similarity_bert_base_nli_mean_tokens(
                    [competence], courses_dict.get(course_url)[1:]
                )
        return coverage_mtx

    def recommend(self, job_info, k: int or None = None):
        # if input[-4:] == ".pdf":
        #     # job_info = self.get_job_info_from_pdf(input)
        #     return
        # elif "https" in input:
        #     job_info = self.get_job_info_from_url(input)
        # else:
        #     # job_info = self.get_job_info_from_text(input)
        #     return
        
        if k is None:
            k = self.k

        recommendations = {}
        for url, course_info in self.courses_dict.items():
            recommendations[url] = self.semantic_similarity_bert_base_nli_mean_tokens(
                job_info, course_info
            )
        recommendations_df = pd.DataFrame({"url": recommendations.keys(), "sim": recommendations.values()})
        recommendations_df = recommendations_df.sort_values(by="sim", ascending=False)
        recommendations = list(recommendations_df.iloc[:k, 0].values)

        names = [self.courses_dict.get(recommendations_url)[0] for recommendations_url in recommendations]
        print(recommendations)
        print(names)
        print(job_info)
        coverage_mtx = self.get_coverage_mtx(recommendations, job_info)
        return {
            "recommendations": recommendations,
            "job_info": job_info,
            "coverage_mtx": coverage_mtx,
            "names": names,
        }


def set_visual_components():
    recommender = Recommender(k=3)
    recommend_button = False
    delete_button = True
    is_calculated = False
    job_parse = False
    
    st.set_page_config(
        page_title="Course Recommender",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # st.title("Компетентностный подбор образовательных курсов")
    st.markdown("# :orange[Компетентностный подбор образовательных курсов [GibData]]")
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

            if input_media is not None and "https" in input_media:
                input_url = input_media

        load_button = ui.button(text="Загрузить вакансию", key="load")
    
        if load_button and input_url is not None:
            hh_parser = HHParser(url=input_url)
            job_info = hh_parser.get_job_info()
            job_parse = True

            st.markdown(f"### :gray[Требования по вакансии:]")
            try:
                st.markdown(f"### :orange[{job_info[0]}]")
            except:
                pass
            st.empty().markdown('''### {}'''.format("Дополнительные фильтры:"),
                                help='Choose either 1 or 2 but not both. If both are selected 1 will be used.')
            switch_comp = {}
            for i in range(1, len(job_info)):
                switch_value = ui.switch(default_checked=True, label=job_info[i], key=f"switch_{i}")
                switch_comp[job_info[i]] = switch_value

    if job_parse:
        cols = st.columns(4)
        with cols[0]:
            recommend_button = ui.button(text="Рекомендовать",
                                         key="styled_btn_tailwind",
                                         className="bg-orange-500 text-white")
        with cols[1]:
            delete_button = ui.button(text="Сбросить", key="d")
    
        if recommend_button and not delete_button:
            dict_hh = recommender.recommend(job_info, k=6)
            is_calculated = True
    
        if is_calculated:
            coating_matrix = dict_hh['coverage_mtx'].copy()
            names = dict_hh['names'].copy()
            
            # sort_matrix = pd.DataFrame(coating_matrix.sum()).sort_values(by=0, ascending=False).reset_index()
            # sort_matrix = sort_matrix.style.map(lambda x: f"background-color: {'green' if x >= 0.85 else 'white'}", subset='Value')
            st.dataframe(coating_matrix)
            
            st.empty().markdown('''### {}'''.format("Рекомендованные курсы"),
                                help='Choose either 1 or 2 but not both. If both are selected 1 will be used.')
            for i in range(len(sort_matrix)):
                # title = f"{sort_matrix['url'][i]}🔥"
                title = "url"
                content = names[i]
                description = "Срок обучения: n месяцев"
                ui.metric_card(title=title, content=content, description=description, key=f"card{i}")


if __name__ == "__main__":
    set_visual_components()
            # Textarea Component
