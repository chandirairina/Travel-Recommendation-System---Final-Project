import joblib
from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

list_activity1=['cocokuntukanakanak',
 'cocokuntukkelompokbesar',
 'cocokuntukpasangan',
 'lokasibulanmadu',
"None"]

list_activity2=['makanandanminuman',
  'pemandangandantengara',
  'museum',
 'bagussaathujan',
 'aktivitasluarruangan',
 'wisataalamdantaman',
 'berjiwapetualang',
 'cocokuntukpenggemaraktivitasekstrem',
 'tamanairdantamanhiburan',
 'hiburandanpermainan',
 'tempatbelanja',
 'hiburanmalam',
 'kasinodanperjudian',
 'kebunbinatangdanakuarium',
 'acara',
 'kursusdansanggar',
 'hargaterjangkau',
 'spadankebugaran', 
 'tempatyangbelumpopuler']

list_options1=['I am going with kids',
 'I am going with a big group',
 'I am going with my partner, but not for honeymoon',
 'I am going with my partner and would like to be recommended a honeymoon spot ;)',
"I am traveling alone / going with my friends"]

list_options2=['I like culinary travel!',
  'I like sightseeing in the city.',
  'I like to go to museums',
 'I like indoor activities and other activities that can be done when it rains',
 'I like outdoor activities',
 'I like nature',
 'I am adventurous',
 'I am adrenaline junkies!',
 'I like to go to water parks and theme parks.',
 'I like fun and games!',
 'I like shopping!',
 'I enjoy nightlife',
 'I like casinos.',
 'I like to go to aquariums and zoos.',
 'I like to attend festivals and special events',
 'I like to learn something new during my travel by joining classes',
 'Recommend me cheap but interesting places!',
 'Refreshing and spa would not hurt, right?',
 'I like to explore unpopular places.']

app = Flask(__name__)

@app.route('/')
def home():
    df=pd.read_csv("dataset_recsys1_engineered.csv")
    list_places=df["Travel Destination"].unique()
    list_places.sort()
    cv = CountVectorizer()
    cv_result = cv.fit_transform(df['Things to Do'])
    list_activity=cv.get_feature_names()

    # list_option=['I would like to attend special events in my next destination.',
    # 'I enjoy outdoor activities.',
    # 'I will go on rainy season.',
    # 'I am adventurous.',
    # 'I will travel with my kids.',
    # 'I will travel in group.',
    # 'I will travel with my partner.',
    # 'I love extreme activities.',
    # 'My budget is limited.',
    # 'I like playing games.',
    # 'I enjoy nightlife.',
    # 'I like casinos.',
    # 'I would like to visit local aquariums and/or zoos.',
    # 'I would like to attend concerts.',
    # 'I would like to join workshops.',
    # 'I am going on honeymoon.',
    # 'I like culinary.',
    # 'I like freebies.',
    # 'I like museums.',
    # 'I like sightseeing within the city.',
    # 'I enjoy spas.',
    # 'I like water park and amusement park.',
    # 'I enjoy shopping!',
    # "I don't like crowded places",
    # 'I enjoy nature.']
    
    df_summ=pd.read_csv("dataset_summary.csv").head(100)

    return render_template('home.html', drop_places=list_places, list_activity1=list_activity1, list_options1=list_options1, list_activity2=list_activity2, list_options2=list_options2, data=df_summ, column_name=df_summ.columns.values,row_data=list(df_summ.values.tolist()))

@app.route('/recommendation', methods=['POST'])
def hasil():

    if request.method == 'POST':
        
        DataUser = request.form
        place=DataUser['destination']

        print(place)
        df1=pd.read_csv("dataset_recsys1_engineered.csv")
        df2=pd.read_csv("dataset_recsys2_engineered.csv")
        df4=pd.read_csv("dataset_indo_forhtml.csv")
        
        list_places=df1["Travel Destination"].unique()
        list_places.sort()
        cv = CountVectorizer()
        cv_result = cv.fit_transform(df1['Things to Do'])
        list_activity=cv.get_feature_names()

        cv.get_feature_names()

        cv_df = pd.DataFrame(cv_result.todense(),columns= cv.get_feature_names(),index=df1['Travel Destination'])
        cv_df

        cos_sin = cosine_similarity(cv_result)
    
        def get_recomendation(place):
            index_to_search = df1[df1['Travel Destination'] == place].index[0]
            place_similar = pd.Series(cos_sin[index_to_search])
            index_similar = place_similar.sort_values(ascending=False).index
            
            recomm_id=[]

            for i in index_similar:
                if (df1["Country Name"].iloc[i])=="Indonesia":
                    recomm_id.append (i)
            
            recomm_data=[]
            for j in recomm_id[0:7]:
                if (df1.loc[j]["Travel Destination"])!=place:
                    recomm_data.append(df1.loc[j]["Travel Destination"])

            return recomm_data

        user_type=""
        
        for i in list_activity1:
            user_type+=(DataUser[i]+" ")
        
        for i in list_activity2:
            user_type+=(DataUser[i]+" ")

        print(user_type)

        user_data={"Spot/Vendor":"user",
            "Type": user_type}

        df2=df2.append(user_data, ignore_index=True)

        cv_spot = CountVectorizer()
        cv_spot_result = cv_spot.fit_transform(df2['Type'])

        cv_spot.get_feature_names()

        cv_df_spot = pd.DataFrame(cv_spot_result.todense(),columns= cv_spot.get_feature_names(),index=df2['Spot/Vendor'])
        cv_df_spot

        cos_sin_spot = cosine_similarity(cv_spot_result)

        def get_recomendation_spot(place):
            index_to_search_spot = df2[df2['Spot/Vendor'] == "user"].index[0]
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
                            recom_spot.append(df2.loc[j]["Spot / Vendor Name"])
                            recom_spot_link.append(df2.loc[j]["Link"])
                            spot_per_destination+=1
                spot_in_destination.append(recom_spot)
                link_spot.append(recom_spot_link)
                recom_hotel_best.append(df4.loc[df4[df4["Travel Destination"]==i].index[0]]["Hotel Best Deal"])
                recom_hotel_link.append(df4.loc[df4[df4["Travel Destination"]==i].index[0]]["Hotel Link"])
                recom_flight_best.append(df4.loc[df4[df4["Travel Destination"]==i].index[0]]["Flight Best Deal"])
                recom_flight_link.append(df4.loc[df4[df4["Travel Destination"]==i].index[0]]["Flight Link"])

            return recom_destination, spot_in_destination, link_spot, recom_hotel_best, recom_hotel_link, recom_flight_best, recom_flight_link

    a,b,c,d,e,f,g=get_recomendation_spot(place)

    df_result=pd.DataFrame()
    df_result["Destination"]=a
    df_result["Hotel"]=d
    df_result["Flight"]=f

    df_result["Hotel"]=df_result["Hotel"].str.replace(".","").str.replace('Rp ',"").str.replace(",-","").astype(int)
    df_result["Flight"]=df_result["Flight"].str.replace(".","").str.replace('Rp ',"").str.replace(",-","").astype(int)

    df_result["Hotel"]=3*df_result["Hotel"]
    df_result["Total"]=df_result["Hotel"]+df_result["Flight"]

    df_hotelprice=df_result[["Destination","Hotel"]]
    df_hotelprice["Price_Type"]="Hotel Best Deal"
    df_hotelprice=df_hotelprice.rename(columns={"Hotel":"Price"})

    df_flightprice=df_result[["Destination","Flight"]]
    df_flightprice["Price_Type"]="Flight Best Deal"
    df_flightprice=df_flightprice.rename(columns={"Flight":"Price"})

    df_total=df_result[["Destination","Total"]]
    df_total["Price_Type"]="Appx. Budget"
    df_total=df_total.rename(columns={"Total":"Price"})

    df_viz=pd.concat([df_hotelprice,df_flightprice,df_total])

    fig=plt.figure(figsize=(45,30))
    # plt.font
    sns.barplot(x="Destination",y="Price", hue="Price_Type", data=df_viz)
    plt.xticks(fontsize=30, rotation=90)
    plt.yticks(fontsize=30)
    matplotlib.rc("xtick",labelsize=30)
    matplotlib.rc("ytick",labelsize=30)
    plt.xlabel('Travel Destination',fontsize=45)
    plt.ylabel('Price',fontsize=45)
    plt.legend(fontsize=35)
    plt.title("Budgeting for Recommended Destinations (For 4D3N)", fontsize=60)
    fig.savefig("static/images/budget_destination.png")

    return render_template('recommend.html', 
    input=DataUser, 
    output_destination=a, 
    output_spot=b, 
    output_link_spot=c, 
    output_hotel=d, 
    output_link_hotel=e, 
    output_flight=f, 
    output_link_flight=g,
    )

if __name__ == "__main__":

    app.run(debug=True)