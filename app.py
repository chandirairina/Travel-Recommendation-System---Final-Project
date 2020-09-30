import joblib
from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

@app.route('/')
def home():
    df=pd.read_csv("dataset_recsys1_engineered.csv")
    list_places=df["Travel Destination"].unique()
    list_places.sort()
    cv = CountVectorizer()
    cv_result = cv.fit_transform(df['Things to Do'])
    list_activity=cv.get_feature_names()

    list_option=['I would like to attend special events in my next destination.',
    'I enjoy outdoor activities.',
    'I will go on rainy season.',
    'I am adventurous.',
    'I will travel with my kids.',
    'I will travel in group.',
    'I will travel with my partner.',
    'I love extreme activities.',
    'My budget is limited.',
    'I like playing games.',
    'I enjoy nightlife.',
    'I like casinos.',
    'I would like to visit local aquariums and/or zoos.',
    'I would like to attend concerts.',
    'I would like to join workshops.',
    'I am going on honeymoon.',
    'I like culinary.',
    'I like freebies.',
    'I like museums.',
    'I like to explore the city.',
    'I enjoy spas.',
    'I need local tourist information to be available.',
    'I like water park and amusement park.',
    'I enjoy shopping!',
    "I don't like crowded places",
    'Transportation',
    'Tours',
    'I like water sports.',
    'I enjoy nature.']
    df1=pd.read_csv("dataset_recsys1_engineered.csv")
    df2=pd.read_csv("dataset_recsys2_engineered_droptur.csv")
    df3=df1.merge(df2, on="Travel Destination")[["Travel Destination","Spot / Vendor","Type","Hotel Best Deal", "Flight Best Deal"]].head(25)
    
    return render_template('home.html', drop_places=list_places, list_activity=list_activity, list_option=list_option, data=df3.to_html())

@app.route('/recommendation', methods=['POST'])
def hasil():
    df1=pd.read_csv("dataset_recsys1_engineered.csv")
    df2=pd.read_csv("dataset_recsys2_engineered_droptur.csv")
    
    list_places=df1["Travel Destination"].unique()
    list_places.sort()
    cv = CountVectorizer()
    cv_result = cv.fit_transform(df1['Things to Do'])
    list_activity=cv.get_feature_names()

    cv.get_feature_names()

    cv_df = pd.DataFrame(cv_result.todense(),columns= cv.get_feature_names(),index=df1['Travel Destination'])
    cv_df

    cos_sin = cosine_similarity(cv_result)

    if request.method == 'POST':
        
        DataUser = request.form
        place=DataUser['destination']
        
        user_type=""
        for i in list_activity:
            user_type+=(DataUser[i]+" ")

        def get_recomendation(place):
            index_to_search = df1[df1['Travel Destination'] == place].index[0]
            place_similar = pd.Series(cos_sin[index_to_search])
            index_similar = place_similar.sort_values(ascending=False).index
            
            recomm_id=[]

            for i in index_similar:
                if (df1["Country Name"].iloc[i])=="Indonesia":
                    recomm_id.append (i)
            
            recomm_data=[]
            hotel_price=[]
            hotel_link=[]
            flight_price=[]
            flight_link=[]
            for j in recomm_id[0:10]:
                if (df1.loc[j]["Travel Destination"])!=place:
                    recomm_data.append(df1.loc[j]["Travel Destination"])
                    hotel_price.append(df1.loc[j]["Hotel Best Deal"])
                    hotel_link.append(df1.loc[j]["Hotel Link"])
                    flight_price.append(df1.loc[j]["Flight Best Deal"])
                    flight_link.append(df1.loc[j]["Hotel Link"])


            return recomm_data

        

        user_data={"Spot / Vendor":"user",
            "Type": user_type}

        df2=df2.append(user_data, ignore_index=True)

        cv_spot = CountVectorizer()
        cv_spot_result = cv_spot.fit_transform(df2['Type'])

        cv_spot.get_feature_names()

        cv_df_spot = pd.DataFrame(cv_spot_result.todense(),columns= cv_spot.get_feature_names(),index=df2['Spot / Vendor'])
        cv_df_spot

        cos_sin_spot = cosine_similarity(cv_spot_result)

        def get_recomendation_spot(place):
            index_to_search_spot = df2[df2['Spot / Vendor'] == "user"].index[0]
            place_similar_spot = pd.Series(cos_sin_spot[index_to_search_spot])
            index_similar_spot = place_similar_spot.sort_values(ascending=False).index
            
            similar_spot_idx=[]
            for i in index_similar_spot:
                if i != 12423:
                    similar_spot_idx.append(i)
                
            recom_destination=[]
            spot_in_destination=[]
            link_spot=[]
            recom_hotel_best=[]
            recom_hotel_link=[]
            recom_flight_best=[]
            recom_flight_link=[]
            
            for i in get_recomendation(place):
                recom_destination.append(i)
                spot_per_destination=0
                recom_spot=[]
                recom_spot_link=[]
                for j in similar_spot_idx:
                    if df2.loc[j]["Travel Destination"]==i:
                        if spot_per_destination<5:
                            recom_spot.append(df2.loc[j]["Spot / Vendor"])
                            recom_spot_link.append(df2.loc[j]["Link"])
                            spot_per_destination+=1
                spot_in_destination.append(recom_spot)
                link_spot.append(recom_spot_link)
                recom_hotel_best.append(df1.loc[df1[df1["Travel Destination"]==i].index[0]]["Hotel Best Deal"])
                recom_hotel_link.append(df1.loc[df1[df1["Travel Destination"]==i].index[0]]["Hotel Link"])
                recom_flight_best.append(df1.loc[df1[df1["Travel Destination"]==i].index[0]]["Flight Best Deal"])
                recom_flight_link.append(df1.loc[df1[df1["Travel Destination"]==i].index[0]]["Flight Link"])


            return recom_destination, spot_in_destination, link_spot, recom_hotel_best, recom_hotel_link, recom_flight_best, recom_flight_link

    a,b,c,d,e,f,g=get_recomendation_spot(place)

    return render_template('recommend.html', 
    input=DataUser, 
    output_destination=a, 
    output_spot=b, 
    output_link_spot=c, 
    output_hotel=d, 
    output_link_hotel=e, 
    output_flight=f, 
    output_link_flight=g)

if __name__ == "__main__":

    app.run(debug=True)