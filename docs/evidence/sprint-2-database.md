# Sprint 2 - Implement Database and Display of Test Data


## Sprint Goals

Implement the database, populated with test data. Create queries that retrieve test data, and display this on web pages as needed. Test and refine the queries and data display, so that it stands as the basis of the next sprint.

### Specific Goals

**Edit these goals as needed**

- Implement the database
- Add test data to the database

- Create the following web pages:
    - Home Page - to show all reported hunt entries
    - Hunt Page - To show specifics for one hunt, show all messages for that hunt, add messages to the hunt, users to join hunt, display all users in the hunt, submit final report on the hunt, set the date for hunt, end the hunt,
    - Report Ghost Page: Add new Reported Hunts to the database, and add new photos to the images table that correspond with the hunt. 
    - Login page: To add new users into the database
    - Profile Page: To View users profile
    - Edit profile Page: To Change users profile picture, bio, and delete users account.

- Develop SQL database queries to:
    - Retrieve all hunts from the database (DONE)
    - Retrive all information about a specific hunt (DONE)
    - Update the data on a specific hunt by: 
        - updating the hunt leader (DONE)
        - Updating the date of the hunt (DONE)
        - Updating the status of the hunt

    - Insert accounts into the database (DONE)

    - update information on accounts 
    - delete accounts
    - Add a hunt into the database
    - Add messages into the database
    - Retrieve all messages from the database
    - Retrieve all participant data, and join it to data on the reported hunt table. 
     - sign users up for hunts
    


## Testing displaying all hunts on the home page. 

I am testing that all hunts in the database get displayed onto the home page. 

All the hunts in the database: 
![All hunts in the database](screenshots/all_hunts.png)

The homepage: 
![The homepage with all the hunts in the database displayed](screenshots/homepage.png)

### Changes / Improvements

I decided it would be more helpful if the list was ordered based on when they were reported. 
To fix this, I added 'ORDER BY reportedHunt.dateReported DESC' to the SQL. 
Before: 
![The homepage with all the hunts in the database displayed before](screenshots/homepage.png)

After: 
![The homepage with all the hunts in the database displayed after being ordered by date](screenshots/homepage_ordered.png)

## Testing users can create accounts

I am testing that users can create accounts, and a new row gets inserted into the database. 

(Part of) Users table before: 
![Part of the users table before](screenshots/users_table.png)

(Part of) Users table after: 
![Part of the users table after](screenshots/users_table_after.png)

The two users that I added through the website have now been added to the database. 
Signing up to the website: (TODO convert to GIF later. )
![Signing up to the website](screenshots/signing_up.mov)

### Changes / Improvements
As the system worked correctly, there was no need for any changes. 


## Testing all information gets displayed about a specific hunt. 

I am testing that on the specific hunt page, the correct information about the hunt is displayed. This includes the usernames of who reported the hunt, who the hunt leader is (if there is one), photos that have been sent in, the description given about the hunt, and when it was reported. 

Hunt information: 

![Hunt information 1](screenshots/hunt_information_1.png)
![Hunt information 2](screenshots/hunt_information_2.png)

And the photo that was submitted: 

![Photo submitted](screenshots/image_for_hunt.png)

Hunt Page: 

![Top of hunt page](screenshots/top_of_hunt.png)
![Bottom of hunt page](screenshots/bottom_of_hunt.png)

The hunt information displays correctly onto the page, including the username of the person who reported the hunt and the image, proving I did my joins correctly. 

### Changes / Improvements

I decided it would be better if instead of saying 'hunt leader is None' it instead said 'There is no hunt leader yet'. 

Before: 
![Bottom of hunt page](screenshots/bottom_of_hunt.png)

After:
![Bottom of hunt page, with new dialog.](screenshots/there_is_no_hunt_leader.png)


## Testing hunt leader can be added from hunt page. 

I am testing that the first person who signs up to the hunt becomes the hunt leader. 

Before signing up: 
![No hunt leader](screenshots/no_hunt_leader.png)

Signing up: 

![signing up for the hunt](screenshots/signing_up_for_hunt.gif)

I signed up using my account 'Pikmin Pikmin' with the ID 11

![Signed up for the hunt](screenshots/signed_up.png)

The Pikmin account becomes the hunt leader.

I then joined the hunt from a second account, to verify the hunt leader would not change with a new account attatched.  

Hunt leader before signing up:
![before_signing_up](screenshots/before_signing_up.png)

Signing up from account 2
![Signing up from account 2](screenshots/leader_signing_up_from_account_2.gif)

Hunt leader after signing up: 
![after signing up (It's the same photo. It's a lot of effort to get a second photo that shows the *exact* same thing.)](screenshots/before_signing_up.png)

The hunt leader did not change with a second account. 

### Changes / Improvements

As this worked as required, no changes were necesary. 


## Testing that date of hunt can be updated. 

I am testing that the date of the hunt can be updated on the hunt page. 

Before setting the date in the hunt we reported earlier:
![Photo of the database before setting the date. It reads null under date_of_hunt ](screenshots/date_before_setting.png)

Setting the date in my Pikmin Pikmin account:
![Setting the date of the hunt](screenshots/date_setting.gif)

Database after: 
![Date reads in database](screenshots/date_after_setting.png)


### Changes / Improvements

As this feature works as intended, there is no need for changes.



## Testing that account details can be updated.

I am testing that account details (bio/profile picture) can be updated.  

Database before editing the profile picture:
![Database before](screenshots/profile_before.png)

Editing the profile
![A gif of editing the profile picture](screenshots/profile_updating.gif)

Database after:
![database after](screenshots/profile_after.png)

### Changes / Improvements

As this feature works as intended, no changes were neeeded. 

## Testing accounts can be deleted. 

I am testing that accounts can be deleted. 

Database before I deleted it
![Database before I deleted it](screenshots/delete_before.png)

Deleting the 'pikmin pikmin' account
![Deleting the pikmin pikmin account](screenshots/delete_deleting.gif)

Database After
![Database with a distinct lack of a Pikmin Pikmin account](screenshots/delete_after.png)
### Changes / Improvements

AS this feature works as intended, no changes were needed. 

## Testing hunts can be created. 

I am testing that hunts can be created. 

Adding hunt:
![Adding hunt](screenshots/hunt_adding.gif)

(part of) Database after:
![Database with the new hunt added](screenshots/hunt_database.png)

### Changes / Improvements

I noticed that the status defaulted to 'open' without a capital.
Status before: 
![Status before](screenshots/status_before.png)

Status after I changed it:
![status reading 'Open' with a capital](screenshots/Status_after.png)

## Testing the status of the hunt updates

I am testing that the status of the hunt updates when it is the hunt date. 

Here is a hunt set for the 12th of October at 11:55
![Hunt set for date above](screenshots/status_update_before.png)

### Changes / Improvements

While this worked sometimes, this specific time it didn't. 
Through further testing, I discovered that because of the Docker container the system runs through, date.today() was returning the date in UTC, but the reportedHunt date was for NZsT. 

To fix this, I converted the dates to UTC to store in the database, and made them display in local time for people elsewhere. 

Date code before changes: 
![date code before](screenshots/date_code_before.png)

Date code after. 
![Date code after. Notably, now using a nifty try & except function, which I learnt for this function alone.](screenshots/date_code_after.png)

I then also updated the form to add inline javascript, taking the date and converting to UTC. 
![Form script](screenshots/date_code_form.png)

Finally, I changed the comparison to work in UTC.
![Date change](screenshots/date_code_utc.png)

Finally, I tested this, to see that it worked. 

![date code final](screenshots/date_code_final.gif)
In the final frame, the status has changed to hunting and the website changed. 

I then also moved the countdown to this page, as I preferred it over here. 

## Testing messages get added to the messages table for a specific hunt. 

I am testing that the correct messages show up for the hunt, and that they are attributed to the correct people. 

The hunt I am sending messages to has an ID of 19, and currently there are no messages with the huntID 19. 
![Messages for other hunts, but no messages for this hunt](screenshots/messages_before.png)

I added three messages to the hunt. All three were successfully by Pikmin Pikmin, meaning I have done my joins correctly. 

![All three messages displaying on the webpage.](screenshots/messages_added.png)

Then in the database: 

![Messages in the database](screenshots/messages_after.png)

### Changes / Improvements
No changes needed to be made here.

## Testing all messages get retrieved from the database

I am testing that all messages can be retrieved from the database on a specific hunt. 

This hunt is huntID 20, and in the database there's three messages recorded.

![messages in the database](screenshots/messages_display_before.png)

Then on the webpage: 

![messageson the page](screenshots/messages_display_after.png)

### Changes / Improvements

As this feature worked as intended, there was no need for changes/improvements. 

## Testing a list of participants gets displayed on the hunt page.

I am testing that the list of participants in the hunt gets displayed on the hunt page, with their first name and their last name. This means I have correctly joined the Participants table to both the users & the reportedHunt table. 

### Changes / Improvements

Replace this text with notes any improvements you made as a result of the testing.

**PLACE SCREENSHOTS AND/OR ANIMATED GIFS OF THE IMPROVED SYSTEM HERE**

v
v


## Testing all information gets displayed about a specific hunt. 

I am testing that on the specific hunt page, the correct information about the hunt is displayed. 

**PLACE SCREENSHOTS AND/OR ANIMATED GIFS OF THE TESTING HERE**

### Changes / Improvements

Replace this text with notes any improvements you made as a result of the testing.

**PLACE SCREENSHOTS AND/OR ANIMATED GIFS OF THE IMPROVED SYSTEM HERE**

## ETC...


## Sprint Review

Replace this text with a statement about how the sprint has moved the project forward - key success point, any things that didn't go so well, etc.

