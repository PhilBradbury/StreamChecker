# -*- coding: utf-8 -*-
""" Created on Sat Sep 24 19:43:39 2022, by Phil bradbury """

import streamlit as st
import requests
import json

# Add Bootstrap
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">', unsafe_allow_html=True)

# Import CSS file to style output page
with open("styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html = True)

#Data dictionaries
services_of_interest = {
    "netflix": "Netflix",
    "prime": "Amazon Prime",
    "disney": "Disney+",
    "apple": "Apple TV",
    "now": "Now TV",
    "iplayer": "BBC iPlayer"
    }

# Start building the page output
st.title('Stream Check')
st.subheader('Select the subscription service(s) of interest to you, and then enter keyword(s) below to search for films streaming in the UK.')
filmtitle = st.text_input("Enter a film title (or part of)")

# Parameters
url = "https://streaming-availability.p.rapidapi.com/v2/search/title"
querystring = {"title": filmtitle,"country":"gb","type":"movie","output_language":"en"}
headers = {
	"X-RapidAPI-Key": "c5e3589ba0mshb0e69d4356a72a3p12b8d4jsn44fbfcc97ec3",
	"X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
}

# Functions
@st.cache
def get_data(theurl, theheaders, thequerystring):
    response = requests.request("GET", theurl, headers=theheaders, params=thequerystring)
    return response

def build_service_indicator(service_name, text_to_display, class_name, chosen):
    service_class_name = ""
    if chosen:
        service_class_name = " " + class_name 

    return "<span class='btn btn-sm btn-secondary" + service_class_name + "'>" + text_to_display + "</span>"
   
# Sidebar - show all services for user to select from
show_service = {}
with st.sidebar:
    st.header("Choose your service(s)")
    for service in services_of_interest:
        show_service[service] = st.checkbox(f'{services_of_interest[service]}')

# The data to use
if filmtitle:
    data = get_data(url, headers, querystring)
    result = json.loads(data.content)
    
    st.markdown("<hr /><h3>UK results...</h3>", unsafe_allow_html=True)
    
    non_uk_data = ""
    not_on_selected_platforms_data = ""

    for obj in result["result"]:
        title = obj["title"]
        year = obj["year"]
        synopsis = obj["overview"]
        
        actor_output = "&nbsp;"
        if obj["cast"]:
            for actor in obj["cast"]:
                actor_output += "<div class='actor'>" + actor + "</div>"
        
        if "original" in obj["posterURLs"]:
            image_url = obj["posterURLs"]["original"]
        
        canaccess = False  
        has_subscription = False
        
        if "gb" in obj["streamingInfo"]:
            canaccess = True
            services = obj["streamingInfo"]["gb"]
            services_data = ""
    
            for s in services:
                service_name = services_of_interest.get(s, s) # Check if service is in those of interest. 
                services_data += build_service_indicator(s, service_name, s, show_service.get(s, False))
                if show_service.get(s, False): 
                    has_subscription = True

            # See if we have matched at least one service of interest
            if not has_subscription:
                not_on_selected_platforms_data += "<div class='card-header'><h4>" + title + "</h4><span>" + services_data + "</span></div>"

        else:
            non_uk_data += "<div class='card-header'><h4>{0}</h4><span class='btn btn-sm btn-primary'>{1}</span></div>".format(obj["title"], obj["year"])

        if canaccess & has_subscription:
            st.markdown(f"""
                        <div class="card">
                            <div class="card-header">
                                <h4>{title}</h4> 
                                <span class="badge badge-primary">{year}</span>
                            </div>
                            <div class="card-body">
                                <div class="card-leftcol">
                                    <img class="poster" src={image_url}></td>
                                </div>
                                <div class="card-rightcol">
                                    <div class="synopsis">
                                        {synopsis}
                                    </div>
                                    <div class="cast">
                                        {actor_output}
                                    </div>
                                </div>                            
                            </div>
                            <div class="card-footer">
                               &nbsp;{services_data}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
    # Out of the loop over the data object 
    if not_on_selected_platforms_data:
        st.markdown(f"""
                    ###
                    <h3>Not on a chosen service...</h3>
                    {not_on_selected_platforms_data}
                    """, unsafe_allow_html=True)
    
    if non_uk_data:
        st.markdown(f"""
                    ###
                    <h3>Non-UK streaming services...</h3>
                    {non_uk_data}
                    """, unsafe_allow_html=True)
