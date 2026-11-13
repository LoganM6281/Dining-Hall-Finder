from drafter import *
from dataclasses import dataclass
import json
set_website_title("Dining Hall Finder")

set_site_information(
    author="Logan Mattie",
    description="A simple dining hall menu viewer for UD students.",
    sources="ChatGPT",
    planning=Link(
        "CS1 Final Project Design (PDF)",
        "https://github.com/LoganM6281/Dining-Hall-Finder/blob/main/Copy%20of%20CS1%20Final%20Project%201_%20Design%20%281%29.pdf",
    ),
    links=["https://github.com/LoganM6281/Dining-Hall-Finder"],
)
RATINGS_KEY = "menu-lookup-ratings"
'''LLM Written Code:'''
def save_rating(food_name: str, rating: int) -> None:
    '''Saves ratings to a seperate file using json (JavaScript Object Notation).
    from js import localStorage format for storing data over multiple runs of a project, made
    for Java but can be used in python as well.'''
    #2nd part LLM Written
    from js import localStorage  # type: ignore[import-not-found]
    saved = localStorage.getItem(RATINGS_KEY)
    scores_by_food = json.loads(saved) if saved else {}
    scores_by_food.setdefault(food_name, []).append(rating)
    localStorage.setItem(RATINGS_KEY, json.dumps(scores_by_food))
'''End of LLM Written Code. Import json helps create a seperate file that is kept which will keep ratings, this file survives restarts because of json, it is important to be
able to track ratings'''
text = "Food+calorie.txt"
info = open(text)
food_lines = info.read()
food_lines = food_lines.splitlines()
@dataclass
class Ratings:
    '''
    food_name: name of food that has a rating
    ratings: all of the given ratings for said food, average will be taken with this information'''
    food_name: str
    ratings: list[int]
#LLM Written Code
def load_ratings() -> list[Ratings]:
    '''Pulls ratings from json, Json is a format for storing data over multiple runs of a project, made
    for Java but can be used in python as well. here, localStorage keeps information between runs, js is where it is kept'''
    try:
        from js import localStorage
    except ImportError:
        # Drafter also runs startup code in regular Python.
        return []

    saved = localStorage.getItem(RATINGS_KEY)
    if not saved:
        return []

    return [
        Ratings(food_name, scores)
        for food_name, scores in json.loads(saved).items()
    ]
#End of LLM Written Code
@dataclass
class State:
    '''
    Four attributes of state, current_food is which food you are currently on
    avg_ratings: is an average of all ratings of given food
    hall_open: lets you know if the hall is currently open at time given
    Rating: a list of ratings for all foods that is run through to get averages
    '''
    current_food: str
    avg_ratings: float
    hall_open: bool
    time_changed: bool
    Rating: list[Ratings]
@dataclass
class Food:
    '''
    Four Attributes:
    name: The name of the food
    calories: how many calories are in the food
    is_vegetarian: whether or not it is vegetarian
    '''
    name: str
    calories: int
    is_vegetarian: bool
def get_avg(current: Ratings) -> float:
    '''
    Parameters:
    current: takes the current list of all ratings objects and uses it to find the average of
    the ratings for a certain food, food is decided outside of this function
    Returns:
    A float representing the average rating of the food
    '''
    total = 0
    count = 0
    for num in current.ratings:
        total += num
        count += 1
    return (total / count)
@route
def check_hours(state: State, time: str) -> Page:
    '''
    Parameters:
    time: what time it currently is, chosen by the user on the index page
    Returns:
    Whether or not dining hall is currently open and modifies the hall_open attribute of State
    '''
    if(time == "Enter"):
        return index(state, time)
    time_list = time.split(" ")
    if (time_list[1]) == "AM":
        if(int(time_list[0]) >= 7):
            state.time_changed = True
            state.hall_open = True
        else:
            state.time_changed = True
            state.hall_open = False
    elif (time_list[1] == "PM"):
        if(int(time_list[0]) <= 8):
            state.time_changed = True
            state.hall_open = True
        else:
            state.time_changed = True
            state.hall_open = False
    return index(state, time)
    

@route
def index(state: State, time: str = "") -> Page:
    opened = ""
    if(state.time_changed == False):
        opened = ""
    else:
        if(state.hall_open == True):
        
             opened = "Hall open!"
        else:
             opened = "Hall Closed!"
    return Page(state, [
        Header("Menu Lookup"),
        "What time is it?",
        SelectBox("time", ["Enter", "12 AM", "1 AM","2 AM","3 AM","4 AM","5 AM","6 AM","7 AM","8 AM","9 AM","10 AM","11 AM","12 PM","1 PM","2 PM","3 PM","4 PM","5 PM","6 PM","7 PM","8 PM","9 PM","10 PM","11 PM"],default_value=time, on_change = check_hours),
        "\n",
        
        Header(opened),
        "Know what you want?",
        TextBox("Enter_Food", state.current_food),
        Button("Search", "search"),
        "\n",
        "Don't know what you want?",
        
        "Choose a type of food",
        "\n",
        Button("Main Dish", "main_dish"),
        
        Button("Protein", "protein"),
        Button("Grain", "grain"),
        Button("Vegetable", "vegetable"),
        Button("Fruit", "fruit"),
        Button("Sauce", "sauce"),
        Button("Dairy", "dairy"),
        Button("Beverage", "beverage")
        
    ])
@route
def rating_entered(state: State, rating: int) -> Page:
    '''Processes the rating given
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    rating: whole number rating typed by the user that gets put into a list of integers for a specific food
    Returns:
    a page that either updates the rating if rating is valid or asks for a rating again if the rating is invalid
    '''
    if(rating >=1 and rating <= 5):
       save_rating(state.current_food, rating)
       state.Rating = load_ratings()
       return search(state, state.current_food)
    else:
        return Page(state, [
            "Enter a rating 1-5",
            TextBox("rating"),
            Button("Enter rating", "rating_entered")
        ])
            
@route
def main_dish(state: State) -> Page:
    '''
    Searches for foods with the main dish label in food+calories.txt and adds them to a list that gets printed when
    main_dish button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of Main Dish
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
        
        
        if(one_line[-1] == "Main Dish"):
          result += "\n" + one_line[0]
    return Page(state, [
        Header("Main Dishes on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])

@route
def protein(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the protein label in food+calories.txt and adds them to a list that gets printed when
    protein button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of protein
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
       
        
        if(one_line[-1] == "Protein"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Proteins on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def grain(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the grain label in food+calories.txt and adds them to a list that gets printed when
    grain button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of grain
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
    
        
        if(one_line[-1] == "Grain"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Grains on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def vegetable(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the vegetable label in food+calories.txt and adds them to a list that gets printed when
    vegetable button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of vegetable
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
      
        
        if(one_line[-1] == "Vegetable"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Vegetables on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def fruit(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the fruit label in food+calories.txt and adds them to a list that gets printed when
    fruit button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of fruit
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
        '''if(one_line[2] == "Vegetarian"):
            if(one_line[3] == "Fruit"):
                result.append(one_line[0])'''
        
        if(one_line[-1] == "Fruit"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Fruits on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def beverage(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the beverage label in food+calories.txt and adds them to a list that gets printed when
    beverage button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of beverage
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
       
        
        if(one_line[-1] == "Beverage"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Beverages on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def sauce(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the sauce label in food+calories.txt and adds them to a list that gets printed when
    sauce button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of sauce
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
        print(one_line)
        
        
        if(one_line[-1] == "Sauce"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Sauce on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
@route
def dairy(state: State, Enter_Food: str) -> Page:
    '''
    Searches for foods with the dairy label in food+calories.txt and adds them to a list that gets printed when
    dairy button is selected
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    
    Returns:
    a page that contains all dishes that fit in the criteria of dairy
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
      
        
        if(one_line[-1] == "Dairy"):
            result += "\n" + one_line[0]
    return Page(state, [
        Header("Dairy on the menu now:"),
        result,
        "\n",
        Button("Back To Home", index)
    ])
def create_food(contents: list[str]) -> Food:
    '''
    creates a food object from a list of strings, which come from one_line, which is
    a list of one line of food+calorie that contains the food name, calories, whether its vegan, and the dish type
    Parameters:
    contents: list of strings taken from one line of food+calorie.txt with information on food name, calories, whether its vegan, and the
    dish type
    Returns:
    a Food object
    '''
    calories = int(contents[1].split()[0])
    return Food(contents[0], contents[1], contents[2] == "Vegetarian")
@route
def search(state: State, Enter_Food: str) -> Page:
    '''
    Searches through for foods that meet enter_food search
    Parameters:
    state: a variable that gets kept through the entire process, keeps information that gets updated through the program
    Enter_Food: gotten from the person searching for a food, used to find food that either meet the criteria or exactly the same
    Returns: Either a page of the exact food searched or a page with a list of all foods that match query
    '''
    result = ""
    for line in food_lines:
        one_line = line.split(" ) ")
        entry = Enter_Food.strip().lower()
        food_name = one_line[0]
        if(")" in food_name):
            food_name = food_name.replace(")"," ")
        if(food_name.lower() == entry):
            food = create_food(one_line)
            state.current_food = food.name
            rating_result = "No ratings yet."
            
            for food_rated in state.Rating:
                state.avg_ratings = 0.0
                if food_rated.food_name == food.name:
                    state.avg_ratings = get_avg(food_rated)
                    rating_result = "Average rating: " + str(state.avg_ratings)
                    break
            
            return Page(state, [
                Header(food.name),
                "\n" + str(food.calories),
                "\n" + "Vegetarian? " + str(food.is_vegetarian),
                "\n",
                rating_result,
                "Enter a rating from 1 to 5.",
                TextBox("rating"),
                
                Button("Save Rating", "rating_entered"),
                Button("Back To Home", index)
            ])
        elif(entry in food_name.lower()):
            result += "\n" + food_name
    if(result == ""):
        return Page(state, [
            Header("No foods matched search"),
            "\n",
            Button("Back To Home", index)
        ])
    return Page(state, [
        Header("Foods That Match Search"),
        result,
        "\n",
        Button("Back To Home", index)
        
    ])

                

    

start_server(State("", 0.0, False, False, load_ratings()))           
info.close()
    
    
        
    
    
