# Sprint 3 - Developing a Minimum Viable Product (MVP)


## Sprint Goals

Continue to develop the web application to the point that it provides all key functionality of the system. Test and refine it so that it can serve as the basis for the final phase of development.

### Specific Goals

- Create the following web pages:
    - login page for users to login
    - 
    - Etc.
- Develop SQL database queries to:
    - Add a new ...
    - Etc.


## Testing users can login 

I am testing that users can login to the website, and that the UI changes when I login. I am also testing that users cannot view hunt specifics while being logged out. 

Login changes include:
- Signup button disappears when user is logged in
- Login button gets replaced with logout button
- Profile button appears. 

Hunts should then be able to be clicked on when logged in. 

Logging in:
![Logging in](screenshots/login_logging_in.gif)

From the video, hunts become clickable when you login, and the UI changes. 

### Changes / Improvements
As this worked as intended, there was no need for changes. 


## Testing Ghost locations get displayed on a map.

I am testing that the ghost location displays on a map in the hunt page. 

Location of the hunt: 
![Hunt at 58 Australia Court Newport Australia](screenshots/map_location.png)

Location the map displays: 
![Map showing a place in Australia](screenshots/map_map.png)

Actual place:
![Map Showing where it actually is (its the same spot)](screenshots/map_google.png)

The map works as intended. 

### Changes / Improvements

As this feature works as intended, there is no need for changes. 


## Testing messages live update on the website

Testing messages live update on the website, without the user having to reload for new messages. 

Pikmin account sending messages to the hunt: 
![The 'pikmin pikmin' account sending messages](screenshots/messages_sending.gif)

### Changes / Improvements

As the website works as intended, there is no need for changes. 

## Testing hunts/hunt statuses appear correctly on the home page. 
Similar to the test in sprint 2, I am this time testing that the status appear next to them, and they are clickable. 

![Hunts displaying the statuses.](screenshots/display_status_beofre.png)


### Changes / Improvements

I decided it could be helpful/interesting to current/potential users if a map at the top of the screen showed the pins of all the hunts currently in the database; similar to the one on the hunt page. 

![New map on the home page.](screenshots/map_added.png)

This can help draw in potential users by seeing if there are ghost locations near them. This also included a database change.

New database:
![New database with LAT & LON coloums added](screenshots/database_v5.png)

*Note: The lat/lon columns are of type real, not of bigint. Bigint doesn't store decimals, SQLite doesn't have a type decimal, and because they store GPS co-ords I need them to store decimals; hence real. DrawSQL doesn't have an option for real type so I went with bigint. 

I then also decided it would look better again if I added popups to the markers with the address of the ghost sighting. 

Map popup when you click on the markers: 
![Map popup](screenshots/map_popup.png)

## Testing addresses autofill on the report page. 

I am testing that I can start typing an address and that it will autofill. 

Testing autofill by typing in addresses both kiwi and then from overseas: 

![Map autofilling](screenshots/autofill_working.gif)



### Changes / Improvements

As the website works as intended, there is no need for changes here. 


## Testing users can send a ghost report at the end of the hunt

While this technically counts as a database interaction, I am testing it again here that the front end & back end work as intended. 

Database before the report is sent: 
![Database before sending the report](screenshots/report_before.png)

Sending a report from the website: 
![Sending a final report](screenshots/report_sending_final.gif)

### Changes / Improvements

No changes were needed as the system works as intended 

## Sprint Review

Replace this text with a statement about how the sprint has moved the project forward - key success point, any things that didn't go so well, etc.

