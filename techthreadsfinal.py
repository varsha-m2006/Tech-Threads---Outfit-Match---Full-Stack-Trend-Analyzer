#TECH THREADS- OUTFIT MATCH (FULL STACK PROJECT)


#importing neccesary modules
import requests
import tkinter as tk
import sqlite3
from pytrends.request import TrendReq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#creating connector and cursor for given sql database
conn=sqlite3.connect('final.db')
curr=conn.cursor()


#creating table with given set of fields
curr.executescript('''
    DROP TABLE if exists USERS;
                   
    CREATE TABLE USERS(
                   NO INTEGER,
                   LOCATION VARCHAR(128),
                   WEATHER INTEGER,
                   MOOD VARCHAR(128),
                   EVENT VARCHAR(128),
                   DRESS_TOP VARCHAR(128),
                   TYPE VARCHAR(128),
                   FABRIC VARCHAR(128),
                   COLOUR VARCHAR(128),
                   JEANS_SKIRT VARCHAR(128),
                   LENGTH VARCHAR(128),
                   TYPE_BOTTOM VARCHAR(128),
                   FABRIC_BOTTOM VARCHAR(128),
                   COLOUR_BOTTOM VARCHAR(128),
                   EMAIL VARCHAR(128),
                   MATCH_PERCENTAGE INTEGER

                   );
'''
)


#to retrieve real-time temperature from Open Weather API based on inputed user's location
def api_temp(user_id):
    global curr 

    #fetching location from database for given user id
    curr.execute('SELECT LOCATION FROM USERS WHERE NO = ?', (user_id,))
    loc=curr.fetchone()[0]

    API_key = "bc63677d455d15df2bda4d5182015416"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={loc}&appid={API_key}&units=metric"

    #parsing data retrived to return real-time temperature of given location
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    temperature = data['main']['temp']
    return temperature

#to retrieve geocode from Open Cage Data API, for given user's location - geocoding
def geocode(user_id):
    global curr 

    #fetching user's location from database
    curr.execute('SELECT LOCATION FROM USERS WHERE NO = ?', (user_id,))
    loc=curr.fetchone()[0]

    API_key = "c6843e03c198458f91a1c00a594c2ba3"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={loc}&key={API_key}"
    
    #parsing data to find country code for given location(ex: Dubai - AE, New York - US)
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    geocode = data['results'][0]['components']['country_code'].upper()
    return geocode

#fetching all data from database for given user_id
def get_user_data(user_id):
    curr.execute('''
        SELECT MOOD, EVENT, WEATHER, DRESS_TOP, TYPE, FABRIC, COLOUR,
               JEANS_SKIRT, LENGTH, TYPE_BOTTOM, FABRIC_BOTTOM, COLOUR_BOTTOM
        FROM USERS WHERE NO = ?
    ''', (user_id,))
    
    return curr.fetchone()

#generating keywords
def generate_keywords(mood, event, temp, outfit_keywords=None):

    #creating keywords list
    keywords = []

    #adding all possible combinations based on user's choices
    keywords.append(f"{mood} {event} outfit")
    keywords.append(f"{event} fashion")
    keywords.append(f"{event} wear")
    keywords.append(f"{mood} style")

    #adding weather keywords based on temperature
    if temp >= 24:
        keywords.append("summer fashion")
    elif 15 <= temp < 24:
        keywords.append("autumn fashion")
    elif 11 <= temp < 15:
        keywords.append("spring outfits")
    else:
        keywords.append("winter outfits")

    #even more keywords to broaden the search
    if outfit_keywords:
        for kw in outfit_keywords[:2]:  
            keywords.append(f"{kw} fashion")

    
    return keywords[:5]  


#loosely matching user's choices to top trending keywords in Google
def loose_match(outfit_kw, phrase):
    outfit_parts = outfit_kw.replace('-', ' ').replace('+', ' ').split()
    phrase_parts = phrase.lower().replace('-', ' ').replace('+', ' ').split()
    return any(part in phrase_parts for part in outfit_parts)

#matching percentage
def calculate_match_percentage(user_id, code):
    user_data = get_user_data(user_id)
    if not user_data:
        return 0, [], []

    
    mood, event, temperature, dress_top, type, fabric, colour, \
    jeans_skirt, length, type_bottom, fabric_bottom, colour_bottom = user_data

    #outfit keywords added
    if dress_top == "Dress":
        outfit_keywords = [dress_top, type, fabric, colour]
    else:
        outfit_keywords = [dress_top, type, fabric, colour,
                           jeans_skirt, type_bottom, fabric_bottom, colour_bottom, length]

    outfit_keywords = [kw.lower() for kw in outfit_keywords if kw and kw != "N/A"]

    
    trend_keywords = generate_keywords(mood, event, temperature, outfit_keywords)
    trend_keywords = [kw for kw in trend_keywords if kw and isinstance(kw, str)][:5]

    #pytrends used to access google search engine for any location
    pytrends = TrendReq(hl='en-' + code, tz=360)

    #trending keywords in the last 3 months
    pytrends.build_payload(trend_keywords, geo=code, timeframe='today 3-m')

    #related keywords/ querries also accessed to broaden the scope
    related_trend_queries = pytrends.related_queries()
    related_terms = set()

    for kw in related_trend_queries:
        if related_trend_queries[kw]['top'] is not None:
            for entry in related_trend_queries[kw]['top']['query']:
                related_terms.add(entry.lower())

    outfit_keywords_for_trends = outfit_keywords[:5]  
    pytrends.build_payload(outfit_keywords_for_trends, geo=code, timeframe='today 3-m')
    related_outfit_queries = pytrends.related_queries()

    for kw in related_outfit_queries:
        if related_outfit_queries[kw]['top'] is not None:
            for entry in related_outfit_queries[kw]['top']['query']:
                related_terms.add(entry.lower())

    
    print("Trend Keywords:", trend_keywords)
    print("Outfit Keywords (search terms):", outfit_keywords_for_trends)
    print("Related Trending Queries (combined):", related_terms)
    print("Outfit Keywords (for matching):", outfit_keywords)

    #matched user's choices to trending results in Google is added
    matched = []
    for outfit_kw in outfit_keywords:
        for phrase in related_terms:
            if loose_match(outfit_kw, phrase):
                matched.append(outfit_kw)
                break

    if not outfit_keywords:
        return 0, trend_keywords, []

    #calculating match percentage
    match_percent = round((len(matched) / len(outfit_keywords)) * 100, 1)

    print("Matched Keywords:", matched)
    print("Match %:", match_percent)

    return match_percent, matched, trend_keywords

#to send match percentage summary to user's entered email
def email_summary(email,user_id,temp):
    
    #fetching match percentage that's calculated
    curr.execute('SELECT MATCH_PERCENTAGE FROM USERS WHERE NO = ?', (user_id,))

    match_percent=curr.fetchone()[0]

    #structured mail message created
    body=f'Temperature at Your Location: {temp}°C \nOutfit match percentage: {match_percent}%\nThank You For Using TechThreads.'
    
    msg=MIMEMultipart()
    msg['From']= "varsha6b@gmail.com"
    msg['To']= email
    msg['Subject']="Your Fashion Match Summary"
    msg.attach(MIMEText(body,'plain'))

    #accessing given SMTP server through TLS port(-587), connection created
    smtpObj=smtplib.SMTP("smtp.gmail.com",587)
    #conversation with server started
    smtpObj.ehlo()                                                 
    smtpObj.starttls()
    #login
    smtpObj.login("varsha6b@gmail.com","jgnaphadxowjyobt")
    #sending email..
    smtpObj.sendmail("varsha6b@gmail.com",email,msg.as_string())
    #logging out
    smtpObj.quit()

#to find highest match percatge of given user based on all of user's tries
def highest_match(user_id):
    curr.execute('''
        SELECT * FROM USERS
        WHERE NO = ?
        AND MATCH_PERCENTAGE = (
            SELECT MAX(MATCH_PERCENTAGE) FROM USERS
        )
    ''', (user_id,))


    highest_match_percentage=curr.fetchone()

    return highest_match_percentage


#creating frame that inherits properties of widget container tk.frame
class MyApp(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#fff0f5")
        #properties initialized
        self.root = root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        


        self.pack(fill=tk.BOTH, expand=True)

        self.flow_branch = None
        self.bottom_branch = None

        self.colour1 = '#fff0f5'
        self.colour2 = '#444444'
        self.colour3 = 'WHITE'

        #at first page
        self.current_page_index = 0
        
        #a list of all pages in GUI framework
        self.pages = [self.location_page, self.mood_page,self.event_page,self. type,self.dress1,self.dress2,self.dress3,self.top1,self.top2,self.top3,self.bottom,self.jean1,self.jean2,self.jean3,self.jean4,self.skirt1,self.skirt2,self.skirt3,self.summary,self.end,self.end1]
        
        #to create page container an doager functions called
        self.create_page_container()
        self.create_pager()

        #calls first page
        self.pages[self.current_page_index]()  
    
    #to clear content in frame
    def clear_frame(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    
    
    
    #creating page container, consist of all pages and content
    def create_page_container(self):
        #configuring it's properties, page container created inside main frame
        self.page_container = tk.Frame(self, bg=self.colour1)
        self.page_container.pack(fill=tk.BOTH, expand=True)
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=0)
        self.page_container.rowconfigure(1, weight=1)
        #tk.label is for text like tk.frame is for frames
        self.title_label = tk.Label(self.page_container, bg=self.colour1, fg=self.colour2, font=('Segoe UI', 24))
        self.title_label.pack(pady=(20, 10))
        #content frame created inside page container
        self.content_frame = tk.Frame(self.page_container, bg=self.colour1)
        self.content_frame.pack(expand=True)

    #creating pager, for navigation
    def create_pager(self):
        #created inside main frame and properties configured
        self.pager = tk.Frame(self, bg=self.colour1, height=125)
        self.pager.pack(fill="x", pady=5) 
        self.pager.columnconfigure(0, weight=1)
        self.pager.columnconfigure(1, weight=1)
        self.pager.columnconfigure(2, weight=1)

    #change page algorithm
    def change_page(self, button):
        
        #initial user_id set to 0
        if not hasattr(self, "user_id"):
            self.user_id = 0  

        #page 1: location 
        if button == "Submit":
            location = self.location_entry.get()
            curr.execute('INSERT INTO USERS (NO, LOCATION) VALUES (?, ?)', (self.user_id, location))
            conn.commit()
            temp = api_temp(self.user_id)
            curr.execute('UPDATE USERS SET WEATHER = ? WHERE NO = ?', (temp, self.user_id))
            conn.commit()
            self.current_page_index += 1 #moving to nect page same logic used everywhere

        #page 2: mood
        elif self.current_page_index == self.pages.index(self.mood_page):
            curr.execute('UPDATE USERS SET MOOD = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        #page 3: event
        elif self.current_page_index == self.pages.index(self.event_page):
            curr.execute('UPDATE USERS SET EVENT = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        #page 4: dress or tops+bottoms
        elif self.current_page_index == self.pages.index(self.type):
            curr.execute('UPDATE USERS SET DRESS_TOP = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            if button == "Dress":
                self.current_page_index = self.pages.index(self.dress1)
            elif button == "Top+Bottoms":
                self.current_page_index = self.pages.index(self.top1)

        #dress flow
        elif self.current_page_index == self.pages.index(self.dress1):
            curr.execute('UPDATE USERS SET TYPE = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.dress2)

        elif self.current_page_index == self.pages.index(self.dress2):
            curr.execute('UPDATE USERS SET FABRIC = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.dress3)

        elif self.current_page_index == self.pages.index(self.dress3):
            curr.execute('''
                UPDATE USERS 
                SET COLOUR = ?, JEANS_SKIRT = ?, TYPE_BOTTOM = ?, FABRIC_BOTTOM = ?, COLOUR_BOTTOM = ?
                WHERE NO = ?
            ''', (button, "N/A", "N/A", "N/A", "N/A", self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.summary)

        #top flow
        elif self.current_page_index == self.pages.index(self.top1):
            curr.execute('UPDATE USERS SET TYPE = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.top2)

        elif self.current_page_index == self.pages.index(self.top2):
            curr.execute('UPDATE USERS SET FABRIC = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.top3)

        elif self.current_page_index == self.pages.index(self.top3):
            curr.execute('UPDATE USERS SET COLOUR = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.bottom)

        #page 11: pants or skirts
        elif self.current_page_index == self.pages.index(self.bottom):
            curr.execute('UPDATE USERS SET JEANS_SKIRT = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            if button == "Pants":
                self.current_page_index = self.pages.index(self.jean1)
            elif button == "Skirt":
                curr.execute('UPDATE USERS SET LENGTH = ? WHERE NO = ?', ("N/A", self.user_id))
                conn.commit()
                self.current_page_index = self.pages.index(self.skirt1)

        #pant/jeans flow
        elif self.current_page_index == self.pages.index(self.jean1):
            curr.execute('UPDATE USERS SET LENGTH = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        elif self.current_page_index == self.pages.index(self.jean2):
            curr.execute('UPDATE USERS SET TYPE_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        elif self.current_page_index == self.pages.index(self.jean3):
            curr.execute('UPDATE USERS SET FABRIC_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        elif self.current_page_index == self.pages.index(self.jean4):
            curr.execute('UPDATE USERS SET COLOUR_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.summary)

        #skirts flow
        elif self.current_page_index == self.pages.index(self.skirt1):
            curr.execute('UPDATE USERS SET TYPE_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        elif self.current_page_index == self.pages.index(self.skirt2):
            curr.execute('UPDATE USERS SET FABRIC_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index += 1

        elif self.current_page_index == self.pages.index(self.skirt3):
            curr.execute('UPDATE USERS SET COLOUR_BOTTOM = ? WHERE NO = ?', (button, self.user_id))
            conn.commit()
            self.current_page_index = self.pages.index(self.summary)

        #page 19: summary for match percatge and email entry
        elif self.current_page_index == self.pages.index(self.summary) and button == "Email":
            email = self.email_entry.get()
            curr.execute('UPDATE USERS SET EMAIL = ? WHERE NO = ?', (email, self.user_id))
            conn.commit()
            temp=api_temp(self.user_id)
            email_summary(email,self.user_id,temp)
            self.current_page_index = self.pages.index(self.end)

        #page 20/21: try again + show highest perctage option
        elif self.current_page_index == self.pages.index(self.end) or  self.current_page_index == self.pages.index(self.end1) :
            if button == "Yes":
                self.user_id+= 1
                self.current_page_index = 0
            elif button == "No":
                print("Done")
                conn.commit()
                return
            elif button=="Highest":
                self.current_page_index=self.pages.index(self.end1)
            

        self.pages[self.current_page_index]()

    #creating of all pages

    def location_page(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        #text
        tk.Label(
            self.content_frame,
            text="Welcome To Tech Threads - Outfit Match",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 14),
            wraplength=600,
            justify=tk.LEFT
        ).pack(pady=10,anchor="center")

        tk.Label(
            self.content_frame,
            text="Enter your location:",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        #tk.entry used for entry/typing 
        self.location_entry = tk.Entry(self.content_frame,justify='center')
        self.location_entry.pack()
        
        #tk.button is used to create buttons
        tk.Button(
            self.content_frame,
            text="Save Location",
            command=lambda: self.change_page("Submit"),     #invoked only when button is clicked
            bg=self.colour2,
            fg=self.colour3
        ).pack(pady=10,anchor="center")

    #simlar logic used for all pages

    def mood_page(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Mood Are You in Today?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        moods = ["Happy", "Relaxed", "Energetic", "Confident", "Romantic", "Casual", "Professional", "Tired", "Adventurous", "Reserved"]
        
        for mood in moods:
            tk.Button(
                self.content_frame,
                text=mood,
                command=lambda b=mood: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def event_page(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Event are you going for?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        events = ["Casual", "Work / Office", "Formal", "Party", "Date", "Wedding", "Outdoor", "Interview"]

        for event in events:
            tk.Button(
                self.content_frame,
                text=event,
                command=lambda b=event: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def type(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="Dress or Top+Bottoms?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        choices=['Dress', 'Top+Bottoms']

        for choice in choices:
            tk.Button(
                self.content_frame,
                text=choice,
                command=lambda b=choice: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def dress1(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What type of Dress",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        dress_types = ["A-line", "Bodycon", "Maxi", "Mini", "Wrap", "Sheath", "Shift", "Ballgown", "Sundress", "Cocktail"]

        for dress_type in dress_types:
            tk.Button(
                self.content_frame,
                text=dress_type,
                command=lambda b=dress_type: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def dress2(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Fabric?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        fabrics = ["Cotton", "Silk", "Linen", "Polyester", "Wool", "Denim", "Chiffon", "Velvet", "Satin", "Leather"]

        for fabric in fabrics:
            tk.Button(
                self.content_frame,
                text=fabric,
                command=lambda b=fabric: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    
    def dress3(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Colour?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        colours = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Beige", "Brown", "Grey", "Orange"]

        for colour in colours:
            tk.Button(
                self.content_frame,
                text=colour,
                command=lambda b=colour: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    def top1(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)

        tk.Label(
            self.content_frame,
            text="What Type of Top?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        top_types = ["T-shirt", "Blouse", "Tank Top", "Crop Top", "Shirt", "Sweater", "Hoodie", "Cardigan", "Bodysuit", "Tube Top"]

        for top_type in top_types:
            tk.Button(
                self.content_frame,
                text=top_type,
                command=lambda b=top_type: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def top2(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Fabric?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        fabrics = ["Cotton", "Linen", "Silk", "Satin", "Chiffon", "Polyester", "Rayon", "Denim", "Wool", "Jersey"]

        for fabric in fabrics:
            tk.Button(
                self.content_frame,
                text=fabric,
                command=lambda b=fabric: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    
    def top3(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What is the colour?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        colours = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Beige", "Brown", "Grey", "Orange"]

        for colour in colours:
            tk.Button(
                self.content_frame,
                text=colour,
                command=lambda b=colour: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def bottom(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="Pants or Skirts?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        choices=['Pants','Skirt']

        for choice in choices:
            tk.Button(
                self.content_frame,
                text=choice,
                command=lambda b=choice: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    
    def jean1(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Length of Pants?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        lengths = ["Full Length", "Ankle Length", "Cropped", "Capri", "Knee Length", "Shorts"]

        for length in lengths:
            tk.Button(
                self.content_frame,
                text=length,
                command=lambda b=length: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def jean2(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Shape of Pant?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        types = ["Straight", "Wide-Leg", "Skinny", "Bootcut", "Tapered", "Cargo", "Flared", "Joggers", "Palazzo"]

        for type in types:
            tk.Button(
                self.content_frame,
                text=type,
                command=lambda b=type: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def jean3(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What is the Fabric?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        fabrics = ["Denim", "Cotton Blend", "Stretch Denim", "Polyester Blend", "Corduroy", "Twill", "Linen Blend", "Raw Denim"]

        for fabric in fabrics:
            tk.Button(
                self.content_frame,
                text=fabric,
                command=lambda b=fabric: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    
    def jean4(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What is the colour?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        colours = ["Blue", "Black", "Grey", "White", "Navy", "Light Blue", "Charcoal", "Beige", "Olive", "Brown"]

        for colour in colours:
            tk.Button(
                self.content_frame,
                text=colour,
                command=lambda b=colour: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def skirt1(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What Shape of Pant?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        types = ["A-line", "Pencil", "Mini", "Midi", "Maxi", "Wrap", "Pleated", "Skater", "Asymmetrical", "Tulip"]

        for type in types:
            tk.Button(
                self.content_frame,
                text=type,
                command=lambda b=type: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def skirt2(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What is the Fabric?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        fabrics = ["Cotton", "Denim", "Chiffon", "Silk", "Linen", "Wool", "Satin", "Polyester", "Corduroy", "Leather"]

        for fabric in fabrics:
            tk.Button(
                self.content_frame,
                text=fabric,
                command=lambda b=fabric: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
    
    def skirt3(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="What is the colour?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        colours = ["Black", "White", "Red", "Pink", "Blue", "Beige", "Brown", "Green", "Yellow", "Purple"]
        for colour in colours:
            tk.Button(
                self.content_frame,
                text=colour,
                command=lambda b=colour: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

    def summary(self):
        #api_temp,geocode,calculate_match_percentage functions called
        temp=api_temp(self.user_id)
        code=geocode(self.user_id)
        match_percent,matched,trendy_keywords=calculate_match_percentage(self.user_id,code)

        curr.execute('UPDATE USERS SET MATCH_PERCENTAGE = ? WHERE NO = ?', (match_percent, self.user_id))
        #to save changes
        conn.commit()
        self.title_label.config(text="SUMMARY")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text=f'The Temperature in Current Location:{temp}°C\nMatch Percatge of User Outfit - {match_percent}%\nThis Summary Can be sent to Your Email. Thank You.',
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 14),
            wraplength=600,
            justify=tk.LEFT
        ).pack(pady=10,anchor="center")
        
        tk.Label(
            self.content_frame,
            text="Enter your email:",
            bg=self.colour1,
            fg=self.colour2,
            font=('Arial', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        self.email_entry = tk.Entry(self.content_frame)
        self.email_entry.pack()
        
        tk.Button(
            self.content_frame,
            text="Save email",
            command=lambda: self.change_page("Email"),
            bg=self.colour2,
            fg=self.colour3
        ).pack(pady=10,anchor="center")

    def end(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        tk.Label(
            self.content_frame,
            text="Email Sent",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 14),
            wraplength=600,
            justify=tk.LEFT
        ).pack(pady=10,anchor="center")

        tk.Label(
            self.content_frame,
            text="Would You like to try Again?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        ops=['Yes','No']

        for op in ops:
            tk.Button(
                self.content_frame,
                text=op,
                command=lambda b=op: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
        tk.Button(
                self.content_frame,
                text="Highest Match Percentage",
                command=lambda: self.change_page("Highest"),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")
        
    def end1(self):
        self.title_label.config(text="TECH THREADS - OUTFIT MATCH")
        self.clear_frame(self.content_frame)
        
        highest=highest_match(self.user_id)
        tk.Label(
            self.content_frame,
            text=f'Highest Match Percentage:\n{highest}',
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 14),
            wraplength=600,
            justify=tk.LEFT
        ).pack(pady=10,anchor="center")

        tk.Label(
            self.content_frame,
            text="Would You like to try Again?",
            bg=self.colour1,
            fg=self.colour2,
            font=('Helvetica', 12)
        ).pack(pady=(20, 5),anchor="center")
        
        ops=['Yes','No']

        for op in ops:
            tk.Button(
                self.content_frame,
                text=op,
                command=lambda b=op: self.change_page(b),
                bg=self.colour2,
                fg=self.colour3
            ).pack(pady=10,anchor="center")

#__main__(outside class)
if __name__ == "__main__":
    #root window is created and properties configured
    root = tk.Tk()
    root.title("My App")
    root.geometry("700x600")
    root.resizable(False, False)
    app = MyApp(root)
    root.mainloop()#GUI main loop