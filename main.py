import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(
        page_title="GibData",
)
def upload():
    uploaded_file = st.file_uploader("Выберите файл")
    if uploaded_file is not None:
        format_name = uploaded_file.name.split('.')[1]

        if format_name == "parquet":
            dataframe = pd.read_parquet(uploaded_file)
        elif format_name == "csv":
            dataframe = pd.read_csv(uploaded_file)
        else:
            st.write("Можно загрузить только файлы формата parquet или csv.")
            st.write("Попробуйте снова!")
            return 0
        st.write(dataframe)
        if st.button('Предсказать результаты'):
            model = LinearRegression()

            model.set_params(**{'copy_X': True, 'fit_intercept': True,
                                'n_jobs': None, 'positive': False})
            model.coef_  = np.array([-3.30519684e+03, -8.95809956e-04,  1.93452312e+03,
                                      1.97646296e+03,  2.24286837e+03,  1.73040943e+03,
                                      1.85721127e+03,  2.39654841e+03,  1.58982174e+03,  
                                      1.84881269e+03])
            model.intercept_  = -400609.56832162244
            test = dataframe.groupby(['wagnum', 'ts_id'], as_index=False).last()
            answer = pd.DataFrame({"wagnum": test["wagnum"],
                                   "ts_id": test["ts_id"],
                                   "target": model.predict(test.drop("wagnum", axis = 1))})
            st.write(answer)
            def convert_df(df):
                return df.to_csv(index = False)

            csv = convert_df(answer)

            st.download_button(
                label="Скачать данные в формате CSV",
                data=csv,
                file_name='GibData.csv',
                mime='text/csv')


if __name__ == "__main__":
       upload()