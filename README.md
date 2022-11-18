# Toronto TTC Trip Planner

CISC/CMPE 204 Modelling Project - 2022 - Group 12

Using data set provided by transitfeeds.com, our program aims to evaluate and provide the most optimal ways one can get from one point to another within Toronto, using just the TTC public transport system. Our project takes into consideration many different variables including transfers, budget, time constraints, etc, and finds the optimal route using propostional logic. 

As the user you will input your starting location, desired ending location, current time, desired arrival time, travel budget, age, extra visiting locations (eg. Toronto Zoo), and other miscellaneous options. 

Using this information, our program will show you a list of trains, buses, and streetcars you need to take at which times in order to reach your location within your budget and time constraints.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.
