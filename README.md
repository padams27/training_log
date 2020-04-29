### CS50 Final Project: 'Winter Training Log' 

### To the user:

my final project is a website that was specifically meant for the annual winter training
competition that is run over the winter break on the heavyweight crew team. it is by class, with
points coming from minutes spent training.

to open the the website i have been using cd into project: training and the using 'flask run'.
once the website has been opened from the cs50.ide, it will take you to a home page. from here a
new user will have to first register by giving their name and class (year of graduation) as well as
a password. otherwise an existing user will just login.

once logged in the user is able to access all pages. the home page displays the most important parts of the
recorded data by class - with minutes per class and number of members of each class. the add page is where the
user should input any training they have done over the previous day. this allows options for what type of
training (e.g. ergo or bike) and then the amount of minutes of each. once this is submitted it is added
to the sql database. the other pages allow further analysis of the data by your class, as well as looking at the
overall rankings and who, out of everyone one on the team, has recorded the most training. in the top right of
the page are options to log out or change your password.

the ultimate aim for the use of this page is to be the class at the end of the holidays with the highest
minutes per person. however the platform can be used at any other time if the database is cleared.
