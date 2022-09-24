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

# The data to use
if filmtitle:
    st.empty()
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
        netflix_class = ""
        amazon_class = ""
        disney_class = ""
        
        
        if "gb" in obj["streamingInfo"]:
            services = obj["streamingInfo"]["gb"]
    
            if "netflix" in services:
                canaccess = True
                netflix_class = "nf"
            elif "prime" in services:
                canaccess = True
                amazon_class = "ap"       
            elif "disney" in services:
                canaccess = True
                disney_class = "dp"
            else:
                not_on_selected_platforms_data += "<div class='nonukdata'>" + obj["title"]
                for service in services:
                    not_on_selected_platforms_data += "<span class='pill'>" + service + "</span>";
                not_on_selected_platforms_data += "</div>"
        else:
            non_uk_data += "<div class='nonukdata'>{0}<span class='pill'>{1}</span></div>".format(obj["title"], obj["year"])

        if canaccess:
            st.markdown(f"""
                        <div class="card">
                            <div class="card-header">{title} <span class="pill">{year}</span></div>
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
                                <span class="btn {netflix_class}">Netflix</span>
                                <span class="btn {amazon_class}">Amazon Prime</span>
                                <span class="btn {disney_class}">Disney+</span>
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