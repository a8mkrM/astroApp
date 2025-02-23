import math
import datetime, calendar, os
import pytz
import numpy as np
import matplotlib.pyplot as plt
import random

import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import (Color, Ellipse, Line, StencilPush, StencilUse,
                           StencilUnUse, StencilPop, Rectangle, RoundedRectangle)
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout

from kivy.config import ConfigParser
from kivy.uix.spinner import SpinnerOption
from kivy.uix.dropdown import DropDown
# -------------------------------------------------------------------
Window.size = (360, 640)

LabelBase.register(name="Roboto", fn_regular="fonts/Amiri-Regular.ttf")

IMAGE_FOLDER = "images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# skyfield
from skyfield.api import load, Topos
from skyfield import almanac

try:
    eph = load('de430.bsp')
    print("Using de430.bsp for ephemeris data.")
except Exception as e:
    print("de430.bsp not available, using de421.bsp. Error:", e)
    eph = load('de421.bsp')

ts = load.timescale()


OMAN_LOCATIONS = {
    "إبراء": ("22.6917 N", "58.5417 E"), "أدم": ("22.2000 N", "57.5200 E"), "ازكي": ("22.8600 N", "57.7700 E"), "البريمي": ("24.2594 N", "55.7828 E"), "بدبد": ("23.4800 N", "58.0700 E"), "بدية": ("22.4167 N", "58.8333 E"), "بخا": ("26.0400 N", "56.2800 E"), "بركاء": ("23.7100 N", "57.8800 E"), "بهلا": ("22.9700 N", "57.3000 E"), "بوشر": ("23.5930 N", "58.4550 E"), "جعلان بني بو حسن": ("22.1300 N", "59.2000 E"), "جعلان بني بو علي": ("22.0833 N", "59.3333 E"), "جدة": ("21.5433 N", "39.1728 E"), "دبا": ("25.6100 N", "56.2600 E"), "دماء والطائيين": ("23.1667 N", "58.7500 E"), "ضنك": ("23.3800 N", "56.3300 E"), "ضلكوت": ("16.7100 N", "53.2900 E"), "الدقم": ("19.6488 N", "57.7083 E"), "رخيوت": ("16.8900 N", "53.8100 E"), "الرستاق": ("23.3938 N", "57.4258 E"), "الرياض": ("24.7136 N", "46.6753 E"), "سمائل": ("23.3300 N", "58.0000 E"), "السويق": ("23.8300 N", "57.4400 E"), "السنينة": ("23.9700 N", "56.1200 E"), "السيب": ("23.6840 N", "58.2160 E"), "شليم وجزر الحلانيات": ("17.4833 N", "56.0333 E"), "شناص": ("24.9600 N", "56.4500 E"), "صحار": ("24.3419 N", "56.7414 E"), "صحم": ("24.1600 N", "56.8800 E"), "صلالة": ("17.0199 N", "54.0890 E"), "صور": ("22.5667 N", "59.5333 E"), "طاقة": ("17.0400 N", "54.4100 E"), "عبري": ("23.2386 N", "56.5167 E"), "العامرات": ("23.4670 N", "58.6460 E"), "العوابي": ("23.2300 N", "57.6900 E"), "القابل": ("22.5000 N", "58.5000 E"), "قريات": ("23.2500 N", "58.9170 E"), "الكامل والوافي": ("22.3300 N", "59.2000 E"), "الخابورة": ("23.9500 N", "57.0800 E"), "خصب": ("26.2444 N", "56.2514 E"), "لوى": ("24.6800 N", "56.6300 E"), "مرباط": ("17.0100 N", "54.7000 E"), "مصيرة": ("20.5833 N", "58.8833 E"), "المصنعة": ("23.7700 N", "57.6700 E"), "مطرح": ("23.6150 N", "58.5670 E"), "مكة": ("21.4225 N", "39.8262 E"), "مقشن": ("18.1000 N", "54.0000 E"), "محضة": ("24.5100 N", "56.0300 E"), "محوت": ("20.3708 N", "58.0061 E"), "مدحاء": ("25.3217 N", "56.3400 E"), "مسقط": ("23.5859 N", "58.4059 E"), "المضيبي": ("22.4500 N", "58.0667 E"), "منح": ("22.9800 N", "57.6500 E"), "المزيونة": ("17.7000 N", "53.8000 E"), "نزوى": ("22.9342 N", "57.5338 E"), "نخل": ("23.3900 N", "57.8200 E"), "هيماء": ("19.2667 N", "56.3667 E"), "وادي بني خالد": ("22.5667 N", "59.0833 E"), "وادي المعاول": ("23.4700 N", "57.8300 E"), "ينقل": ("23.5100 N", "56.5500 E"), "ثمريت": ("17.6000 N", "54.0167 E"), "سدح": ("16.967 N", "55.033 E"), "الجازر": ("19.0800 N", "57.7300 E"), "الحمراء": ("23.1500 N", "57.2800 E")
}

def process_text(text):
    return get_display(arabic_reshaper.reshape(text))

def reshape_text(text):
    return get_display(arabic_reshaper.reshape(text))

def apply_refraction_correction(alt_deg):
    if alt_deg < -1:
        return alt_deg
    R = 1.02 / math.tan(math.radians(alt_deg + 10.3/(alt_deg + 5.11)))
    R_deg = R / 60.0
    return alt_deg + R_deg

def get_current_location():
    app = App.get_running_app()
    location_name = getattr(app, "current_location_name", "مسقط")
    lat_str, lon_str = OMAN_LOCATIONS.get(location_name, OMAN_LOCATIONS["مسقط"])
    return Topos(lat_str, lon_str)

def get_rise_set(ts, dt, body, include_date=False):
    """
    تحسب أوقات الشروق والغروب بحيث:
      - يُستخرج شروق ضمن نافذة 13 ساعة من dt.
      - يُستخرج غروب يكون بعد الشروق.
        إذا كان الحدث المُرشَّح للغروب وقع قبل الشروق أو بفارق كبير (مثلاً أكثر من 3 ساعات) يتم اختيار الحدث التالي.
    تُنسَّق النتائج مع استبدال AM بـ"ص" وPM بـ"م".
    """
    utc_tz = pytz.UTC
    oman_tz = pytz.timezone('Asia/Muscat')
    location = get_current_location()
    dt_local = dt.astimezone(oman_tz)

    dt_start = (dt - datetime.timedelta(hours=24)).astimezone(utc_tz)
    dt_end = (dt + datetime.timedelta(hours=24)).astimezone(utc_tz)
    t0 = ts.from_datetime(dt_start)
    t1 = ts.from_datetime(dt_end)
    
    f = almanac.risings_and_settings(eph, body, location)
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise_events = []
    sunset_events = []
    for t_val, e_val in zip(times, events):
        local_time = t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz)
        diff_sec = abs((local_time - dt_local).total_seconds())
        if e_val == 1 and diff_sec <= 13 * 3600:
            sunrise_events.append(local_time)
        elif e_val == 0 and diff_sec <= 12 * 3600:
            sunset_events.append(local_time)
    
    if sunrise_events:
        sunrise_time = min(sunrise_events, key=lambda t: abs((t - dt_local).total_seconds()))
    else:
        all_rising = [t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz)
                      for t_val, e_val in zip(times, events) if e_val == 1]
        sunrise_time = min(all_rising, key=lambda t: abs((t - dt_local).total_seconds())) if all_rising else None

    if sunrise_time:
        valid_sunset = [t for t in sunset_events if t > sunrise_time]
        if valid_sunset:
            future_sunset = [t for t in valid_sunset if t >= dt_local]
            if future_sunset:
                sunset_time = min(future_sunset, key=lambda t: (t - dt_local).total_seconds())
            else:
                sunset_time = min(valid_sunset, key=lambda t: abs((t - dt_local).total_seconds()))
        else:
            all_setting = [t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz)
                           for t_val, e_val in zip(times, events) if e_val == 0]
            sunset_time = min(all_setting, key=lambda t: abs((t - dt_local).total_seconds())) if all_setting else None
    else:
        all_setting = [t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz)
                       for t_val, e_val in zip(times, events) if e_val == 0]
        sunset_time = min(all_setting, key=lambda t: abs((t - dt_local).total_seconds())) if all_setting else None

    if sunrise_time and sunset_time:
        if (sunset_time - sunrise_time).total_seconds() < 3 * 3600:
            all_setting = [t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz)
                           for t_val, e_val in zip(times, events) if e_val == 0 and t_val.utc_datetime().replace(tzinfo=utc_tz).astimezone(oman_tz) > sunrise_time]
            if all_setting:
                sunset_time = min(all_setting, key=lambda t: abs((t - dt_local).total_seconds()))
    
    fmt = "%d/%m/%Y %I:%M %p" if include_date else "%I:%M %p"
    
    if sunrise_time:
        if include_date and sunrise_time.hour == 0:
            sunrise_str = (sunrise_time + datetime.timedelta(days=1)).strftime(fmt)
        else:
            sunrise_str = sunrise_time.strftime(fmt)
    else:
        sunrise_str = dt_local.strftime(fmt)
    
    if sunset_time:
        if include_date and sunset_time.hour == 0:
            sunset_str = (sunset_time + datetime.timedelta(days=1)).strftime(fmt)
        else:
            sunset_str = sunset_time.strftime(fmt)
    else:
        sunset_str = dt_local.strftime(fmt)
    
    sunrise_str = sunrise_str.replace("AM", "ص").replace("PM", "م")
    sunset_str = sunset_str.replace("AM", "ص").replace("PM", "م")
    
    return sunrise_str, sunset_str

def hex_to_rgba(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (r, g, b, alpha)

def calc_inner(outer_diameter, semi_phase):
    abs_phase = abs(semi_phase)
    n = (1 - abs_phase) * outer_diameter / 2 or 0.01
    inner_radius = n/2 + (outer_diameter * outer_diameter) / (8 * n)
    d = inner_radius * 2
    if semi_phase > 0:
        o = outer_diameter/2 - n
    else:
        o = -2 * inner_radius + outer_diameter/2 + n
    return d, o

def get_moon_phase_name(phase_angle, is_waxing):
    if phase_angle < 10 or phase_angle > 350:
        return "New Moon"
    elif 10 <= phase_angle < 80:
        return "Waxing Crescent" if is_waxing else "Waning Crescent"
    elif 80 <= phase_angle < 100:
        return "First Quarter" if is_waxing else "Last Quarter"
    elif 100 <= phase_angle < 170:
        return "Waxing Gibbous" if is_waxing else "Waning Gibbous"
    elif 170 <= phase_angle < 190:
        return "Full Moon"
    elif 190 <= phase_angle < 260:
        return "Waning Gibbous" if is_waxing else "Waxing Gibbous"
    elif 260 <= phase_angle < 280:
        return "Last Quarter" if is_waxing else "First Quarter"
    elif 280 <= phase_angle <= 350:
        return "Waning Crescent" if is_waxing else "Waxing Crescent"
    return "Unknown"

default_config = {
    'shadow_colour': hex_to_rgba("#333333"),
    'light_colour': hex_to_rgba("#6f456e"),
    'diameter': 150,
    'earthshine': 0.1,
    'blur': 2,
}

# -------------------------------------------------------------------
# ودجت رسم القمر
class MoonPhaseWidget(Widget):
    phase = NumericProperty(0.0)      
    is_waxing = BooleanProperty(True) 
    config = ObjectProperty(default_config)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            side = min(self.width, self.height)
            square_x = self.center_x - side/2
            square_y = self.center_y - side/2

            Color(1, 1, 1, 1)
            Line(rectangle=(square_x, square_y, side, side), width=2)

            margin = 10
            diameter = side - margin
            outer_pos = (square_x + margin/2, square_y + margin/2)

            phase_value = self.phase
            if phase_value < 0.5:
                outer_colour = self.config.get('light_colour', default_config['light_colour'])
                inner_colour = self.config.get('shadow_colour', default_config['shadow_colour'])
                phase_adj = -phase_value if self.is_waxing else phase_value
            else:
                outer_colour = self.config.get('shadow_colour', default_config['shadow_colour'])
                inner_colour = self.config.get('light_colour', default_config['light_colour'])
                phase_adj = 1 - phase_value
                if not self.is_waxing:
                    phase_adj = -phase_adj

            semi_phase = phase_adj * 2
            inner_diameter, inner_offset = calc_inner(diameter, semi_phase)

            Color(*outer_colour)
            Ellipse(pos=outer_pos, size=(diameter, diameter))

            StencilPush()
            Ellipse(pos=outer_pos, size=(diameter, diameter))
            StencilUse()
            inner_x = outer_pos[0] + inner_offset
            inner_y = self.center_y - inner_diameter/2
            Color(*inner_colour)
            Ellipse(pos=(inner_x, inner_y), size=(inner_diameter, inner_diameter))
            StencilUnUse()
            StencilPop()

            Color(0, 0, 0, 1)
            Line(circle=(self.center_x, self.center_y, diameter/2), width=1)

    def on_size(self, *args):
        self.update_canvas()

    def on_phase(self, *args):
        self.update_canvas()

    def on_is_waxing(self, *args):
        self.update_canvas()

# -------------------------------------------------------------------
# صندوق معلومات القمر
class MoonContent(BoxLayout):
    def __init__(self, dt, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 5
        self.size_hint_y = None
        self.height = 400
        self.padding = [0, 10, 0, 10]
        
        self.moon_widget = MoonPhaseWidget(size_hint=(1, 0.8))
        self.add_widget(self.moon_widget)
        
        self.info_label = Label(
            text="",
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            size_hint_y=None,
            halign='center', valign='middle'
        )
        self.info_label.bind(width=lambda inst, value: setattr(inst, 'text_size', (value, None)))
        self.info_label.bind(texture_size=lambda inst, value: setattr(inst, 'height', value[1]))
        self.add_widget(self.info_label)
        
        self.update_content(dt)

    def update_content(self, dt):
        oman_tz = pytz.timezone('Asia/Muscat')
        dt_local = dt if dt.tzinfo else oman_tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.UTC)
        t = ts.from_datetime(dt_utc)
        
        illumination = float(almanac.fraction_illuminated(eph, "moon", t))
        phase_angle = almanac.moon_phase(eph, t).degrees
        waxing = True if phase_angle < 180 else False
        self.moon_widget.phase = illumination
        self.moon_widget.is_waxing = waxing

        phase_name = get_moon_phase_name(phase_angle, waxing)
        phase_ar_map = {
            "New Moon": "قمر جديد",
            "Waxing Crescent": "الهلال متزايد",
            "First Quarter": "التربيع الأول",
            "Waxing Gibbous": "الأحدب المتزايد",
            "Full Moon": "البدر",
            "Waning Gibbous": "أحدب متناقص",
            "Last Quarter": "التربيع الأخير",
            "Waning Crescent": "الهلال المتناقص",
            "Unknown": "غير معروف"
        }
        phase_name_ar = phase_ar_map.get(phase_name, phase_name)

        location = get_current_location()
        observer = eph['earth'] + location
        moon = eph["moon"]
        astrometric = observer.at(t).observe(moon).apparent()
        alt, az, _ = astrometric.altaz()
        alt_deg = alt.degrees
        az_deg = az.degrees

        rise_str, set_str = get_rise_set(ts, dt, moon, include_date=True)
        rise_str = rise_str.replace("AM", "ص").replace("PM", "م")
        set_str = set_str.replace("AM", "ص").replace("PM", "م")
        
        info_text = (
            f"الطور: {phase_name_ar}\n"
            f"الشروق: {rise_str}\nالغروب: {set_str}\n"
            f"الارتفاع: {alt_deg:.2f}°\nالسمت: {az_deg:.2f}°\n"
            f"نسبة الإضاءة: {illumination*100:.1f}%"
        )
        self.info_label.text = process_text(info_text)

# -------------------------------------------------------------------
# عنصر الكوكب (صورة + معلومات)
class PlanetItem(BoxLayout):
    def __init__(self, image_path, arabic_name, rise_str, set_str, altitude, azimuth, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 2
        self.spacing = 5
        self.size_hint_y = None
        self.height = 200
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        rise_str = rise_str.replace("AM", "ص").replace("PM", "م")
        set_str = set_str.replace("AM", "ص").replace("PM", "م")
        
        top_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=40)
        top_box.add_widget(Widget(size_hint_x=1))
        name_label = Label(
            text=process_text(arabic_name),
            font_size='16sp',
            halign='left', valign='middle'
        )
        name_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        top_box.add_widget(name_label)
        img = Image(source=image_path, size_hint_x=None, width=30)
        top_box.add_widget(img)
        top_box.add_widget(Widget(size_hint_x=1))
        self.add_widget(top_box)
        
        ss_label = Label(
            text=process_text(f"الشروق: {rise_str}\nالغروب: {set_str}" ),
            font_size='14sp', halign='center', valign='middle'
        )
        ss_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self.add_widget(ss_label)
        
        aa_label = Label(
            text=process_text(f"الارتفاع: {altitude:.2f}°\nالسمت: {azimuth:.2f}°"),
            font_size='14sp', halign='center', valign='middle'
        )
        aa_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self.add_widget(aa_label)
        
    def update_rect(self, *args):
        self.rect.rectangle = (self.x + 5, self.y, self.width - 10, self.height)

class PlanetsContent(BoxLayout):
    def __init__(self, dt, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 5
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.update_content(dt)

    def update_content(self, dt):
        self.clear_widgets()
        oman_tz = pytz.timezone('Asia/Muscat')
        dt_local = dt if dt.tzinfo else oman_tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.UTC)
        t = ts.from_datetime(dt_utc)

        location = get_current_location()
        observer = eph['earth'] + location

        planets = {
            'venus': 'الزهرة',
            'mercury': 'عطارد',
            'JUPITER BARYCENTER': 'المشتري',
            'mars': 'المريخ',
            'Uranus BARYCENTER': 'أورانوس',
            'SATURN BARYCENTER': 'زحل',
            'Neptune BARYCENTER': 'نبتون'
        }
        image_map = {
            'mercury': 'planetimg/mercury.png',
            'venus': 'planetimg/venus.png',
            'mars': 'planetimg/mars.png',
            'JUPITER BARYCENTER': 'planetimg/jupiter.png',
            'SATURN BARYCENTER': 'planetimg/saturn.png',
            'Uranus BARYCENTER': 'planetimg/uranus.png',
            'Neptune BARYCENTER': 'planetimg/neptune.png'
        }

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for key, arabic_name in planets.items():
            planet = eph[key]
            astrometric = observer.at(t).observe(planet).apparent()
            alt, az, _ = astrometric.altaz()
            alt_corrected = apply_refraction_correction(alt.degrees)
            rise_str, set_str = get_rise_set(ts, dt, planet)
            image_path = image_map.get(key, '')
            item = PlanetItem(
                image_path=image_path,
                arabic_name=arabic_name,
                rise_str=rise_str,
                set_str=set_str,
                altitude=alt_corrected,
                azimuth=az.degrees
            )
            grid.add_widget(item)
        self.add_widget(grid)

# -------------------------------------------------------------------
# خريطة السماء
class MapContent(BoxLayout):
    def __init__(self, dt, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.size_hint_y = None
        self.height = 400
        self.update_content(dt)

    def update_content(self, dt):
        try:
            oman_tz = pytz.timezone('Asia/Muscat')
            dt_local = dt if dt.tzinfo else oman_tz.localize(dt)
            dt_utc = dt_local.astimezone(pytz.UTC)
            t = ts.from_datetime(dt_utc)
            location = get_current_location()
            observer = eph['earth'] + location

            bodies = {
                "الشمس": "sun",
                "القمر": "moon",
                "عطارد": "mercury",
                "الزهرة": "venus",
                "المريخ": "mars",
                "المشتري": "JUPITER BARYCENTER",
                "زحل": "SATURN BARYCENTER"
            }
            results = []
            for name, key in bodies.items():
                try:
                    body = eph[key]
                except Exception:
                    continue
                astrometric = observer.at(t).observe(body).apparent()
                alt, az, _ = astrometric.altaz()
                results.append({"name": name, "alt": alt.degrees, "az": az.degrees})

            planet_colors = {
                "الشمس":    "#FDB813",
                "القمر":    "#CCCCCC",
                "عطارد":   "#B1B1B1",
                "الزهرة":  "#F7D358",
                "المريخ":  "#FF4500",
                "المشتري": "#FFA500",
                "زحل":     "#D2B48C"
            }

            fig, ax = plt.subplots(figsize=(8, 8))
            bg_color = '#300544'
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)

            circle = plt.Circle((0, 0), 1, edgecolor='#ffffff', facecolor='#0c0842', lw=2)
            ax.add_artist(circle)

            directions = {"شمال": 0, "شرق": 90, "جنوب": 180, "غرب": 270}
            for dir_label, angle in directions.items():
                x = np.cos(np.radians(angle))
                y = np.sin(np.radians(angle))
                ax.text(x * 1.2, y * 1.2, reshape_text(dir_label),
                        ha='center', va='center', fontsize=12, color='white')

            for angle in range(0, 360, 30):
                x = np.cos(np.radians(angle)) * 1.05
                y = np.sin(np.radians(angle)) * 1.05
                ax.text(x, y, f"{angle}°", ha='center', va='center', fontsize=8, color='white')

            for r in results:
                if r["alt"] < 0:
                    continue
                r_coord = 1 - r["alt"] / 90.0
                x = np.cos(np.radians(r["az"])) * r_coord
                y = np.sin(np.radians(r["az"])) * r_coord
                color = planet_colors.get(r["name"], "white")
                ax.plot(x, y, 'o', color=color, markersize=8)
                ax.text(x, y + 0.05, reshape_text(r["name"]), fontsize=10,
                        color='white', ha='left', va='bottom')

            ax.set_aspect('equal')
            ax.axis('off')

            for file in os.listdir(IMAGE_FOLDER):
                file_path = os.path.join(IMAGE_FOLDER, file)
                if os.path.isfile(file_path) and file.startswith("sky_map") and file.endswith('.png'):
                    os.remove(file_path)

            timestamp = int(datetime.datetime.now().timestamp())
            image_path = os.path.join(IMAGE_FOLDER, f"sky_map_{timestamp}.png")
            plt.savefig(image_path, bbox_inches='tight', dpi=150)
            plt.close()

            self.clear_widgets()
            img_widget = Image(source=image_path, allow_stretch=True, keep_ratio=True)
            self.add_widget(img_widget)
        except Exception as e:
            self.clear_widgets()
            error_label = Label(
                text=process_text("حدث خطأ أثناء رسم الخريطة"),
                font_size='16sp',
                color=(1, 0, 0, 1)
            )
            self.add_widget(error_label)

# -------------------------------------------------------------------
# ValueAdjuster - لضبط الأرقام
class ValueAdjuster(BoxLayout):
    def __init__(self, initial_value, min_value, max_value,
                 on_value_change=None,
                 rollover=False,
                 on_rollover=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.width = 60
        self.height = 70

        self.current_value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.on_value_change = on_value_change
        self.rollover = rollover
        self.on_rollover = on_rollover

        self.up_button = Button(
            size_hint=(1, None),
            size=(20, 20),
            background_normal='planetimg/up-arrow.png',
            background_down='planetimg/up-arrow.png',
            border=(0, 0, 0, 0)
        )
        self.up_button.bind(on_release=self.increment)
        self.add_widget(self.up_button)
        font_size_value = 20
        widget_height = 40
        vertical_padding = (widget_height - font_size_value) / 2

        self.value_label = Label(
            text=process_text(str(self.current_value)),
            font_size='18sp',
            size_hint=(1, None),
            height=40,
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.value_label.bind(size=lambda inst, value: setattr(inst, 'text_size', value))
        self.value_label.bind(on_text_validate=self.on_text_validate)
        self.add_widget(self.value_label)

        self.down_button = Button(
            size_hint=(1, None),
            size=(20, 20),
            background_normal='planetimg/down-arrow.png',
            background_down='planetimg/down-arrow.png',
            border=(0, 0, 0, 0)
        )
        self.down_button.bind(on_release=self.decrement)
        self.add_widget(self.down_button)

    def update_display(self):
        self.value_label.text = str(self.current_value)

    def on_text_validate(self, instance):
        self.validate_and_update(instance.text)

    def validate_and_update(self, text):
        try:
            value = int(text)
        except ValueError:
            self.value_label.text = str(self.current_value)
            return
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        self.current_value = value
        self.update_display()
        if self.on_value_change:
            self.on_value_change(self.current_value)

    def increment(self, instance):
        if self.current_value >= self.max_value:
            if self.rollover:
                self.current_value = self.min_value
                if self.on_rollover:
                    self.on_rollover('increment')
            else:
                self.current_value = self.max_value
        else:
            self.current_value += 1
        self.update_display()
        if self.on_value_change:
            self.on_value_change(self.current_value)

    def decrement(self, instance):
        if self.current_value <= self.min_value:
            if self.rollover:
                self.current_value = self.max_value
                if self.on_rollover:
                    self.on_rollover('decrement')
            else:
                self.current_value = self.min_value
        else:
            self.current_value -= 1
        self.update_display()
        if self.on_value_change:
            self.on_value_change(self.current_value)

# -------------------------------------------------------------------
# زر اختيار الفترة (ص/م)
class PeriodAdjuster(BoxLayout):
    def __init__(self, initial_period="ص", on_value_change=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.width = 60
        self.height = 70

        self.current_period = initial_period
        self.on_value_change = on_value_change

        self.up_button = Button(
            size_hint=(1, None),
            size=(20, 20),
            background_normal='planetimg/up-arrow.png',
            background_down='planetimg/up-arrow.png',
            border=(0, 0, 0, 0)
        )
        self.up_button.bind(on_release=self.toggle)
        self.add_widget(self.up_button)

        self.value_label = Label(
            text=process_text(self.current_period),
            font_size='18sp',
            size_hint=(1, None),
            height=40,
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.value_label.bind(size=lambda inst, value: setattr(inst, 'text_size', value))
        self.add_widget(self.value_label)

        self.down_button = Button(
            size_hint=(1, None),
            size=(20, 20),
            background_normal='planetimg/down-arrow.png',
            background_down='planetimg/down-arrow.png',
            border=(0, 0, 0, 0)
        )
        self.down_button.bind(on_release=self.toggle)
        self.add_widget(self.down_button)

    def toggle(self, instance):
        self.current_period = "م" if self.current_period == "ص" else "ص"
        self.value_label.text = process_text(self.current_period)
        if self.on_value_change:
            self.on_value_change(self.current_period)

# -------------------------------------------------------------------
# مجموعة التاريخ (سنة/شهر/يوم)
class DateAdjusterGroup(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = 0

        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        today = datetime.date.today()
        self.current_date = today
        max_day = calendar.monthrange(today.year, today.month)[1]

        self.year_adjuster = ValueAdjuster(
            today.year, 1900, 2100,
            on_value_change=self.on_year_change
        )
        self.month_adjuster = ValueAdjuster(
            today.month, 1, 12,
            on_value_change=self.on_month_change,
            rollover=True,
            on_rollover=self.month_rollover
        )
        self.day_adjuster = ValueAdjuster(
            today.day, 1, max_day,
            on_value_change=self.on_day_change,
            rollover=True,
            on_rollover=self.day_rollover
        )
        self.year_adjuster.value_label.foreground_color = (1, 1, 1, 1)
        self.month_adjuster.value_label.foreground_color = (1, 1, 1, 1)
        self.day_adjuster.value_label.foreground_color = (1, 1, 1, 1)
        self.year_adjuster.value_label.background_color = hex_to_rgba("#300544")
        self.month_adjuster.value_label.background_color = hex_to_rgba("#300544")
        self.day_adjuster.value_label.background_color = hex_to_rgba("#300544")

        self.add_widget(self.year_adjuster)
        self.add_widget(self.month_adjuster)
        self.add_widget(self.day_adjuster)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def day_rollover(self, direction):
        if direction == 'increment':
            new_month = self.month_adjuster.current_value + 1
            if new_month > 12:
                new_month = 1
                self.year_adjuster.current_value += 1
                self.year_adjuster.update_display()
            self.month_adjuster.current_value = new_month
            self.month_adjuster.update_display()
        elif direction == 'decrement':
            new_month = self.month_adjuster.current_value - 1
            if new_month < 1:
                new_month = 12
                self.year_adjuster.current_value -= 1
                self.year_adjuster.update_display()
            self.month_adjuster.current_value = new_month
            self.month_adjuster.update_display()

        max_day = calendar.monthrange(
            self.year_adjuster.current_value,
            self.month_adjuster.current_value
        )[1]
        self.day_adjuster.max_value = max_day

        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_day_change(self, new_day):
        max_day = calendar.monthrange(self.year_adjuster.current_value, self.month_adjuster.current_value)[1]
        if new_day > max_day:
            new_day = max_day
        self.current_date = datetime.date(
            self.year_adjuster.current_value,
            self.month_adjuster.current_value,
            new_day
        )
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def month_rollover(self, direction):
        if direction == 'increment':
            new_year = self.year_adjuster.current_value
            new_month = self.month_adjuster.current_value + 1
            if new_month > 12:
                new_month = 1
                new_year += 1
                self.year_adjuster.current_value = new_year
                self.year_adjuster.update_display()
            self.month_adjuster.current_value = new_month
            self.month_adjuster.update_display()
        elif direction == 'decrement':
            new_year = self.year_adjuster.current_value
            new_month = self.month_adjuster.current_value - 1
            if new_month < 1:
                new_month = 12
                new_year -= 1
                self.year_adjuster.current_value = new_year
                self.year_adjuster.update_display()
            self.month_adjuster.current_value = new_month
            self.month_adjuster.update_display()

        max_day = calendar.monthrange(
            self.year_adjuster.current_value,
            self.month_adjuster.current_value
        )[1]
        self.day_adjuster.max_value = max_day
        if self.day_adjuster.current_value > max_day:
            self.day_adjuster.current_value = max_day
            self.day_adjuster.update_display()

        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_month_change(self, new_month):
        max_day = calendar.monthrange(self.current_date.year, new_month)[1]
        new_day = min(self.current_date.day, max_day)
        self.current_date = datetime.date(
            self.current_date.year,
            new_month,
            new_day
        )
        self.day_adjuster.max_value = max_day
        self.day_adjuster.current_value = new_day
        self.day_adjuster.update_display()
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_year_change(self, new_year):
        max_day = calendar.monthrange(new_year, self.current_date.month)[1]
        new_day = min(self.current_date.day, max_day)
        self.current_date = datetime.date(
            new_year,
            self.current_date.month,
            new_day
        )
        self.day_adjuster.max_value = max_day
        self.day_adjuster.current_value = new_day
        self.day_adjuster.update_display()
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

# -------------------------------------------------------------------
# مجموعة الوقت (ص/م + دقائق + ساعة)
class TimeAdjusterGroup(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = 0

        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        now = datetime.datetime.now()
        hour_24 = now.hour
        if hour_24 == 0:
            hour_12 = 12
        elif hour_24 > 12:
            hour_12 = hour_24 - 12
        else:
            hour_12 = hour_24

        period = "م" if hour_24 >= 12 else "ص"

        self.prev_hour = hour_12
        self.period_adjuster = PeriodAdjuster(
            initial_period=period,
            on_value_change=self.on_period_change
        )
        self.minute_adjuster = ValueAdjuster(
            now.minute, 0, 59,
            on_value_change=self.on_minute_change,
            rollover=True,
            on_rollover=self.minute_rollover
        )
        self.hour_adjuster = ValueAdjuster(
            hour_12, 1, 12,
            on_value_change=self.on_hour_change,
            rollover=True,
            on_rollover=self.hour_rollover
        )
        self.period_adjuster.value_label.color = (1, 1, 1, 1)
        self.period_adjuster.value_label.background_color = hex_to_rgba("#300544")
        self.hour_adjuster.value_label.background_color = hex_to_rgba("#300544")
        self.hour_adjuster.value_label.foreground_color = (1, 1, 1, 1)
        self.minute_adjuster.value_label.background_color = hex_to_rgba("#300544")
        self.minute_adjuster.value_label.foreground_color = (1, 1, 1, 1)
        self.add_widget(self.period_adjuster)
        self.add_widget(self.hour_adjuster)
        self.add_widget(self.minute_adjuster)
   
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def minute_rollover(self, direction):
        if direction == 'increment':
            self.hour_adjuster.increment(None)
        elif direction == 'decrement':
            self.hour_adjuster.decrement(None)
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def hour_rollover(self, direction):
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_hour_change(self, new_hour):
        old_hour = self.prev_hour
        current_period = self.period_adjuster.current_period
        if old_hour == 11 and new_hour == 12:
            if current_period == "ص":
                self.period_adjuster.current_period = "م"
                self.period_adjuster.value_label.text = process_text("م")
            else:
                self.period_adjuster.current_period = "ص"
                self.period_adjuster.value_label.text = process_text("ص")
                self._adjust_parent_date('increment')
        elif old_hour == 12 and new_hour == 11:
            if current_period == "ص":
                self.period_adjuster.current_period = "م"
                self.period_adjuster.value_label.text = process_text("م")
                self._adjust_parent_date('decrement')
            else:
                self.period_adjuster.current_period = "ص"
                self.period_adjuster.value_label.text = process_text("ص")

        self.prev_hour = new_hour
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_minute_change(self, new_minute):
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def on_period_change(self, new_period):
        if self.parent and hasattr(self.parent, 'on_datetime_change'):
            self.parent.on_datetime_change()

    def _adjust_parent_date(self, direction):
        if self.parent and hasattr(self.parent, 'adjust_date_by_day'):
            self.parent.adjust_date_by_day(direction)

# -------------------------------------------------------------------
# Popup لاختيار الموقع



class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = hex_to_rgba("#55117e")
        self.color = (1, 1, 1, 1)

class CustomDropDown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # تحديد أقصى ارتفاع للقائمة، وعند تجاوزها يظهر شريط التمرير
        self.max_height = 300
class LocationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = process_text("اختر الموقع")
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        self.bind(on_dismiss=self.on_popup_dismiss)

        # تعيين خلفية النافذة باستخدام الخاصيتين background و background_color
        self.background = ''
        self.background_color = hex_to_rgba("#2b113a")
        with self.canvas.before:
            Color(*hex_to_rgba("#2b113a"))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.location_keys = list(OMAN_LOCATIONS.keys())
        self.location_texts = [process_text(k) for k in self.location_keys]

        content_box = BoxLayout(orientation="vertical", spacing=10, padding=20)
        
        # إنشاء Spinner مع تخصيص قائمة الخيارات باستخدام CustomSpinnerOption و CustomDropDown
        self.spinner = Spinner(
            text=process_text("اختر"),
            values=self.location_texts,
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            size_hint=(1, None),
            height=44,
            background_normal='',
            background_color=hex_to_rgba("#410a63"),
            color=(1, 1, 1, 1),
            option_cls=CustomSpinnerOption,
            dropdown_cls=CustomDropDown,
        )
        self.spinner.bind(text=self.on_select_location)
        content_box.add_widget(self.spinner)

        close_btn = Button(
            text=process_text("إغلاق"),
            size_hint=(1, None),
            height=44,
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            background_normal='',
            background_color=hex_to_rgba("#410a63"),
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_release=lambda x: self.dismiss())
        content_box.add_widget(close_btn)

        self.add_widget(content_box)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_open(self):
        self.spinner.unbind(text=self.on_select_location)
        app = App.get_running_app()
        current_location = getattr(app, "current_location_name", "مسقط")
        if current_location in self.location_keys:
            idx = self.location_keys.index(current_location)
            shaped_loc = self.location_texts[idx]
            self.spinner.text = shaped_loc
        else:
            self.spinner.text = process_text("اختر")
        self.spinner.bind(text=self.on_select_location)

    def on_select_location(self, spinner, shaped_text):
        if shaped_text == process_text("اختر"):
            return
        idx = self.location_texts.index(shaped_text)
        actual_location = self.location_keys[idx]
        app = App.get_running_app()
        app.current_location_name = actual_location
        app.save_location_preference()
        current_dt = (
            app.root.options_widget.dt_adjuster.get_datetime()
            if hasattr(app.root, 'options_widget')
            else datetime.datetime.now(pytz.timezone('Asia/Muscat'))
        )
        update_all_screens(current_dt)
        self.dismiss()

    def on_popup_dismiss(self, instance):
        app = App.get_running_app()
        if app.root and hasattr(app.root, 'update_current_content'):
            dt = app.root.options_widget.dt_adjuster.get_datetime()
            app.root.update_current_content(dt)


# -------------------------------------------------------------------
# أداة ضبط التاريخ والوقت مع زرين بجانب بعض: أيقونة "الوقت الحالي" + زر الموقع
class CombinedDateTimeAdjuster(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))  
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)        
        self.orientation = "horizontal"
        self.spacing = 5
        self.datetime_change_callback = None

        top_btns_box = BoxLayout(orientation="horizontal", size_hint=(None, None), height=70)
        top_btns_box.width = 100

        anchor = AnchorLayout(size_hint=(None, 1), width=50, anchor_y='center')
        if hasattr(self, 'location_button') and self.location_button.parent:
            self.location_button.parent.remove_widget(self.location_button)
        self.location_button = Button(
            size_hint=(None, None), size=(50, 50),
            background_normal='planetimg/location.png',
            background_down='planetimg/location.png',
            border=(0, 0, 0, 0)
        )
        self.location_button.bind(on_release=self.open_location_popup)
        anchor.add_widget(self.location_button)
        top_btns_box.add_widget(anchor)

        anchor_reset = AnchorLayout(size_hint=(None, 1), width=50, anchor_y='center')
        self.reset_button = Button(
            size_hint=(None, None),
            size=(50, 50),
            border=(0, 0, 0, 0),
            background_normal='planetimg/redo.png',
            background_down='planetimg/redo.png'
        )
        self.reset_button.bind(on_release=self.reset_to_now)
        anchor_reset.add_widget(self.reset_button)
        top_btns_box.add_widget(anchor_reset)

        self.add_widget(top_btns_box)

        self.date_group = DateAdjusterGroup()
        self.time_group = TimeAdjusterGroup()

        self.add_widget(self.date_group)
        self.add_widget(self.time_group)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def open_location_popup(self, instance):
        loc_popup = LocationPopup()
        loc_popup.open()

    def get_datetime(self):
        date_ = self.date_group.current_date
        hour_12 = self.time_group.hour_adjuster.current_value
        minute_ = self.time_group.minute_adjuster.current_value
        period = self.time_group.period_adjuster.current_period

        if period == "م":
            if hour_12 < 12:
                hour_12 += 12
        else:
            if hour_12 == 12:
                hour_12 = 0

        oman_tz = pytz.timezone('Asia/Muscat')
        return oman_tz.localize(datetime.datetime(date_.year, date_.month, date_.day, hour_12, minute_))

    def on_datetime_change(self):
        if self.datetime_change_callback:
            self.datetime_change_callback(self.get_datetime())

    def adjust_date_by_day(self, direction):
        current_date = self.date_group.current_date
        if direction == 'increment':
            new_date = current_date + datetime.timedelta(days=1)
        else:
            new_date = current_date - datetime.timedelta(days=1)

        self.date_group.current_date = new_date
        self.date_group.year_adjuster.current_value = new_date.year
        self.date_group.month_adjuster.current_value = new_date.month

        max_day = calendar.monthrange(new_date.year, new_date.month)[1]
        self.date_group.day_adjuster.max_value = max_day
        if new_date.day <= max_day:
            self.date_group.day_adjuster.current_value = new_date.day

        self.date_group.year_adjuster.update_display()
        self.date_group.month_adjuster.update_display()
        self.date_group.day_adjuster.update_display()

        self.on_datetime_change()

    def reset_to_now(self, instance):
        oman_tz = pytz.timezone('Asia/Muscat')
        now = datetime.datetime.now(oman_tz)

        self.date_group.current_date = now.date()
        self.date_group.year_adjuster.current_value = now.year
        self.date_group.month_adjuster.current_value = now.month
        max_day = calendar.monthrange(now.year, now.month)[1]
        self.date_group.day_adjuster.max_value = max_day
        self.date_group.day_adjuster.current_value = min(now.day, max_day)
        self.date_group.year_adjuster.update_display()
        self.date_group.month_adjuster.update_display()
        self.date_group.day_adjuster.update_display()

        hour_24 = now.hour
        minute_ = now.minute
        if hour_24 == 0:
            hour_12 = 12
        elif hour_24 > 12:
            hour_12 = hour_24 - 12
        else:
            hour_12 = hour_24

        period = "م" if hour_24 >= 12 else "ص"
        self.time_group.hour_adjuster.current_value = hour_12
        self.time_group.minute_adjuster.current_value = minute_
        self.time_group.period_adjuster.current_period = period
        self.time_group.prev_hour = hour_12
        self.time_group.hour_adjuster.update_display()
        self.time_group.minute_adjuster.update_display()
        self.time_group.period_adjuster.value_label.text = process_text(period)

        self.on_datetime_change()

# -------------------------------------------------------------------
# الصفحة الرئيسية
class HomeContent(BoxLayout):
    def __init__(self, dt, **kwargs):
        super().__init__(**kwargs)
        self.dt = dt
        self.orientation = "vertical"
        self.spacing = 15
        self.padding = [10, 10, 10, 10]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        welcome_label = Label(
            text=process_text("مرحباً بك"),
            font_size='20sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=40
        )
        welcome_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(welcome_label)

        phrases = [
            "الفلك مفتاح الكون",
            "كلنا نجوم",
            "انظر إلى السماء وارتقب المعجزات",
            "الكون واسع ومليء بالأسرار"
        ]
        random_phrase = random.choice(phrases)
        random_label = Label(
            text=process_text(random_phrase),
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=40
        )
        random_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(random_label)

        self.location_label = Label(
            text="",
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=40
        )
        self.location_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(self.location_label)

        self.moon_phase_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
        self.phase_label = Label(
            text="",
            font_size='18sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="right",
            valign="middle"
        )
        self.phase_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.moon_phase_box.add_widget(self.phase_label)
        phase_title_label = Label(
            text=process_text("طور القمر الحالي:"),
            font_size='18sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="left",
            valign="middle",
            size_hint_x=None,
            width=220
        )
        phase_title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.moon_phase_box.add_widget(phase_title_label)
        self.add_widget(self.moon_phase_box)

        bodies_title = Label(
            text=process_text("أجرام النظام الشمسي الظاهرة في السماء في الوقت المحدد:"),
            font_size='16sp',
            font_name="fonts/Amiri-Regular.ttf",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=40
        )
        bodies_title.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(bodies_title)

        self.bodies_box = GridLayout(cols=4, spacing=10, size_hint_y=None)
        self.bodies_box.bind(minimum_height=self.bodies_box.setter('height'))
        self.add_widget(self.bodies_box)

        self.update_content(dt)

    def update_content(self, dt):
        self.dt = dt
        loc = getattr(App.get_running_app(), "current_location_name", "مسقط")
        date_str = dt.strftime("%d/%m/%Y")
        time_str = dt.strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
        self.location_label.text = process_text(f"الموقع: {loc} | التاريخ: {date_str} | الوقت: {time_str}")

        oman_tz = pytz.timezone('Asia/Muscat')
        dt_local = dt if dt.tzinfo else oman_tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.UTC)
        t = ts.from_datetime(dt_utc)
        location = get_current_location()
        observer = eph['earth'] + location

        phase_angle = almanac.moon_phase(eph, t).degrees
        waxing = True if phase_angle < 180 else False
        phase_name = get_moon_phase_name(phase_angle, waxing)
        phase_ar_map = {
            "New Moon": "قمر جديد",
            "Waxing Crescent": "الهلال متزايد",
            "First Quarter": "التربيع الأول",
            "Waxing Gibbous": "الأحدب المتزايد",
            "Full Moon": "البدر",
            "Waning Gibbous": "أحدب متناقص",
            "Last Quarter": "التربيع الأخير",
            "Waning Crescent": "الهلال المتناقص",
            "Unknown": "غير معروف"
        }
        phase_name_ar = phase_ar_map.get(phase_name, phase_name)
        self.phase_label.text = process_text(phase_name_ar)

        bodies = {
            'Neptune BARYCENTER': 'نبتون',
            'Uranus BARYCENTER': 'أورانوس',
            'SATURN BARYCENTER': 'زحل',
            'JUPITER BARYCENTER': 'المشتري',
            'mars': 'المريخ',
            'venus': 'الزهرة',
            'mercury': 'عطارد',
            'moon': 'القمر',
            'sun': 'الشمس',
        }
        visible_bodies = []
        for key, arabic_name in bodies.items():
            try:
                body = eph[key]
            except Exception:
                continue
            astrometric = observer.at(t).observe(body).apparent()
            alt, _, _ = astrometric.altaz()
            if alt.degrees > 0:
                visible_bodies.append(arabic_name)
        self.bodies_box.clear_widgets()
        if visible_bodies:
            for name in visible_bodies:
                lbl = Label(
                    text=process_text(name),
                    font_size='16sp',
                    font_name="fonts/Amiri-Regular.ttf",
                    halign="left",
                    valign="top",
                    size_hint=(None, None),
                    size=(100, 30)
                )
                lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
                self.bodies_box.add_widget(lbl)
        else:
            lbl = Label(
                text=process_text("لا توجد أجرام ظاهرة"),
                font_size='16sp',
                font_name="fonts/Amiri-Regular.ttf",
                halign="center",
                valign="middle"
            )
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
            self.bodies_box.add_widget(lbl)

# -------------------------------------------------------------------
# شريط القائمة السفلية
class MenuWidget(BoxLayout):
    def __init__(self, content_area=None, **kwargs):
        super().__init__(**kwargs)
        self.content_area = content_area
        self.orientation = 'horizontal'
        self.spacing = 0
        self.size_hint_y = None
        self.height = 50

        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        sections = ["الخريطة", "القمر", "الكواكب", "الرئيسية"]
        for section in sections:
            btn = Button(
                text=process_text(section),
                font_name="fonts/Amiri-Regular.ttf",
                font_size='18sp',
                background_normal='',
                background_color=hex_to_rgba("#521876"),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=self.menu_pressed)
            self.add_widget(btn)

        self.options_widget = None
        self.preloaded_map = None

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def menu_pressed(self, instance):
        dt_group = self.options_widget.dt_adjuster
        dt_full = dt_group.get_datetime()
        text = instance.text

        if text == process_text("الكواكب"):
            self.content_area.set_content(PlanetsContent(dt=dt_full))
        elif text == process_text("القمر"):
            self.content_area.set_content(MoonContent(dt=dt_full))
        elif text == process_text("الخريطة"):
            if self.preloaded_map:
                self.preloaded_map.update_content(dt_full)
                self.content_area.set_content(self.preloaded_map)
            else:
                self.content_area.set_content(MapContent(dt=dt_full))
        elif text == process_text("الرئيسية"):
            dt_full = self.options_widget.dt_adjuster.get_datetime()
            self.content_area.set_content(HomeContent(dt=dt_full))

# -------------------------------------------------------------------
# رأس الصفحة
class HeaderWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 100
        self.orientation = 'vertical'
        with self.canvas.before:
            Color(*hex_to_rgba("#50106e"))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        header_label = Label(
            text=process_text("أجرام النظام الشمسي"),
            font_size='24sp',
            halign='center',
            valign='middle',
            font_name="fonts/Amiri-Regular.ttf",
            size_hint=(1,1),
            color=(1, 1,1, 1)
        )
        header_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self.add_widget(header_label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# -------------------------------------------------------------------
# مكان عرض المحتوى
class ContentArea(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_content(self, widget):
        self.clear_widgets()
        self.add_widget(widget)

# -------------------------------------------------------------------
# خيارات التطبيق (تشمل CombinedDateTimeAdjuster)
class OptionsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 80

        self.dt_adjuster = CombinedDateTimeAdjuster()
        self.add_widget(self.dt_adjuster)

# -------------------------------------------------------------------
# التطبيق الرئيسي
class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15

        header_area = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=100+80+50)
        header_area.add_widget(HeaderWidget())
        self.options_widget = OptionsWidget()
        header_area.add_widget(self.options_widget)

        self.menu = MenuWidget(None)
        header_area.add_widget(self.menu)

        self.add_widget(header_area)

        scroll = ScrollView(size_hint=(1, 1))
        self.content_area = ContentArea()
        scroll.add_widget(self.content_area)
        self.add_widget(scroll)

        self.menu.options_widget = self.options_widget
        self.menu.content_area = self.content_area

        self.options_widget.dt_adjuster.datetime_change_callback = self.update_current_content

        dt_full = self.options_widget.dt_adjuster.get_datetime()
        self.content_area.set_content(HomeContent(dt=dt_full))

        self.preloaded_map = None
        self.menu.preloaded_map = None

        Clock.schedule_once(lambda dt: self.preload_map(), 1)

        with self.canvas.before:
            Color(*hex_to_rgba("#300544"))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def preload_map(self):
        dt_current = self.options_widget.dt_adjuster.get_datetime()
        self.preloaded_map = MapContent(dt_current)
        self.menu.preloaded_map = self.preloaded_map

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_current_content(self, new_dt):
        if self.content_area.children:
            widget = self.content_area.children[0]
            if hasattr(widget, 'update_content'):
                widget.update_content(new_dt)

# -------------------------------------------------------------------
# تعديل MainScreen ليحتوي على دالة update_content لتحديث جميع الشاشات
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_widget = MainWidget()
        self.add_widget(self.main_widget)
    
    def update_content(self, new_dt):
        self.main_widget.update_current_content(new_dt)

class PlanetsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
        header = Label(
            text=process_text("معلومات الكواكب"),
            font_size='24sp',
            font_name="fonts/Amiri-Regular.ttf",
            size_hint_y=None,
            height=60,
            halign='center', valign='middle'
        )
        header.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        layout.add_widget(header)

        self.planets_content = PlanetsContent(dt=datetime.datetime.now(pytz.timezone('Asia/Muscat')))
        layout.add_widget(self.planets_content)

        back_button = Button(
            text=process_text("عودة"),
            size_hint_y=None,
            height=50,
            font_size='20sp',
            font_name="fonts/Amiri-Regular.ttf"
        )
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'main'
    
    def update_content(self, new_dt):
        self.planets_content.update_content(new_dt)

class MyScreenManager(ScreenManager):
    pass

# -------------------------------------------------------------------
# دالة لتحديث جميع الشاشات عند تغيير الموقع أو التاريخ/الوقت
def update_all_screens(new_dt):
    app = App.get_running_app()
    sm = app.root  # ScreenManager
    for screen in sm.screens:
        if hasattr(screen, 'update_content'):
            screen.update_content(new_dt)
        elif hasattr(screen, 'update_current_content'):
            screen.update_current_content(new_dt)
        else:
            for child in screen.children:
                if hasattr(child, 'update_content'):
                    child.update_content(new_dt)
                elif hasattr(child, 'update_current_content'):
                    child.update_current_content(new_dt)

# -------------------------------------------------------------------
# التطبيق الأساسي
class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_parser = ConfigParser()
        self.config_file = "user_settings.ini"
        self.current_location_name = "مسقط"
        self.load_location_preference()

    def load_location_preference(self):
        if os.path.exists(self.config_file):
            self.config_parser.read(self.config_file)
            if (self.config_parser.has_section("Location") and
                    self.config_parser.has_option("Location", "name")):
                self.current_location_name = self.config_parser.get("Location", "name")
        else:
            self.config_parser.add_section("Location")
            self.config_parser.set("Location", "name", self.current_location_name)
            self.config_parser.write()

    def save_location_preference(self):
        if not self.config_parser.has_section("Location"):
            self.config_parser.add_section("Location")
        self.config_parser.set("Location", "name", self.current_location_name)
        self.config_parser.write()

    def build(self):
        sm = MyScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(PlanetsScreen(name='planets'))
        return sm

if __name__ == '__main__':
    MyApp().run()
