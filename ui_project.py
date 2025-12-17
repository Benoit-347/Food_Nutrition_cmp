import os      # opening files, and exiting program
import requests     # sending api requests
import matplotlib.pyplot as plt     # for plotting bar graphs
import numpy as np
import json # loading json file, which we create ourselves to store previously searched food names
import streamlit
import atexit   # to do fns when a user exits program

MAX_PER_REQUEST = 25
if False:
    """
    
    when submitting- The graders will primarily look at demo video. pytests should ignore using api keys


    Todo-
    Additional display info:
    3. (follwed with 2nd feature) Do self chk on food, to see if it is relatively high on bad nutrients using a simple if else classification if the food is high in bad cholesterol, and sugar.
    4. Display nutrient density score with density = (sum(weighted_important_nutrients)) / calories

    Big updates
    5. Multi food cmp

    Extras:
    1. keep track and update all keys with new values of dict_memoization data if oldest data, older than 1 year.
        # dicts in py after 3.7 uses arrays to have spare hash tables, that preserve order of keys that is inserted.

    Done:

    1. 
    cleared: Already did memorization, turn it into a local database storage
    method: Store memoized data in dict format and store it to a json file when program terminates. Load the same file back on when programs execution starts, keeping data and appending over n number of program executions.
                Uses json module with json.dump(<dict>, <file_obj>) and <dict> = json.load(<file_obj>)

        Further details:
            # Using python to format to storing <dict> type hash (faster as build in), and storing as json (Reading- if able to load full file into python- o(n) speed to read inputs. Else- vary slow, fix- shelve)
            # Medium size (over 1 GB files) shelve- allows partial load of database, smaller file size as uses binary format to store. 
                # shelve uses random single-key reads/writes; shelve = best for many small persistent operations without loading all data.
            # High size (and majority of scenarios)- SQLite
                Even while reading/writing, uses B-Tree lookup. Bulk inserts & queries are available, with optimized features.
                Has smallest file size.

    2.
    Implemented UI on program, using input and submit button,
        atexit module to run save fn only after exit program is initiated.

    3.
    Implemented custom selected nutrient display, using 'multiselect' option in streamlit, instead of repeated checkbox selection.

    4.
    Added a Filter feature to iteratively search for food with a specified minimum value of nutrients, under the given food name.
    completed: Enable user to set filtering to values (min/max). So we iterate over to nxt food, until all conditions match. (Also keep score to find best match? (largest of a list, iteratively algo))

    5. 
    Made a seperate graph for bad nutrients
    """


def request_food(SEARCH_URL, API_KEY, food_query, page_limit, dict_memoization):
    
    # check memoized data first
    if food_query in dict_memoization:
        return dict_memoization[food_query]
    
    # get (url, parameters);     parameters  = "api_key", "query" (food name), "pageSize" (max results count)
    search_result = requests.get(SEARCH_URL, params= {"api_key": API_KEY, "query": food_query, "pageSize": page_limit}, timeout=10)
    search_result.raise_for_status()        # raise exception if failed web request.

    result = search_result.json().get("foods", [])     # convert result obj into json dict, use dict get method to obtain value in "foods" key (default []).
    
    if bool(result) == False:
        return None
    
    # add to memoized data
    dict_memoization[food_query] = result

    return result

def get_nutrient(food, name):
    # this fn runs on the node to response object from request. Searching for matching nutrient name from value to nutrientName key, from node to foodNutrients value, which is from dict food.  
         # ideal workflow- "foods = [ dict_food, dict_food_2..]; dict_food = {"foodNutrients": [ {"nutrientName": <name_1>, "value": <val_1>}, {"nutrientName": <name_2>, "value": <val_2>} ] }
    for nutrient in food["foodNutrients"]:
        if nutrient["nutrientName"] == name:
            return nutrient["value"]

def get_nutrients_food(food, selected_nutrients):
    result = []
    for i in selected_nutrients:
        value = get_nutrient(food, i)
        if value == None:
            value = 0
        result.append(value)     #  # ideal workflow- "foods = [ dict_food, dict_food_2..]; dict_food = {"foodNutrients": [ {"nutrientName": <name_1>, "value": <val_1>}, {"nutrientName": <name_2>, "value": <val_2>} ] }
    return result

def graph_food(first_food_obj, second_food_obj, first_food_data, second_food_data, nutrients):

    # 1. setup label
    label_1 = first_food_obj['description']
    label_2 = second_food_obj['description']

    # 2. SETUP PLOT
    x = np.arange(len(nutrients))  # Label locations
    width = 0.35  # Width of the bars

    fig, ax = plt.subplots(figsize=(10, 8))

    # 3. PLOT BARS
    # We shift the position of the bars by +/- width/2 so they sit side-by-side
    rects1 = ax.bar(x - width/2, first_food_data, width, label= label_1, color='#66b3ff')
    rects2 = ax.bar(x + width/2, second_food_data, width, label= label_2, color='#ff9999')

    # 4. STYLING & LABELS
    ax.set_ylabel('Nutrient Density (grams per 100g)')
    ax.set_title('Nutrient Density Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(nutrients)
    ax.legend()

    
    # Add Text 1: Positioned below the axis, aligned left
    if False:
        """
        if 'ingredients' in first_food_obj:
            fig.text(
                0.05, 0.20, # x=5% from left, y=20% from bottom (in figure coordinates)
                f"{first_food_obj['description']}- ingredients: \n{first_food_obj['ingredients'][:150]}", 
                wrap=True, 
                fontsize=9, 
                color='#66b3ff', # Match bar color
                transform=fig.transFigure # Use figure coordinates for stability
            )
        
        if 'ingredients' in second_food_obj:
        # Add Text 2: Positioned slightly lower
            fig.text(
                0.05, 0.15, # x=5% from left, y=15% from bottom
                f"{second_food_obj['description']}- ingredients: \n{second_food_obj['ingredients'][:150]}", 
                wrap=True, 
                fontsize=9, 
                color='#ff9999', # Match bar color
                transform=fig.transFigure
            )
        """

    # Optional: Add the specific numbers on top of the bars for clarity
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    
    return fig

def load_stored_json(memoization_file_name):
    # feature 1
        # storing previously searched food data.
    if not os.path.exists(memoization_file_name):
        dict_memoization = {}
    else:
        with open(memoization_file_name, 'r') as file_obj:
            dict_memoization = json.load(file_obj)
    return dict_memoization

def save_json(memoization_file_name, dict_memoization):
    with open(memoization_file_name, 'w') as file_obj:
        json.dump(dict_memoization, file_obj)
    print("Saved file, holding results")

def chk_nutrient_filter(chk_data, dict_filter_data, maximum):
    try:
        i = 0
        new_max = 0
        matched = True
        for key in dict_filter_data:
            if dict_filter_data[key] <= chk_data[i]:
                new_max += 1
            else:
                matched = False
            i += 1
        return matched, max(new_max, maximum)
    except:
        print(f"ERROR FACED AT LINE 165; values: {chk_data, dict_filter_data}")
        streamlit.write(f"ERROR FACED AT LINE 165; values: {chk_data, dict_filter_data}")
        streamlit.rerun()

def main():

    # setting up cross session variables.
    if 'count' not in streamlit.session_state:
        streamlit.session_state.count = 0

    memoization_file_name = "dict_memoization.json"

    if 'loaded' not in streamlit.session_state:
        dict_memoization = load_stored_json(memoization_file_name)
        streamlit.session_state.loaded = 1
        streamlit.session_state.dict_mem = dict_memoization
        # loading api key
        try:
            API_KEY = streamlit.secrets["USDA_API_KEY"]
            streamlit.session_state.api_key = API_KEY
        except:
            streamlit.error("API Key not found!")
            streamlit.stop()

    dict_memoization = streamlit.session_state.dict_mem

    SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


    # START OF PROGRAM

    streamlit.title("Food Nutrient Program")
    
    # INPUT
    with streamlit.form(key = "Form_1"):
        
        input_box_1, input_box_2 = streamlit.columns(2)
        # 1st food item
        input_box_1 = input_box_1.text_input("Enter first food to compare: ").lower()
        # 2nd food item
        input_box_2 = input_box_2.text_input("Enter second food to compare: ").lower()

    # Multiselect nutrient
            #  Sends a list, which a user can see IN UI- scrollable, and select them, appearing like tabs on selected space
        streamlit.subheader("Select the Nutrients to display")
        list_nutrients = ['Protein', 'Total lipid (fat)', 'Carbohydrate, by difference', 'Energy', 'Alcohol, ethyl', 'Water', 'Caffeine', 'Theobromine', 'Total Sugars', 'Fiber, total dietary',
                          'Calcium, Ca', 'Iron, Fe', 'Magnesium, Mg', 'Phosphorus, P', 'Potassium, K', 'Sodium, Na', 'Zinc, Zn', 'Copper, Cu', 'Selenium, Se', 'Retinol', 'Vitamin A, RAE',
                          'Carotene, beta', 'Carotene, alpha', 'Vitamin E (alpha-tocopherol)', 'Vitamin D (D2 + D3)', 'Cryptoxanthin, beta', 'Lycopene', 'Lutein + zeaxanthin',
                          'Vitamin C, total ascorbic acid', 'Thiamin', 'Riboflavin', 'Niacin', 'Vitamin B-6', 'Folate, total', 'Vitamin B-12', 'Choline, total', 'Vitamin K (phylloquinone)',
                          'Folic acid', 'Folate, food', 'Folate, DFE', 'Vitamin E, added', 'Vitamin B-12, added', 'Cholesterol', 'Fatty acids, total saturated',
                          'SFA 4:0', 'SFA 6:0', 'SFA 8:0', 'SFA 10:0', 'SFA 12:0', 'SFA 14:0', 'SFA 16:0', 'SFA 18:0', 'MUFA 18:1', 'PUFA 18:2', 'PUFA 18:3', 'PUFA 20:4', 'PUFA 22:6 n-3 (DHA)',
                          'MUFA 16:1', 'PUFA 18:4', 'MUFA 20:1', 'PUFA 20:5 n-3 (EPA)', 'MUFA 22:1', 'PUFA 22:5 n-3 (DPA)', 'Fatty acids, total monounsaturated', 'Fatty acids, total polyunsaturated']
        
        selected_nutrients = streamlit.multiselect("", options = list_nutrients, default= ['Energy', 'Protein', 'Total lipid (fat)', 'Fiber, total dietary'])

        streamlit.subheader("Move slider to apply minimum nutrition value in search")
        if 'dict_filter_values' not in streamlit.session_state:
            streamlit.session_state.dict_filter_values = {}
        for i in selected_nutrients:
            streamlit.session_state.dict_filter_values[i] = streamlit.slider(i, 0, 100)


        choice = streamlit.radio("Show bad nutrient graph?", ["No", "Yes"], horizontal=True)

        if choice == "Yes":
            streamlit.session_state.show_bad = True
            streamlit.write("Bad nutrient selection, max criteria, graph")
            selected_nutrients_bad = streamlit.multiselect("Select bad nutrients to compare: ", ['Fatty acids, total saturated', 'Total Sugars', 'Cholesterol', 'Sodium, Na'], default=['Fatty acids, total saturated', 'Total Sugars', 'Cholesterol'])
            
        else:
            streamlit.session_state.show_bad = False

        streamlit.form_submit_button("Apply")
        
    # BUTTON, which also sends api request
        button_1 = streamlit.form_submit_button("Submit")

    if 'past_search' not in streamlit.session_state:
        streamlit.session_state.past_search = True

    if not streamlit.session_state.past_search:
        print(f"Did not find any results for food: {streamlit.session_state.food_name}")
        print(f"Please Change food name and try again\n")
        streamlit.write(f"Did not find any results for food: {streamlit.session_state.food_name}")
        streamlit.write(f"Please change Food Name and Try again")
    if button_1:
        if (not input_box_1 ) or (not input_box_2):
            streamlit.write("Enter food names!")
            streamlit.stop()
        with streamlit.spinner(f"\nSearching for food: {input_box_1}..."):
            foods = request_food(SEARCH_URL, streamlit.session_state.api_key, input_box_1, MAX_PER_REQUEST, dict_memoization)
            if foods == None:
                streamlit.session_state.past_search = None
                streamlit.session_state.food_name = input_box_1
                streamlit.rerun()
            else:
                streamlit.session_state.past_search = True
            max_old = 0
            result = 0
            for i in range(len(foods)):
                first_food = foods[i]
                first_data = get_nutrients_food(first_food, selected_nutrients)
                match, max = chk_nutrient_filter(first_data, streamlit.session_state.dict_filter_values, max_old)
                if (match):
                    result = i
                    break
                elif (max_old < max):
                    result = i
                    max_old = max
            else:
                first_food = foods[result]
                first_data = get_nutrients_food(first_food, selected_nutrients)
        print(f"Obtained first food at {result+1}th filter check")
        streamlit.success(f"Found- {first_food["description"]}")
        #obtain relevant nutrients of first food

        with streamlit.spinner(f"Searching for food: {input_box_2}..."):
            foods = request_food(SEARCH_URL, streamlit.session_state.api_key, input_box_2, MAX_PER_REQUEST, dict_memoization)  
            if foods == None:
                streamlit.session_state.past_search = None
                streamlit.session_state.food_name = input_box_2
                streamlit.rerun()
            max_old = 0
            result = 0
            for i in range(len(foods)):
                second_food = foods[i]
                second_data = get_nutrients_food(second_food, selected_nutrients)
                match, max = chk_nutrient_filter(second_data, streamlit.session_state.dict_filter_values, max_old)
                if (match):
                    result = i
                    break
                elif (max_old < max):
                    result = i
                    max_old = max
            else:
                second_food = foods[result]
        print(f"Obtained second food at {result+1}th filter check\n")
        streamlit.success(f"Found: {second_food["description"]}")
    
        # PLOT a bar graph of the 2 foods

        streamlit.title(f"\nBar graph of nutrients")
        streamlit.pyplot(graph_food(first_food, second_food, first_data, second_data, selected_nutrients))

        if 'ingredients' in first_food:
            streamlit.write(f"{first_food["description"]} ingredients: ")
            streamlit.write(f"{first_food["ingredients"]}")
        if 'ingredients' in second_food:
            streamlit.write(f"{second_food["description"]} ingredients: ")
            streamlit.write(f"{second_food["ingredients"]}")


        if streamlit.session_state.show_bad:
            first_data_b = get_nutrients_food(first_food, selected_nutrients_bad)
            second_data_b = get_nutrients_food(second_food, selected_nutrients_bad)

            streamlit.title(f"\nBar graph of the bad nutrients")
            streamlit.pyplot(graph_food(first_food, second_food, first_data_b, second_data_b, selected_nutrients_bad))

        streamlit.session_state.count += 1  # keeps track of number of times program was executed
        streamlit.write(f"\n\nExecuted program {streamlit.session_state.count} times in this session!")

    # Below code makes fn 'save_json' run only when terminating
    # every time atexit.register(fn_name) is called, sends the fn to a queue, which runs at program termination
        # Below makes it call atexit.register only once

    if streamlit.button("Save"):
        with streamlit.spinner(f"\nSaving results to  cache json file: {memoization_file_name}..."):
            save_json(memoization_file_name, dict_memoization)
        streamlit.write(f"Saved the seatch results to cache json file: {memoization_file_name}")


    if "terminated" not in streamlit.session_state:
        atexit.register(save_json, memoization_file_name, dict_memoization)
        streamlit.session_state.terminated = True

if __name__ == "__main__":
    main()

