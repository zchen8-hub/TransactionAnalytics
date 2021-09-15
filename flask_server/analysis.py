import json
import pandas as pd
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from wordcloud import WordCloud
from _datetime import datetime

class PaymentMetaConstants:
    REFERENCE_NUMBER = 'reference_number'
    PPD_ID = 'ppd_id'
    PAYEE = 'payee'
    BY_ORDER_OF = 'by_order_of'
    PAYER = 'payer'
    PAYMENT_METHOD = 'payment_method'
    PAYMENT_PROCESSOR = 'payment_processor'
    REASON = 'reason'

class LocationConstants:
    ADDRESS = 'address'
    CITY = 'city'
    REGION = 'region'
    POSTAL_CODE = 'postal_code'
    COUNTRY = 'country'
    LAT = 'lat'
    LON = 'lon'
    STORE_NUMBER = 'store_number'


class TransactionKeyConstants:
    TRANSACTION_ID = 'transaction_id'
    ACCOUNT_OWER= 'account_owner'
    PENDING_TRANSACTION_ID = 'pending_transaction_id'
    PENDING = 'pending'
    PAYMENT_CHANNEL = 'payment_channel'
    PAYMENT_META = 'payment_meta'


class TransactionItem:
    def __init__(self, data):
        self.data = data
    
    def get_property(self, property):
        return self.data[property]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()


def convert_json_to_df(url):
    data = json.load(open(url))
    trans_df = pd.DataFrame([TransactionItem(item) for item in data])
    return df

def convert_to_df_from_json(json_path):
    df = pd.read_json(json_path)
    return df

def get_null_table(df):
    null_rate_df = pd.DataFrame(df.isnull().mean()).reset_index()
    null_rate_df.columns = ['Columns', 'NULL Ratio']
    null_rate_df['Keep'] = (null_rate_df['NULL Ratio'] != 0)
    null_rate_df['Keep'] = null_rate_df['Keep'].map({True:'Yes',False:'No'})
    return null_rate_df


def remove_null_column(df):
    valid_column_names = np.array(df.columns)[df.isnull().mean() != 1]
    invalid_colum_names = set(df.columns) -  set(valid_column_names)
    trans_df_valid = df[valid_column_names]
    return trans_df_valid

def draw_barh(labels, nums, x_label_name, figsize = (15,10), save_name='img.png', st=None):
    y = np.arange(len(labels))  # the label locations
    width = 0.5  # the width of the bars

    plt.figure(figsize=figsize)
    ax = plt.gca() 
    

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel(x_label_name)

    rects1 = ax.barh(y, nums, width)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)

    ax.bar_label(rects1, padding=3)
    dmin,dmax = np.min(nums), np.max(nums)
    margin = (dmax - dmin) * 0.1
    plt.xlim((dmin - margin, dmax + margin))
    if st:
        st.pyplot(plt.gcf())
        return
    plt.show()
    plt.savefig('images/' + save_name)

def numof_transactions_per_brand(df_valid):
    labels = df_valid.name.value_counts().index
    merchant_num = df_valid.name.value_counts()
    x_label_name = 'Number of Transactions'

    draw_barh(labels, merchant_num, x_label_name)

def process_category(cat_list):
    cat_list = sorted(cat_list)
    return ' | '.join(cat_list)

def numof_category(df_valid):
    df_valid['category_str'] = df_valid.category.apply(process_category)
    labels = df_valid.category_str.value_counts().index
    cat_num = df_valid.category_str.value_counts()
    x_label_name = 'Number of Categories'
    draw_barh(labels, cat_num, x_label_name)

def amount_disp_per_cat(df_valid):
    amt_sum_by_cat = df_valid[['category_str', 'amount']].groupby(by = 'category_str').sum()
    draw_barh(amt_sum_by_cat.index,amt_sum_by_cat['amount'], 'Total Amount for Each Category')

def payment_channel_disp(df_valid):
    payment_channel = df_valid['payment_channel']
    payment_channel_counts = payment_channel.value_counts()
    draw_barh(payment_channel_counts.index, payment_channel_counts, 'Payment Channel Counts', figsize=(8,3))

def precess_date(df_valid):
  for i in range(len(df_valid['date'])) :
    df_valid.iloc[i,7] = datetime.strptime(df_valid.iloc[i,7],'%Y-%m-%d')

def month_expense_per_cat(df_valid):
    print(df_valid.groupby(by=['category_id',pd.Grouper(key='date',freq='M')]).sum())

def month_expense_per_acc(df_valid):
    print(df_valid.groupby(by=['account_id',pd.Grouper(key='date',freq='M')]).sum())

def predict_acc_with_trans(transations_csv):
    x = pd.DataFrame()
    le = preprocessing.LabelEncoder()
    x['category_id'] = le.fit_transform(transations_csv['category_id'])
    x['payment_channel']= le.fit_transform(transations_csv['payment_channel'])
    date_info = []
    for i in range(len(transations_csv['date'])):
      date_info.append(int(transations_csv.iloc[i,7].strftime('%Y%m%d')))
    x['date'] = date_info
    y = le.fit_transform(transations_csv['account_id'])

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,max_depth=1, random_state=0).fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    return le.classes_,pd.DataFrame(confusion_matrix(y_test, y_pred))

def wordcloud_of_brand(df_valid, st = None):
    merchant_names = ''
    merchant_name = df_valid['merchant_name'].tolist()
    
    for i in range(len(merchant_name)):
        merchant_names += str(merchant_name[i]) + '  '

    wordcloud = WordCloud(width = 800, height = 800,
                  background_color ='white',
                  min_font_size = 10).generate(merchant_names)
  
    # plot the WordCloud image                      
    plt.figure(figsize = (5, 5), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    if st:
        st.pyplot(plt.gcf())
        return 
    plt.show()
    plt.savefig('word_cloud.png')
