from kivy.app import App
from kivy.config import Config

#Screen resolution 
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
#fullscreen
Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'show_cursor', 0)
Config.write()

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from PIL import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from datetime import datetime
from kivy.uix.screenmanager import ScreenManager, Screen
import json
import os
import requests
import base64
import http.client
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from PIL import Image
from io import BytesIO
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from time import time
#for rounded button in main
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, ListProperty

class ApodWindow(Screen): #APOD window
    def on_enter(self): #When the screen is displayed
        self.load_apod() 

    def load_apod(self): #fetch NASA APOD API
            api_key = "fuwbgeljQZLYXyPTRZV71hovCNE5eXAOed3pRVWi"  # Replace with your own key if needed
            url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

            try:
                response = requests.get(url)
                data = response.json()

                self.clear_widgets() # Clear old widgets

                main_layout = BoxLayout(orientation='horizontal', spacing =10)
                

                explanation_label = Label(
                    text=data.get("explanation", ""),
                    text_size=(580, None),
                    font_size="20sp",
                    size_hint_y=None,
                    halign="left",
                    valign="top",
                    padding = 10
                )

                explanation_label.bind(
                    texture_size=lambda instance, value: setattr(instance, 'height', value[1])
                )

                scroll = ScrollView(size_hint=(1, 1))
                scroll.add_widget(explanation_label)

                popup_content = BoxLayout(orientation='vertical', spacing=10, padding=5)
                popup_content.add_widget(scroll)

                # Create and add the Close button
                close_button = Button(
                    text="Close",
                    size_hint=(1, 0.15),
                    font_name= "RiosarkRegular-ZpgLB.otf",
                    font_size='24sp'
                )

                popup = Popup(
                    title=data.get("title", ""),
                    content=popup_content,
                    size_hint=(None, None),
                    size=(600, 500),
                    auto_dismiss= False
                )

                close_button.bind(on_release=popup.dismiss)
                popup_content.add_widget(close_button)

                vert_layout = BoxLayout(orientation='vertical', size_hint_x=0.15, padding = 10, spacing = 10)

                readmorebutton = RoundedButton(
                    text = "Learn\nmore",
                    font_name= "RiosarkRegular-ZpgLB.otf",
                    font_size= "24sp",
                    background_color = (0.30, 0.30, 0.30, 0.75),
                    size_hint=(1,1),
                    pos_hint={"left": 1, "y":0},
                    on_press = lambda x: popup.open()
                )
                vert_layout.add_widget(readmorebutton)

                home_container = RelativeLayout(size_hint=(1, 1))

                # Background image
                homeimage = KivyImage(
                    source="images/home-white-icon (1).png",
                    allow_stretch=False,
                    keep_ratio=True,
                    size_hint=(0.7, 0.7),
                    pos_hint={"center_x": 0.5, "center_y": 0.5}
                )

                home_button = RoundedButton( #user can tap to go to the next screen
                    # text = "Home",
                    font_name= "RiosarkRegular-ZpgLB.otf",
                    font_size= "16sp",
                    background_color=(0.30, 0.30, 0.30, 0.75),
                    size_hint=(1, 1),
                    pos_hint={"left": 1, "y": 0},
                    on_press=lambda x: setattr(self.manager, 'current', 'AstroDashboard'),
                )
                home_container.add_widget(home_button)
                home_container.add_widget(homeimage)
                vert_layout.add_widget(home_container)

                # main_layout.add_widget(vert_layout)

                if data.get("media_type") == "image": # Display image (if it's an image, not a video)
                    image = AsyncImage(
                        source=data["url"],
                        fit_mode="scale-down",
                        size_hint=(1,1),
                        allow_stretch=True
                    )

                    image_container = BoxLayout(size_hint_x=0.7)  # 70% of width
                    image_container.add_widget(image)
                    main_layout.add_widget(vert_layout)
                    main_layout.add_widget(image_container)

                    # main_layout.add_widget(image)
                else:
                    main_layout.add_widget(Label(text="Video content not supported.", font_size='20sp'))

                self.add_widget(main_layout)

            except Exception as e: #catch any errors
                self.clear_widgets()
                self.add_widget(Label(text=f"Failed to load APOD: {e}"))

class AstroDashboard(Screen): #Main clockface screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Get base directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(BASE_DIR, "astronomy_events_2025.json") #use json path for the input file so python looks at the correct directory

        # Load and filter events
        with open(json_path, "r") as file:
            events = json.load(file)
        today = datetime.today().date()

        upcoming = [ #get upcoming events 
            e for e in events
            if datetime.strptime(e["date"], "%m-%d-%Y").date() >= today
        ]


        for e in upcoming: # Add next 8 events to event_list (referenced by id)
            layout = BoxLayout(orientation='horizontal')
            
            label_container = BoxLayout(
                orientation= "vertical",
                size_hint= (1,None),
                padding=5,
                spacing=5
            )
            date = Label(
                text=f"[u]{e['date']}:[/u]",
                markup= True,
                color=(0, 0.8, 1, 1),
                font_size='25sp',
                font_name="RiosarkRegular-ZpgLB.otf",
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=30,
                text_size=(self.width, None)  # Let width wrap naturally
            )
            event = Label(
                text=f"{e['event']}",
                # color=(0, 0, 0, 1),
                font_size='20sp',
                font_name="RiosarkRegular-ZpgLB.otf",
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=50,
                text_size=(self.width, None)
            )

            date.bind(size=lambda s, _: setattr(s, 'text_size', s.size))
            event.bind(size=lambda s, _: setattr(s, 'text_size', s.size))

            label_container.add_widget(date)
            label_container.add_widget(event)

            self.ids.event_list.add_widget(label_container)

        Clock.schedule_interval(self.update_time, 1) # Schedule clock update

    def update_time(self, dt):
        self.ids.time_label.text = datetime.now().strftime("%H:%M:%S")
        self.ids.date_label.text = datetime.now().strftime("%A,\n%B %d %Y")


    def on_enter(self):
        self.load_moon_data()

    def load_moon_data(self):
        print("Starting moon data request...")

        app_id = "151ed190-5ebf-4211-b472-5018955a9463"
        app_secret = "67489438a73c8dc6e256c6ce112920b232ad9a45e49e4dda186efee52daea0442c1c363731e743d2bc30756dd64f9b101cd71886c7cb777b139c34a6821f320408c97a5e789b70eb064180d47d710db302f25d9709f2028e285c29221d9ad1fcbbe23617136dff0f7eef6f4717d2cd05"
        userpass = f"{app_id}:{app_secret}"
        auth_string = base64.b64encode(userpass.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        }

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M:%S")
        payload = {
            "format": "png",
            "style": {
                "moonStyle": "default",
                "backgroundStyle": "solid",
                "backgroundColor": "black",
                "headingColor": "black",
                "textColor": "black"
            },
            "observer": {
                "latitude": 38.6274,
                "longitude": -90.1982,
                "date": today
            },
            "view": {
                "type": "landscape-simple"
            }
        }

        try:
            self.ids.moonimage.clear_widgets()
            self.ids.moonphase.clear_widgets()

            response = requests.post(
                "https://api.astronomyapi.com/api/v2/studio/moon-phase",
                headers=headers,
                data=json.dumps(payload)
            )

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            data = response.json()
            image_url = data['data']['imageUrl']  # this will crash if 'data' doesn't exist
            print("Moon Image URL:", image_url)

            conn = http.client.HTTPSConnection("api.astronomyapi.com")
            conn.request("GET", f"/api/v2/bodies/positions?longitude=-90.20&latitude=38.63&elevation=1&from_date={today}&to_date={today}&time={now}", headers=headers)

            res = conn.getresponse() #use http client
            raw_data = res.read()
            data = json.loads(raw_data) #decode json data
            #grab moon phase string
            moon = data["data"]["table"]["rows"][1]["cells"][0]["extraInfo"]["phase"]["string"]
            print("Moon Phase:", moon) 


            response = requests.get(image_url) #fetch moon image from api

            img = Image.open(BytesIO(response.content))
            # Manually out everything besides the moon (x0, y0, x1, y1)
            cropped = img.crop((15,45, 110, 142))
            cropped.save("moon_only.png")

            moon_image = AsyncImage( #insert image in kivy
                source="moon_only.png",
                fit_mode="scale-down",
                size_hint=(1, 1),
                allow_stretch=True
            )
            self.ids.moonimage.add_widget(moon_image)

            formatted_moon = moon.replace(" ", "\n")
            
            moonlabel = Label(
                text= f"[u][color=#00BDF6]Moon Phase:[/color][/u]\n\n{formatted_moon}",
                valign="top",
                halign= "center",
                font_size= '24sp',
                font_name= "RiosarkRegular-ZpgLB.otf",
                size_hint_y= 1,
                markup = True
            )
            self.ids.moonphase.add_widget(moonlabel)

        except Exception as e:
            print("Error fetching moon data:", e)


class OptionsWindow(Screen):
    pass

class AlarmsWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.alarms_list = []
        self.last_alarm_time = 0
        self.alarm_switches = {}
            
        Clock.schedule_interval(self.update_time, 1) # Schedule clock update
        Clock.schedule_interval(self.check_for_alarm, 1) #schedule alarm checker

    def update_time(self, dt):
        self.ids.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def update_alarm_label(self, *args):
        hour = int(self.ids.hourslider.value)
        minute = int(self.ids.minuteslider.value)
        if minute < 10 and hour < 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{fixed_hour}:{fixed_minute}"
        elif minute >= 10 and hour < 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{fixed_hour}:{minute}"
        elif minute < 10 and hour >= 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{hour}:{fixed_minute}"
        else:
            time_str = f"{hour}:{minute}"
        self.ids.alarm_label.text = f"Alarm Time: {time_str}"

    def save_alarm_time(self, *args):
        hour = int(self.ids.hourslider.value)
        minute = int(self.ids.minuteslider.value)
        if minute < 10 and hour < 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{fixed_hour}:{fixed_minute}"
        elif minute >= 10 and hour < 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{fixed_hour}:{minute}"
        elif minute < 10 and hour >= 10:
            fixed_minute = "0" + str(minute)
            fixed_hour = "0" + str(hour)
            time_str = f"{hour}:{fixed_minute}"
        else:
            time_str = f"{hour}:{minute}"

        self.alarms_list.append(time_str)
        print("List of alarm times:")
        print(self.alarms_list)

        now = time()
        if now - self.last_alarm_time < 0.5:
            return
        self.last_alarm_time = now
        
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=75,
            spacing=10,
            padding=5
        )

        alarm_label = Label(
            text= time_str,
            text_size= (350,None),
            font_size='40sp',
            font_name= "RiosarkRegular-ZpgLB.otf",
            halign= "center",
            pos_hint= {"y": -0.25},
            size_hint_x= 0.4,
            size_hint_y=None,
            height= 100,
            padding= 5
        )
        
        alarm_switch = Switch(
            active= True,
            size_hint_x=0.4,
            on_active= lambda instance, value: self.switch_click(instance, value, time_str)
        )

        self.alarm_switches[time_str] = alarm_switch #add active switch to alarm_switches dict

        delete_button = Button(
            size_hint_x = 0.125,
            size_hint_y = 0.7,
            pos_hint= {"y": 0.2},
            background_color=(1, 0, 0, 1),
            text= "X",
            font_size= "24sp",
            font_name= "RiosarkRegular-ZpgLB.otf",
            on_press = lambda instance: self.delete_alarm_time(layout, time_str) #have to use lambda isntancei in main.py as this function will be called immediately without it
        )

        layout.add_widget(alarm_label)
        layout.add_widget(alarm_switch)
        layout.add_widget(delete_button)

        self.ids.alarm_list.add_widget(layout)

    
    def check_for_alarm(self, dt):
        # actual alarm logic

        current_time = datetime.now().strftime("%H:%M")
        if current_time in self.alarms_list:
            switch = self.alarm_switches.get(current_time) #get kivy switch object from dict
            if switch and switch.active: #if there is a valid witch and it is active
                #trigger alarm
                print(f"Alarm ringing for time: {current_time}")
                self.manager.current = 'AlarmRingingWindow'
                self.alarms_list.remove(current_time) #immediately remove alarm time from list after ringing
            else:
                pass


    def delete_alarm_time(self, layout, time_str):
        if time_str in self.alarms_list:
            self.alarms_list.remove(time_str)
        self.ids.alarm_list.remove_widget(layout)
    
    def switch_click(self, switchObject, switchValue, time_str):
        print(f"Switch toggled for {time_str}: {'ON' if switchValue else 'OFF'}")



class AlarmRingingWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
            
        Clock.schedule_interval(self.update_time, 1) # Schedule clock update

    def update_time(self, dt):
        self.ids.clocklabel.text = datetime.now().strftime("%H:%M:%S")




class RoundedButton(Button):
    radius = ListProperty([20])
    normal_color = ListProperty([0.17, 0.17, 0.17, 0.75])
    down_color = ListProperty([0, 0.5, 0.6, 0.75])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # Fully transparent background

        with self.canvas.before:
            self.bg_color = Color(*self.normal_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

        self.bind(pos=self.update_rect, size=self.update_rect, state=self.update_color)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def update_color(self, *args):
        if self.state == 'down':
            self.bg_color.rgba = self.down_color
        else:
            self.bg_color.rgba = self.normal_color




class AstroApp(App): #App class
    def build(self):
        sm = ScreenManager() #define different screens
        sm.add_widget(ApodWindow(name="ApodWindow"))
        sm.add_widget(AstroDashboard(name="AstroDashboard"))
        sm.add_widget(OptionsWindow(name="OptionsWindow"))
        sm.add_widget(AlarmsWindow(name="AlarmsWindow"))
        sm.add_widget(AlarmRingingWindow(name="AlarmRingingWindow"))
        sm.current = "AstroDashboard"
        return sm

if __name__ == '__main__':
    AstroApp().run()
