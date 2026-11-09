import math
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Mesh
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton

Window.clearcolor = (0.02, 0.03, 0.07, 1)

# Optional Android AdMob via KivMob
try:
    from kivmob import KivMob, TestIds
    KIVMOB_AVAILABLE = True
except ImportError:
    KIVMOB_AVAILABLE = False

# Optional Android Hardware Sensors (Accelerometer & Proximity) for Presence-Based 2D/3D Switching
try:
    from plyer import accelerometer, proximity
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


class PresenceSensorManager:
    """
    Detects user presence & device posture to switch automatically between 2D and 3D:
    - When user holds the phone up at an angle (or approaches proximity/touches), switches to 3D Perspective!
    - When phone is laid flat on a desk (or user steps away / idle), switches smoothly to 2D Top-Down Map!
    """
    def __init__(self, orbit_canvas, status_cb):
        self.orbit_canvas = orbit_canvas
        self.status_cb = status_cb
        self.enabled = True
        self.last_interaction_time = 0.0
        self.sensor_active = False

        if PLYER_AVAILABLE:
            try:
                accelerometer.enable()
                self.sensor_active = True
            except Exception:
                self.sensor_active = False

    def update(self, dt):
        self.last_interaction_time += dt
        if not self.enabled:
            return

        if self.sensor_active:
            try:
                val = accelerometer.acceleration
                if val and val[0] is not None:
                    ax, ay, az = val
                    # Calculate tilt angle from flat horizontal table
                    tilt = math.sqrt(ax * ax + ay * ay)
                    if tilt > 3.2:
                        # User picked up phone / holding in hand -> 3D Mode + Tilt Pitch
                        if not self.orbit_canvas.is_3d:
                            self.orbit_canvas.is_3d = True
                            self.status_cb("Presence Sensor: Hand Posture Detected -> Switched to 3D View")
                        self.orbit_canvas.cam_pitch = max(0.15, min(1.35, tilt / 9.81))
                    else:
                        # Phone resting flat on desk -> 2D Top-Down Blueprint Mode
                        if self.orbit_canvas.is_3d and self.last_interaction_time > 6.0:
                            self.orbit_canvas.is_3d = False
                            self.status_cb("Presence Sensor: Flat Desk Mode -> Switched to 2D Top-Down View")
                    return
            except Exception:
                pass

        # Fallback Presence Logic (Touch/Cursor Activity Presence):
        # Active presence (< 12s since interaction) -> 3D Interactive Mode; Idle (> 12s) -> 2D Overview Map
        if self.last_interaction_time > 14.0 and self.orbit_canvas.is_3d:
            self.orbit_canvas.is_3d = False
            self.status_cb("Auto-Presence: User Idle -> 2D Overview Map (Touch to resume 3D)")
        elif self.last_interaction_time <= 0.2 and not self.orbit_canvas.is_3d:
            self.orbit_canvas.is_3d = True
            self.status_cb("Auto-Presence: User Active -> 3D Orbital Perspective Restored")


class MonetizationManager:
    """Manages Google AdMob Banner, Interstitial & Rewarded Video Ads + Local Pro Unlock."""
    def __init__(self, store, status_callback):
        self.store = store
        self.status_callback = status_callback
        self.is_pro = self.store.get("monetization")["is_pro"] if self.store.exists("monetization") else False
        self.ads = None

        if KIVMOB_AVAILABLE and not self.is_pro:
            self.ads = KivMob(TestIds.APP)
            self.ads.new_banner(TestIds.BANNER, top_pos=False)
            self.ads.request_banner()
            self.ads.show_banner()
            self.ads.new_interstitial(TestIds.INTERSTITIAL)
            self.ads.request_interstitial()
            self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)

    def show_interstitial(self):
        if self.is_pro:
            return
        if self.ads and self.ads.is_interstitial_loaded():
            self.ads.show_interstitial()
            self.ads.request_interstitial()
        else:
            self.status_callback("[AdMob] Interstitial Ad Slot Triggered (Test Mode)")

    def watch_rewarded_ad(self, on_reward_granted):
        if self.is_pro:
            on_reward_granted()
            return
        if self.ads:
            self.ads.show_rewarded_ad()
            on_reward_granted()
        else:
            self.status_callback("Rewarded Video Complete! Custom Exoplanet & Quiz Hints Unlocked.")
            on_reward_granted()

    def unlock_pro(self):
        self.is_pro = True
        self.store.put("monetization", is_pro=True)
        if self.ads:
            self.ads.hide_banner()
        self.status_callback("ASTRONOVA PRO Unlocked! All Ads Disabled Permanently.")


PLANETS = [
    {"name": "Mercury", "a": 0.387, "e": 0.2056, "i": 7.0,  "mass": 0.055, "color": (0.75, 0.72, 0.68), "radius": 5, "M0": 0.5},
    {"name": "Venus",   "a": 0.723, "e": 0.0067, "i": 3.4,  "mass": 0.815, "color": (0.95, 0.78, 0.45), "radius": 7, "M0": 1.8},
    {"name": "Earth",   "a": 1.000, "e": 0.0167, "i": 0.0,  "mass": 1.000, "color": (0.25, 0.65, 1.00), "radius": 7.5, "M0": 3.1},
    {"name": "Mars",    "a": 1.524, "e": 0.0934, "i": 1.85, "mass": 0.107, "color": (0.95, 0.40, 0.25), "radius": 6, "M0": 4.2},
    {"name": "Jupiter", "a": 5.203, "e": 0.0489, "i": 1.3,  "mass": 317.8, "color": (0.90, 0.68, 0.48), "radius": 11, "M0": 1.1},
    {"name": "Saturn",  "a": 9.537, "e": 0.0565, "i": 2.49, "mass": 95.16, "color": (0.92, 0.84, 0.55), "radius": 9.5, "M0": 2.6},
    {"name": "Uranus",  "a": 19.19, "e": 0.0457, "i": 0.77, "mass": 14.54, "color": (0.45, 0.88, 0.92), "radius": 8.5, "M0": 5.0},
    {"name": "Neptune", "a": 30.07, "e": 0.0113, "i": 1.77, "mass": 17.15, "color": (0.30, 0.50, 0.98), "radius": 8.5, "M0": 0.9},
    {"name": "Halley",  "a": 17.83, "e": 0.9671, "i": 18.0, "mass": 0.001, "color": (0.40, 0.98, 0.75), "radius": 5, "M0": 0.15},
    {"name": "Exoplanet-X", "a": 2.40, "e": 0.5800, "i": 22.0, "mass": 2.500, "color": (0.98, 0.35, 0.82), "radius": 8, "M0": 0.0},
]

QUIZ_QUESTIONS = [
    {
        "q": "According to Kepler's 1st Law, the sum of distances from any point on an orbit to the two foci (r1 + r2) equals:",
        "options": ["Semi-Major Axis (a)", "Twice Semi-Major Axis (2a)", "Focal Distance (2c)", "Eccentricity (e)"],
        "answer": 1,
        "explain": "An ellipse is defined by r1 + r2 = 2a at every point along the orbit."
    },
    {
        "q": "Where does a planet travel fastest according to Kepler's 2nd Law & the Vis-Viva equation?",
        "options": ["Aphelion (farthest)", "Empty Focus (F2)", "Perihelion (closest)", "Mean Anomaly = 90°"],
        "answer": 2,
        "explain": "At perihelion (minimum r), gravitational potential energy converts to kinetic energy, maximizing orbital speed."
    },
    {
        "q": "If a planet orbits a 1 Solar-Mass star at semi-major axis a = 4 AU, what is its orbital period T?",
        "options": ["4 Years", "8 Years", "16 Years", "64 Years"],
        "answer": 1,
        "explain": "By Kepler's 3rd Law, T^2 = a^3 = 4^3 = 64, so T = sqrt(64) = 8 Earth years."
    }
]


def solve_kepler(M, e, iterations=7):
    E = M if e < 0.8 else math.pi
    for _ in range(iterations):
        f = E - e * math.sin(E) - M
        f_prime = 1.0 - e * math.cos(E)
        if abs(f_prime) > 1e-9:
            E -= f / f_prime
    return E


class OrbitCanvas(FloatLayout):
    is_3d = BooleanProperty(True)
    law1_enabled = BooleanProperty(True)
    law2_enabled = BooleanProperty(True)
    compressed_scale = BooleanProperty(True)
    paused = BooleanProperty(False)

    cam_yaw = NumericProperty(0.6)
    cam_pitch = NumericProperty(0.58)
    zoom = NumericProperty(1.0)
    time_scale = NumericProperty(0.35)
    star_mass = NumericProperty(1.0)
    selected_idx = NumericProperty(2)

    def __init__(self, telemetry_callback, on_user_touch_cb, **kwargs):
        super().__init__(**kwargs)
        self.telemetry_callback = telemetry_callback
        self.on_user_touch_cb = on_user_touch_cb
        self.sim_time = 0.0
        self.last_touch_pos = None
        Clock.schedule_interval(self.update_simulation, 1.0 / 60.0)

    def scale_r(self, r_au):
        base = min(self.width, self.height) * 0.42 * self.zoom
        if self.compressed_scale:
            return base * (math.pow(max(r_au, 0.02), 0.43) / math.pow(31.0, 0.43))
        return base * (r_au / 6.0)

    def project_point(self, x_au, y_au, z_au):
        cx = self.x + self.width * 0.5
        cy = self.y + self.height * 0.52
        r_au = math.sqrt(x_au * x_au + y_au * y_au + z_au * z_au)
        if r_au < 1e-6:
            return cx, cy, 1.0
        s = self.scale_r(r_au) / r_au
        px, py, pz = x_au * s, y_au * s, z_au * s

        if not self.is_3d:
            return cx + px, cy + py, 1.0

        cos_y, sin_y = math.cos(self.cam_yaw), math.sin(self.cam_yaw)
        rx = px * cos_y - py * sin_y
        ry = px * sin_y + py * cos_y
        rz = pz

        cos_p, sin_p = math.cos(self.cam_pitch), math.sin(self.cam_pitch)
        fy = ry * cos_p - rz * sin_p
        fz = ry * sin_p + rz * cos_p

        fov = 900.0
        depth = max(300.0, fov - fz * 0.45)
        persp = fov / depth
        return cx + rx * persp, cy + fy * persp, persp

    def get_planet_3d_pos(self, body, E):
        a = body["a"]
        e = min(max(body["e"], 0.0), 0.98)
        inc = math.radians(body["i"])
        b = a * math.sqrt(1.0 - e * e)
        x_orb = a * (math.cos(E) - e)
        y_orb = b * math.sin(E)
        return x_orb, y_orb * math.cos(inc), y_orb * math.sin(inc)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.last_touch_pos = touch.pos
            self.on_user_touch_cb()
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.last_touch_pos and self.collide_point(*touch.pos):
            dx = touch.pos[0] - self.last_touch_pos[0]
            dy = touch.pos[1] - self.last_touch_pos[1]
            self.last_touch_pos = touch.pos
            self.on_user_touch_cb()
            if self.is_3d:
                self.cam_yaw += dx * 0.007
                self.cam_pitch = max(0.1, min(1.45, self.cam_pitch - dy * 0.007))
            return True
        return super().on_touch_move(touch)

    def update_simulation(self, dt):
        if self.width < 10 or self.height < 10:
            return
        if not self.paused:
            self.sim_time += dt * self.time_scale
            if self.is_3d:
                self.cam_yaw += dt * 0.12

        self.canvas.before.clear()
        with self.canvas.before:
            for ref_au in (1.0, 5.0, 15.0, 30.0):
                Color(0.15, 0.22, 0.35, 0.28)
                pts = []
                for step in range(49):
                    ang = (step / 48.0) * 2.0 * math.pi
                    sx, sy, _ = self.project_point(ref_au * math.cos(ang), ref_au * math.sin(ang), 0.0)
                    pts.extend([sx, sy])
                Line(points=pts, width=1.0)

            sun_x, sun_y, _ = self.project_point(0, 0, 0)
            Color(1.0, 0.65, 0.1, 0.25)
            Ellipse(pos=(sun_x - dp(20), sun_y - dp(20)), size=(dp(40), dp(40)))
            Color(1.0, 0.9, 0.3, 1.0)
            Ellipse(pos=(sun_x - dp(9), sun_y - dp(9)), size=(dp(18), dp(18)))

            for idx, body in enumerate(PLANETS):
                is_sel = (idx == self.selected_idx)
                a, e = body["a"], body["e"]
                period = math.sqrt((a ** 3) / max(self.star_mass, 0.1))
                n = (2.0 * math.pi) / period
                M = (body["M0"] + n * self.sim_time) % (2.0 * math.pi)
                E = solve_kepler(M, e)

                r, g, b_col = body["color"]
                Color(r, g, b_col, 0.85 if is_sel else 0.28)
                orbit_pts = []
                steps = 72 if is_sel else 48
                for s_i in range(steps + 1):
                    ang_E = (s_i / float(steps)) * 2.0 * math.pi
                    ox, oy, oz = self.get_planet_3d_pos(body, ang_E)
                    sx, sy, _ = self.project_point(ox, oy, oz)
                    orbit_pts.extend([sx, sy])
                Line(points=orbit_pts, width=dp(1.8) if is_sel else dp(1.0))

                px_au, py_au, pz_au = self.get_planet_3d_pos(body, E)
                sx, sy, persp = self.project_point(px_au, py_au, pz_au)

                if is_sel:
                    if self.law2_enabled:
                        dt_sweep = period * 0.06
                        for base_M, w_col in [(0.0, (0.2, 0.95, 0.6, 0.28)), (math.pi, (0.95, 0.4, 0.8, 0.28))]:
                            Color(*w_col)
                            vertices = [sun_x, sun_y, 0, 0]
                            indices = []
                            w_steps = 16
                            for w_i in range(w_steps + 1):
                                m_step = base_M + (w_i / float(w_steps)) * (n * dt_sweep)
                                e_step = solve_kepler(m_step, e)
                                wx, wy, wz = self.get_planet_3d_pos(body, e_step)
                                wsx, wsy, _ = self.project_point(wx, wy, wz)
                                vertices.extend([wsx, wsy, 0, 0])
                                if w_i > 0:
                                    indices.extend([0, w_i, w_i + 1])
                            Mesh(vertices=vertices, indices=indices, mode="triangles")

                    if self.law1_enabled:
                        c_au = a * e
                        f2_sx, f2_sy, _ = self.project_point(-2.0 * c_au, 0.0, 0.0)
                        Color(1.0, 0.35, 0.55, 0.95)
                        Line(circle=(f2_sx, f2_sy, dp(5)), width=dp(1.4))
                        Color(0.3, 0.95, 1.0, 0.85)
                        Line(points=[sun_x, sun_y, sx, sy], width=dp(1.3))
                        Color(1.0, 0.45, 0.65, 0.85)
                        Line(points=[f2_sx, f2_sy, sx, sy], width=dp(1.3))

                    r_dist = math.sqrt(px_au ** 2 + py_au ** 2 + pz_au ** 2)
                    v_kms = 29.7847 * math.sqrt(max(0.0, self.star_mass * (2.0 / max(r_dist, 1e-4) - 1.0 / a)))
                    r2_dist = 2.0 * a - r_dist
                    b_semi = a * math.sqrt(1.0 - e * e)
                    area_rate = (math.pi * a * b_semi) / period

                    self.telemetry_callback({
                        "name": body["name"], "a": a, "e": e, "i": body["i"],
                        "mass": body["mass"], "r1": r_dist, "r2": r2_dist,
                        "sum_r": r_dist + r2_dist, "v_kms": v_kms,
                        "period": period, "t2_a3": (period ** 2) / (a ** 3),
                        "area_rate": area_rate
                    })

                rad_px = dp(body["radius"]) * max(0.75, min(1.35, persp))
                if is_sel:
                    Color(1.0, 1.0, 1.0, 0.35)
                    Ellipse(pos=(sx - rad_px * 1.6, sy - rad_px * 1.6), size=(rad_px * 3.2, rad_px * 3.2))
                Color(r, g, b_col, 1.0)
                Ellipse(pos=(sx - rad_px, sy - rad_px), size=(rad_px * 2.0, rad_px * 2.0))


class AstroNovaApp(App):
    status_text = StringProperty("Presence Sensor Active | Drag to Rotate 3D | 100% Local (No Login)")

    def build(self):
        self.title = "ASTRONOVA: 3D Solar System & Kepler Lab"
        self.store = JsonStore("astronova_local_data.json")
        self.monetization = MonetizationManager(self.store, self.set_status)

        root = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(6))

        top_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))
        self.btn_tab_sim = ToggleButton(text="Observatory", group="main_tabs", state="down",
                                        background_color=(0.15, 0.55, 0.95, 1), font_size=sp(13))
        self.btn_tab_guide = ToggleButton(text="User Guide & Quiz", group="main_tabs",
                                          background_color=(0.2, 0.25, 0.38, 1), font_size=sp(13))
        self.btn_3d = Button(text="Mode: 3D", size_hint_x=0.65, background_color=(0.1, 0.7, 0.55, 1), font_size=sp(12))
        self.btn_presence = Button(text="Presence: ON", size_hint_x=0.75, background_color=(0.45, 0.35, 0.85, 1), font_size=sp(12))
        self.btn_pro = Button(text="PRO / Rewards", size_hint_x=0.7, background_color=(0.95, 0.65, 0.15, 1), font_size=sp(12))

        self.btn_tab_sim.bind(on_release=lambda *_: self.switch_view("sim"))
        self.btn_tab_guide.bind(on_release=lambda *_: self.switch_view("guide"))
        self.btn_3d.bind(on_release=self.toggle_2d_3d)
        self.btn_presence.bind(on_release=self.toggle_presence)
        self.btn_pro.bind(on_release=self.open_monetization_popup)

        for w in (self.btn_tab_sim, self.btn_tab_guide, self.btn_3d, self.btn_presence, self.btn_pro):
            top_bar.add_widget(w)
        root.add_widget(top_bar)

        self.content_area = BoxLayout(orientation="vertical")
        self.sim_view = self.build_simulator_view()
        self.guide_view = self.build_user_guide_view()
        self.content_area.add_widget(self.sim_view)
        root.add_widget(self.content_area)

        self.lbl_status = Label(text=self.status_text, size_hint_y=None, height=dp(26),
                                font_size=sp(11), color=(0.65, 0.82, 1.0, 1))
        root.add_widget(self.lbl_status)

        self.presence_mgr = PresenceSensorManager(self.orbit_canvas, self.set_status)
        self.orbit_canvas.bind(is_3d=lambda _, val: setattr(self.btn_3d, "text", "Mode: 3D" if val else "Mode: 2D"))
        Clock.schedule_interval(self.presence_mgr.update, 0.5)
        return root

    def set_status(self, msg):
        self.lbl_status.text = msg

    def on_user_interaction(self):
        if hasattr(self, "presence_mgr"):
            self.presence_mgr.last_interaction_time = 0.0
            self.presence_mgr.update(0.0)

    def build_simulator_view(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(4))
        planet_scroll = ScrollView(size_hint_y=None, height=dp(38), do_scroll_y=False)
        planet_bar = BoxLayout(size_hint_x=None, width=dp(820), spacing=dp(4))
        for idx, p in enumerate(PLANETS):
            btn = ToggleButton(text=p["name"], group="planets", state="down" if idx == 2 else "normal",
                               background_color=(0.22, 0.35, 0.58, 1), font_size=sp(12))
            btn.bind(on_release=lambda b, i=idx: self.select_planet(i))
            planet_bar.add_widget(btn)
        planet_scroll.add_widget(planet_bar)
        layout.add_widget(planet_scroll)

        self.orbit_canvas = OrbitCanvas(
            telemetry_callback=self.update_telemetry_labels,
            on_user_touch_cb=self.on_user_interaction
        )
        layout.add_widget(self.orbit_canvas)

        self.lbl_telemetry = Label(text="Initializing Kepler Solver...", size_hint_y=None, height=dp(68),
                                   font_size=sp(11.5), markup=True, halign="center", valign="middle")
        self.lbl_telemetry.bind(size=self.lbl_telemetry.setter("text_size"))
        layout.add_widget(self.lbl_telemetry)

        toggles_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        btn_l1 = ToggleButton(text="Law I: Foci (r1+r2=2a)", state="down", font_size=sp(11))
        btn_l2 = ToggleButton(text="Law II: Equal Areas", state="down", font_size=sp(11))
        btn_scale = ToggleButton(text="Scale: Compressed", state="down", font_size=sp(11))
        btn_pause = ToggleButton(text="Pause", font_size=sp(11), size_hint_x=0.5)

        btn_l1.bind(on_release=lambda b: setattr(self.orbit_canvas, "law1_enabled", b.state == "down"))
        btn_l2.bind(on_release=lambda b: setattr(self.orbit_canvas, "law2_enabled", b.state == "down"))
        btn_scale.bind(on_release=self.toggle_scale_mode)
        btn_pause.bind(on_release=lambda b: setattr(self.orbit_canvas, "paused", b.state == "down"))

        for b in (btn_l1, btn_l2, btn_scale, btn_pause):
            toggles_row.add_widget(b)
        layout.add_widget(toggles_row)

        sliders_grid = GridLayout(cols=2, size_hint_y=None, height=dp(96), spacing=dp(4))
        sliders_grid.add_widget(Label(text="Sim Speed & Zoom:", font_size=sp(11), size_hint_x=0.38))
        speed_zoom_box = BoxLayout(spacing=dp(6))
        s_speed = Slider(min=0.02, max=2.5, value=0.35)
        s_zoom = Slider(min=0.5, max=3.5, value=1.0)
        s_speed.bind(value=lambda _, v: setattr(self.orbit_canvas, "time_scale", v))
        s_zoom.bind(value=lambda _, v: setattr(self.orbit_canvas, "zoom", v))
        speed_zoom_box.add_widget(s_speed)
        speed_zoom_box.add_widget(s_zoom)
        sliders_grid.add_widget(speed_zoom_box)

        sliders_grid.add_widget(Label(text="Orbit Eccentricity (e):", font_size=sp(11), size_hint_x=0.38))
        self.slider_e = Slider(min=0.0, max=0.92, value=PLANETS[2]["e"])
        self.slider_e.bind(value=self.on_eccentricity_slider)
        sliders_grid.add_widget(self.slider_e)

        sliders_grid.add_widget(Label(text="Semi-Major Axis (a AU):", font_size=sp(11), size_hint_x=0.38))
        self.slider_a = Slider(min=0.3, max=32.0, value=PLANETS[2]["a"])
        self.slider_a.bind(value=self.on_axis_slider)
        sliders_grid.add_widget(self.slider_a)

        layout.add_widget(sliders_grid)
        return layout

    def build_user_guide_view(self):
        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(10), spacing=dp(12))
        box.bind(minimum_height=box.setter("height"))

        guide_markup = (
            "[b][size=18sp][color=#4dd0e1]ASTRONOVA USER GUIDE & KEPLER ENCYCLOPEDIA[/color][/size][/b]\n\n"
            "[b][color=#ffd54f]1. Smart Presence 2D/3D Sensor & Touch Controls[/color][/b]\n"
            "• [b]Presence Auto-Switching[/b]: When holding your phone in hand or actively interacting, ASTRONOVA renders "
            "a full [b]3D Perspective View[/b] with inclination tilt. Lay the phone flat on a desk (or step away) and it "
            "automatically transitions into a clean [b]2D Top-Down Blueprint Map[/b].\n"
            "• [b]Manual Override[/b]: Tap [i]Mode: 3D/2D[/i] or [i]Presence: ON/OFF[/i] anytime in the top bar.\n\n"
            "[b][color=#ffd54f]2. Studying Kepler's Three Laws[/color][/b]\n"
            "• [b]1st Law (Ellipses)[/b]: The Sun sits at Focus F1 and F2 is the Empty Focus. Notice in live telemetry that "
            "[b]r1 + r2 = 2a[/b] stays invariant across the entire orbit.\n"
            "• [b]2nd Law (Equal Areas)[/b]: Equal areas are swept in equal time ([b]dA/dt = const[/b]). Green (Perihelion) "
            "and Magenta (Aphelion) wedges have identical areas!\n"
            "• [b]3rd Law (Harmonic Law)[/b]: [b]T² / a³ = 1.000[/b] for all bodies orbiting a 1.0 Solar-Mass star."
        )
        lbl_guide = Label(text=guide_markup, markup=True, size_hint_y=None, font_size=sp(13), halign="left", valign="top")
        lbl_guide.bind(
            width=lambda *_: setattr(lbl_guide, "text_size", (lbl_guide.width, None)),
            texture_size=lambda *_: setattr(lbl_guide, "height", lbl_guide.texture_size[1] + dp(10))
        )
        box.add_widget(lbl_guide)

        for q_idx, item in enumerate(QUIZ_QUESTIONS):
            q_lbl = Label(text=f"[b]Q{q_idx + 1}: {item['q']}[/b]", markup=True, size_hint_y=None, height=dp(48), font_size=sp(12.5))
            q_lbl.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            box.add_widget(q_lbl)
            opts_grid = GridLayout(cols=2, size_hint_y=None, height=dp(76), spacing=dp(6))
            for o_idx, opt_text in enumerate(item["options"]):
                btn_opt = Button(text=opt_text, font_size=sp(11.5), background_color=(0.18, 0.28, 0.45, 1))
                btn_opt.bind(on_release=lambda b, qi=q_idx, oi=o_idx: self.check_quiz_answer(qi, oi))
                opts_grid.add_widget(btn_opt)
            box.add_widget(opts_grid)

        scroll.add_widget(box)
        return scroll

    def check_quiz_answer(self, q_idx, o_idx):
        item = QUIZ_QUESTIONS[q_idx]
        if o_idx == item["answer"]:
            self.set_status(f"Correct! {item['explain']}")
        else:
            self.set_status("Try again! Tap 'PRO / Rewards' -> Watch Ad for a full Physics Hint.")

    def select_planet(self, idx):
        self.on_user_interaction()
        self.orbit_canvas.selected_idx = idx
        self.slider_e.value = PLANETS[idx]["e"]
        self.slider_a.value = PLANETS[idx]["a"]
        if idx == 9:
            self.monetization.show_interstitial()

    def on_eccentricity_slider(self, instance, val):
        self.on_user_interaction()
        PLANETS[self.orbit_canvas.selected_idx]["e"] = val

    def on_axis_slider(self, instance, val):
        self.on_user_interaction()
        PLANETS[self.orbit_canvas.selected_idx]["a"] = val

    def toggle_2d_3d(self, instance):
        self.orbit_canvas.is_3d = not self.orbit_canvas.is_3d

    def toggle_presence(self, instance):
        self.presence_mgr.enabled = not self.presence_mgr.enabled
        instance.text = "Presence: ON" if self.presence_mgr.enabled else "Presence: OFF"

    def toggle_scale_mode(self, instance):
        self.orbit_canvas.compressed_scale = (instance.state == "down")
        instance.text = "Scale: Compressed" if self.orbit_canvas.compressed_scale else "Scale: True Linear"

    def switch_view(self, mode):
        self.content_area.clear_widgets()
        self.content_area.add_widget(self.sim_view if mode == "sim" else self.guide_view)

    def update_telemetry_labels(self, data):
        self.lbl_telemetry.text = (
            f"[b][color=#4dd0e1]{data['name'].upper()}[/color][/b] (Mass: {data['mass']} M⊕ | Tilt: {data['i']:.1f}°)   "
            f"[b]Speed (v):[/b] [color=#ffd54f]{data['v_kms']:.2f} km/s[/color]   "
            f"[b]Dist (r1):[/b] {data['r1']:.3f} AU\n"
            f"[b]Law I (r1+r2=2a):[/b] {data['r1']:.2f} + {data['r2']:.2f} = [color=#81c784]{data['sum_r']:.2f} AU[/color]   "
            f"[b]Law II (dA/dt):[/b] {data['area_rate']:.3f} AU²/yr   "
            f"[b]Law III (T²/a³):[/b] [color=#ff8a65]{data['t2_a3']:.3f}[/color] (T={data['period']:.2f} yr)"
        )

    def open_monetization_popup(self, *args):
        box = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        box.add_widget(Label(
            text=(
                "[b]Support ASTRONOVA Observatory[/b]\n\n"
                "• [b]Watch 1 Rewarded Ad[/b]: Unlock custom Exoplanet-X presets & Quiz explanations.\n"
                "• [b]Upgrade to ASTRONOVA PRO[/b]: Remove all banner & interstitial ads permanently (Stored locally, No Login!)."
            ),
            markup=True, halign="center"
        ))
        btn_reward = Button(text="Watch Rewarded Video (Free Bonus)", size_hint_y=None, height=dp(42),
                            background_color=(0.2, 0.65, 0.95, 1))
        btn_buy = Button(text="Unlock ASTRONOVA PRO (Remove Ads)", size_hint_y=None, height=dp(42),
                         background_color=(0.15, 0.8, 0.45, 1))
        btn_close = Button(text="Close", size_hint_y=None, height=dp(38))

        popup = Popup(title="ASTRONOVA Store & Rewards", content=box, size_hint=(0.88, 0.55))
        btn_reward.bind(on_release=lambda *_: (self.monetization.watch_rewarded_ad(lambda: None), popup.dismiss()))
        btn_buy.bind(on_release=lambda *_: (self.monetization.unlock_pro(), popup.dismiss()))
        btn_close.bind(on_release=popup.dismiss)

        for b in (btn_reward, btn_buy, btn_close):
            box.add_widget(b)
        popup.open()


if __name__ == "__main__":
    AstroNovaApp().run()
