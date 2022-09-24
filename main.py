# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 12:43:39 2022
@author: Phil bradbury
"""

import streamlit as st
import pandas as pd
import requests
import json

with open("styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html = True)

st.title('Stream Check')
filmtitle = st.text_input("Enter a film title (or part of)")

# Parameters
url = "https://streaming-availability.p.rapidapi.com/v2/search/title"
querystring = {"title": filmtitle,"country":"gb","type":"movie","output_language":"en"}
headers = {
	"X-RapidAPI-Key": "c5e3589ba0mshb0e69d4356a72a3p12b8d4jsn44fbfcc97ec3",
	"X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
}

# Function
@st.cache
def get_data(theurl, theheaders, thequerystring):
    response = requests.request("GET", theurl, headers=theheaders, params=thequerystring)
    return response

with st.sidebar:
    show_netflix = st.checkbox("Netflix")
    show_amazon = st.checkbox("Amazon Prime")
    show_disney = st.checkbox("Disney+")
    show_apple = st.checkbox("Apple")
    show_now = st.checkbox("Now TV")


# The data to use
if filmtitle:
    data = get_data(url, headers, querystring)
    result = json.loads(data.content)
    
    #st.write(result["result"])
    st.markdown("<h4>UK results...</h4>", unsafe_allow_html=True)
    
    non_uk_data = ""
    not_on_selected_platforms_data = ""

    for obj in result["result"]:
        title = obj["title"]
        year = obj["year"]
        synopsis = obj["overview"]
        
        actor_output = "&nbsp;"
        if obj["cast"]:
            actor_output += "<hr /><h6 style='padding-left: 5px;'>Cast<h6>"
            for actor in obj["cast"]:
                actor_output += "<div class='actor'>" + actor + "</div>"
        
        if "original" in obj["posterURLs"]:
            image_url = obj["posterURLs"]["original"]
        
        canaccess = False  
        has_subscription = False
        
        services_data = ""
        netflix_class = ""
        amazon_class = ""
        disney_class = ""
        apple_class = ""
        now_class = ""
        
        
        if "gb" in obj["streamingInfo"]:
            canaccess = True
            services = obj["streamingInfo"]["gb"]
    
            for s in services:
                if s == "netflix":
                    if show_netflix:
                        has_subscription = True
                        netflix_class = "nf"
                    services_data += "<span class='pill " + netflix_class + "'>Netflix</span>"
                    
                elif s == "prime":
                    if show_amazon:
                        has_subscription = True
                        amazon_class = "ap"
                    services_data += "<span class='pill " + amazon_class + "'>Amazon Prime</span>"
                    
                elif s == "disney":
                    if show_disney:
                        has_subscription = True
                        disney_class = "dp"
                    services_data += "<span class='pill " + disney_class + "'>Disney+</span>"
                    
                elif s == "apple":
                    if show_apple:
                        has_subscription = True
                        apple_class = "app"
                    services_data += "<span class='pill " + apple_class + "'>Apple</span>"
                
                elif s == "now":
                    if show_now:
                        has_subscription = True
                        now_class = "now"
                    services_data += "<span class='pill " + now_class + "'>Now TV</span>"

                else:
                    services_data += "<span class='pill'>" + s + "</span>"
            
            if not has_subscription:
                not_on_selected_platforms_data += "<div class='nonukdata'>" + title + services_data + "</div>"

        else:
            non_uk_data += "<div class='nonukdata'>{0}<span class='pill year-pill'>{1}</span></div>".format(obj["title"], obj["year"])

        if canaccess & has_subscription:
            st.markdown(f"""
                        <div class="card">
                            <div class="card-header">{title} <span class="pill year-pill">{year}</span></div>
                            <div class="card-body">
                                <div class="image">
                                    <img class="poster" src={image_url}></td>
                                </div>
                                <div class="film-details">
                                    {synopsis}
                                    {actor_output}
                                </div>                            
                            </div>
                            <div class="card-footer">
                               &nbsp;{services_data}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
    # Out of the loop over the data object  
    st.markdown(f"""
                <h4>Not on a chosen service...</h4>
                {not_on_selected_platforms_data}
                """, unsafe_allow_html=True)
    
    st.markdown(f"""
                <h4>Non-UK results...</h4>
                {non_uk_data}
                """, unsafe_allow_html=True)