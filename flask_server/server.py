import streamlit as st
import pandas as pd
import json
import numpy as np
from math import ceil
import analysis
from io import StringIO

header = st.container()
dataset = st.container()
description = st.container()
visualization = st.container()
model_trainining = st.container()
side_container = st.sidebar.container()

df = pd.read_json('data.json')
n_row,n_column = df.shape

with side_container:
    st.header("Transaction Analytics")
    st.text("Data Transform")
    st.text("Invalid Data Filtering")
    st.text("Classification")



with header:
    st.title("Payment Analysis Report")
    st.text("Analyzed and Designed by Zhiyuan Chen")


with dataset:
    st.header('Input Data')
    st.text('This is the original data received')

    page_size = 50
    page_number = st.number_input(
        label=f"Page Number ({n_row} row and {n_column})",
        min_value=1,
        max_value=ceil(len(df)/page_size),
        step=1,
    )
    current_start = (page_number-1)*page_size
    current_end = page_number*page_size
    st.write(df[current_start:current_end])

with description:
    st.header('Description')
    st.text('The ratio of NULLs in each column. We only keep columns with NULL Ratio > 0')
    get_null_table = analysis.get_null_table(df)
    st.write(get_null_table)




with visualization:
    st.header('Visualization')
    st.text('Word Cloud of Brands')
    df_not_null = analysis.remove_null_column(df)
    analysis.wordcloud_of_brand(df, st)

    st.text('Number of Transactions of Brand Names')
    labels = df_not_null.name.value_counts().index
    merchant_num = df_not_null.name.value_counts()
    x_label_name = 'Number of Transactions'

    analysis.draw_barh(labels, merchant_num, x_label_name, st=st)

    st.text('Number of Transactions of Categories')
    df_not_null['category_str'] = df_not_null.category.apply(analysis.process_category)
    labels = df_not_null.category_str.value_counts().index
    cat_num = df_not_null.category_str.value_counts()
    x_label_name = 'Number of Categories'
    analysis.draw_barh(labels, cat_num, x_label_name, st=st)

    st.text('Total Amount for Each Category')
    amt_sum_by_cat = df_not_null[['category_str', 'amount']].groupby(by = 'category_str').sum()
    analysis.draw_barh(amt_sum_by_cat.index,amt_sum_by_cat['amount'], 'Total Amount for Each Category', st=st)

    st.text("Payment Channel Counts")
    payment_channel = df_not_null['payment_channel']
    payment_channel_counts = payment_channel.value_counts()
    analysis.draw_barh(payment_channel_counts.index, payment_channel_counts, 'Payment Channel Counts', figsize=(8,3), st = st)


with model_trainining:
    st.header('Model Performance')
    st.text("results trained/predicted using GBM")
    df_not_null = analysis.remove_null_column(df)
    class_list, conf_mat = analysis.predict_acc_with_trans(df_not_null)
    for idx,cid in enumerate(class_list):
        st.text(f"Account {idx}: {cid}")
    
    st.write(conf_mat)

