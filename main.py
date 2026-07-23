import random
import math
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty, ListProperty, DictProperty, BooleanProperty
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import os
import traceback
from datetime import datetime

# ═══════════════════════════════════════════
#  KV DESIGN DECLARATION
# ═══════════════════════════════════════════
Builder.load_string('''
<CoinWidget>:
    size_hint: None, None
    size: dp(220), dp(220)
    canvas.before:
        # Subtle drop-shadow base
        Color:
            rgba: [0.02, 0.02, 0.05, 0.6]
        Ellipse:
            pos: self.center_x - (dp(85) * abs(root.scale_x)) + dp(4), self.center_y - dp(85) - dp(4)
            size: (dp(170) * abs(root.scale_x)), dp(170)
        
        # Outer Metallic Structural Rim
        Color:
            rgba: root.coin_color
        Ellipse:
            pos: self.center_x - (dp(85) * abs(root.scale_x)), self.center_y - dp(85)
            size: (dp(170) * abs(root.scale_x)), dp(170)
            
        # Inner Core Plate
        Color:
            rgba: root.core_color
        Ellipse:
            pos: self.center_x - (dp(78) * abs(root.scale_x)), self.center_y - dp(78)
            size: (dp(156) * abs(root.scale_x)), dp(156)

    Label:
        text: root.face_text
        font_size: max(dp(12), int(dp(46) * abs(root.scale_x)))
        bold: True
        color: root.text_color
        center: root.center


<CoinFlipRoot>:
    do_default_tab: False
    background_color: app.c_bg
    tab_pos: 'top_mid'
    tab_width: self.width / 3

    # ── TAB 1: FLIP INTERFACE ────────────────
    TabbedPanelItem:
        text: 'FLIP'
        background_color: app.c_panel if self.state == 'normal' else app.c_accent
        
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            canvas.before:
                Color:
                    rgba: app.c_bg
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: "COIN FLIP"
                font_size: dp(26)
                bold: True
                color: app.c_text
                size_hint_y: None
                height: dp(40)

            Label:
                text: root.decision_display
                font_size: dp(13)
                color: app.c_muted
                size_hint_y: None
                height: dp(20)
                halign: 'center'

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                CoinWidget:
                    id: coin_render

            Label:
                text: root.result_display
                font_size: dp(22)
                bold: True
                color: root.result_color
                size_hint_y: None
                height: dp(35)

            Label:
                text: root.streak_display
                font_size: dp(13)
                bold: True
                color: app.c_streak
                size_hint_y: None
                height: dp(20)

            Button:
                text: "INITIATE FLIP" if not root.is_flipping else "CALCULATING..."
                font_size: dp(16)
                bold: True
                size_hint_y: None
                height: dp(55)
                background_normal: ''
                background_color: app.c_accent if not root.is_flipping else app.c_muted
                disabled: root.is_flipping
                on_press: root.start_flip_sequence()

    # ── TAB 2: METRICS & DATA ────────────────
    TabbedPanelItem:
        text: 'DATA'
        background_color: app.c_panel if self.state == 'normal' else app.c_accent

        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            canvas.before:
                Color:
                    rgba: app.c_bg
                Rectangle:
                    pos: self.pos
                    size: self.size

            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(100)
                spacing: dp(10)

                # Heads Panel Card
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(10)
                    canvas.before:
                        Color:
                            rgba: app.c_card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(8)]
                    Label:
                        text: "HEADS"
                        font_size: dp(12)
                        color: app.c_muted
                    Label:
                        text: str(root.heads_count)
                        font_size: dp(32)
                        bold: True
                        color: app.c_gold

                # Tails Panel Card
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(10)
                    canvas.before:
                        Color:
                            rgba: app.c_card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(8)]
                    Label:
                        text: "TAILS"
                        font_size: dp(12)
                        color: app.c_muted
                    Label:
                        text: str(root.tails_count)
                        font_size: dp(32)
                        bold: True
                        color: app.c_silver

            # Milestones Tracker Box
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(4)
                size_hint_y: None
                height: dp(75)
                canvas.before:
                    Color:
                        rgba: app.c_panel
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(6)]
                Label:
                    text: "SYSTEM ACHIEVEMENT TIER"
                    font_size: dp(10)
                    bold: True
                    color: app.c_muted
                    anchor_x: 'left'
                Label:
                    text: root.achievement_badge
                    font_size: dp(15)
                    bold: True
                    color: app.c_accent

            Label:
                text: "RECENT HISTORY ARCHIVE"
                font_size: dp(12)
                bold: True
                color: app.c_muted
                size_hint_y: None
                height: dp(20)
                halign: 'left'

            # Graphic Row Layout for History Stream
            BoxLayout:
                id: history_container
                orientation: 'horizontal'
                spacing: dp(6)
                size_hint_y: None
                height: dp(45)

            Widget: # Spacer

            Button:
                text: "RESET ALL METRICS"
                font_size: dp(13)
                bold: True
                size_hint_y: None
                height: dp(45)
                background_normal: ''
                background_color: app.c_card
                color: app.c_text
                on_press: root.reset_metrics()

    # ── TAB 3: CONTROL SYSTEMS ───────────────
    TabbedPanelItem:
        text: 'SYSTEMS'
        background_color: app.c_panel if self.state == 'normal' else app.c_accent

        ScrollView:
            do_scroll_x: False
            BoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                size_hint_y: None
                height: self.minimum_height
                canvas.before:
                    Color:
                        rgba: app.c_bg
                    Rectangle:
                        pos: self.pos
                        size: self.size

                Label:
                    text: "VISUAL THEME ENGINE"
                    font_size: dp(12)
                    bold: True
                    color: app.c_muted
                    size_hint_y: None
                    height: dp(20)

                Spinner:
                    id: theme_selector
                    text: "Default Dark"
                    values: list(app.THEMES.keys())
                    size_hint_y: None
                    height: dp(45)
                    background_color: app.c_card
                    color: app.c_text
                    on_text: app.apply_theme_pack(self.text)

                Label:
                    text: "SYSTEM PROBABILITY WEIGHT: HEADS (" + str(int(prob_slider.value)) + "%)"
                    font_size: dp(12)
                    bold: True
                    color: app.c_muted
                    size_hint_y: None
                    height: dp(20)

                Slider:
                    id: prob_slider
                    min: 0
                    max: 100
                    value: 50
                    step: 1
                    size_hint_y: None
                    height: dp(35)
                    value_track: True
                    value_track_color: app.c_accent

                Label:
                    text: "DECISION MATRIX CAPTURE"
                    font_size: dp(12)
                    bold: True
                    color: app.c_muted
                    size_hint_y: None
                    height: dp(20)

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    size_hint_y: None
                    height: dp(65)
                    Label:
                        text: "Target routing if outcome is Heads:"
                        font_size: dp(11)
                        color: app.c_text
                        size_hint_y: None
                        height: dp(15)
                    TextInput:
                        id: input_heads
                        multiline: False
                        background_color: app.c_card
                        foreground_color: app.c_text
                        cursor_color: app.c_text

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    size_hint_y: None
                    height: dp(65)
                    Label:
                        text: "Target routing if outcome is Tails:"
                        font_size: dp(11)
                        color: app.c_text
                        size_hint_y: None
                        height: dp(15)
                    TextInput:
                        id: input_tails
                        multiline: False
                        background_color: app.c_card
                        foreground_color: app.c_text
                        cursor_color: app.c_text
''')

# ═══════════════════════════════════════════
#  UI WIDGET LOGIC MECHANICS
# ═══════════════════════════════════════════
class CoinWidget(Widget):
    scale_x = NumericProperty(1.0)
    coin_color = ListProperty([1, 1, 1, 1])
    core_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    face_text = StringProperty('?')


class CoinFlipRoot(TabbedPanel):
    heads_count = NumericProperty(0)
    tails_count = NumericProperty(0)
    streak_count = NumericProperty(0)
    
    result_display = StringProperty("— READY SYSTEM —")
    streak_display = StringProperty("")
    decision_display = StringProperty("")
    achievement_badge = StringProperty("RECRUIT LOGIST")
    
    result_color = ListProperty([1, 1, 1, 1])
    is_flipping = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CoinFlipRoot, self).__init__(**kwargs)
        self.history_records = []
        self._frames = []
        self._frame_idx = 0
        self.last_outcome = None
        Clock.schedule_once(self._post_init, 0.1)

    def _post_init(self, dt):
        self.clear_and_render_history_stream()
        self.update_coin_visuals(1.0, '?', App.get_running_app().c_muted)
        self.result_color = App.get_running_app().c_text

    def update_coin_visuals(self, scale, char, base_color):
        app = App.get_running_app()
        self.ids.coin_render.scale_x = scale
        self.ids.coin_render.face_text = char
        self.ids.coin_render.coin_color = base_color
        
        # Core dynamic darkening computation
        self.ids.coin_render.core_color = [base_color[0] * 0.65, base_color[1] * 0.65, base_color[2] * 0.65, 1.0]
        self.ids.coin_render.text_color = [base_color[0] * 0.40, base_color[1] * 0.40, base_color[2] * 0.40, 1.0]

    def start_flip_sequence(self):
        if self.is_flipping:
            return
        
        self.is_flipping = True
        self.result_display = "COMPUTING ENGINE..."
        self.result_color = App.get_running_app().c_muted
        self.decision_display = ""
        self.streak_display = ""

        # Tactical Probability Calculations
        h_prob = self.ids.prob_slider.value / 100.0
        self.final_outcome = 'Heads' if random.random() < h_prob else 'Tails'

        # Generate Sinusoidal Easing Curve Mapping Structural Rotation Simulation
        frames = []
        steps = 38
        for i in range(steps):
            progress = i / steps
            eased = 1 - (1 - progress) ** 3
            frames.append(math.cos(eased * 6 * math.pi))
            
        # Terminal settling frame sequence
        frames += [0.0, 0.20, 0.50, 0.80, 0.95, 1.0]
        self._frames = frames
        self._frame_idx = 0
        
        Clock.schedule_interval(self._execution_animate_tick, 0.02) # Fixed to 50fps

    def _execution_animate_tick(self, dt):
        app = App.get_running_app()
        if self._frame_idx >= len(self._frames):
            Clock.unschedule(self._execution_animate_tick)
            self._finalize_outcome()
            return

        x_scale = self._frames[self._frame_idx]
        progress_ratio = self._frame_idx / len(self._frames)

        if progress_ratio < 0.88:
            face = 'H' if x_scale >= 0 else 'T'
            color = app.c_gold if x_scale >= 0 else app.c_silver
        else:
            face = 'H' if self.final_outcome == 'Heads' else 'T'
            color = app.c_gold if self.final_outcome == 'Heads' else app.c_silver

        self.update_coin_visuals(x_scale, face, color)
        self._frame_idx += 1

    def _finalize_outcome(self):
        app = App.get_running_app()
        outcome = self.final_outcome
        active_color = app.c_gold if outcome == 'Heads' else app.c_silver
        
        self.update_coin_visuals(1.0, 'H' if outcome == 'Heads' else 'T', active_color)
        self.result_display = outcome.upper()
        self.result_color = active_color

        # Execution evaluation against decision map criteria
        matrix_text = self.ids.input_heads.text if outcome == 'Heads' else self.ids.input_tails.text
        if matrix_text.strip():
            self.decision_display = f"Routing Destination: {matrix_text.strip()}"

        # Streak System Tracking Checks
        if outcome == self.last_outcome:
            self.streak_count += 1
        else:
            self.streak_count = 1
        self.last_outcome = outcome

        if self.streak_count >= 3:
            self.streak_display = f"STREAK COMPLIANCE: {self.streak_count}x MULTIPLIER"

        if outcome == 'Heads':
            self.heads_count += 1
        else:
            self.tails_count += 1

        self.history_records.insert(0, outcome)
        if len(self.history_records) > 7:
            self.history_records.pop()
            
        self.clear_and_render_history_stream()
        self.recalculate_system_achievements()
        self.is_flipping = False

    def clear_and_render_history_stream(self):
        container = self.ids.history_container
        container.clear_widgets()
        app = App.get_running_app()

        for i in range(7):
            if i < len(self.history_records):
                rec = self.history_records[i]
                sym = 'H' if rec == 'Heads' else 'T'
                txt_color = app.c_gold if rec == 'Heads' else app.c_silver
                bg_color = app.c_card if i == 0 else app.c_panel
            else:
                sym = '·'
                txt_color = app.c_muted
                bg_color = app.c_bg

            # Python-based instantiation (Fixes memory leaks and lag)
            lbl = Label(
                text=sym,
                bold=True,
                font_size=dp(14),
                color=txt_color,
                size_hint_x=None,
                width=dp(38)
            )
            
            with lbl.canvas.before:
                Color(rgba=bg_color)
                lbl.rect = RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[dp(4)])

            def update_rect(instance, value):
                instance.rect.pos = instance.pos
                instance.rect.size = instance.size

            lbl.bind(pos=update_rect, size=update_rect)
            container.add_widget(lbl)

    def recalculate_system_achievements(self):
        total = self.heads_count + self.tails_count
        if self.streak_count >= 6:
            self.achievement_badge = "QUANTUM CHAOS LORD"
        elif total >= 25:
            self.achievement_badge = "MASTER PROBABILIST"
        elif self.streak_count >= 3:
            self.achievement_badge = "STREAK QUANTUM AGENT"
        elif total >= 10:
            self.achievement_badge = "DATA ENGINE ANALYST"
        else:
            self.achievement_badge = "RECRUIT LOGIST"

    def reset_metrics(self):
        if self.is_flipping:
            return
        self.heads_count = 0
        self.tails_count = 0
        self.streak_count = 0
        self.last_outcome = None
        self.history_records = []
        self.result_display = "— SYSTEM RESET Complete —"
        self.result_color = App.get_running_app().c_text
        self.decision_display = ""
        self.streak_display = ""
        self.achievement_badge = "RECRUIT LOGIST"
        Clock.schedule_once(self._reset_ui_safe, 0.05)

    def _reset_ui_safe(self, dt):
        app = App.get_running_app()

        if not app:
            return

        try:
            self.update_coin_visuals(1.0, '?', app.c_muted)
            self.clear_and_render_history_stream()
        except Exception as e:
            print("Reset UI error:", e)
# ═══════════════════════════════════════════
#  MAIN APPLICATION RUNNER
# ═══════════════════════════════════════════
class CoinFlipApp(App):
    c_bg = ListProperty()
    c_panel = ListProperty()
    c_card = ListProperty()
    c_accent = ListProperty()
    c_gold = ListProperty()
    c_silver = ListProperty()
    c_text = ListProperty()
    c_muted = ListProperty()
    c_streak = ListProperty()

    THEMES = {
        "Default Dark": {
            'BG': '#0a0a14', 'PANEL': '#11111f', 'CARD': '#18182a',
            'ACCENT': '#6644ee', 'GOLD': '#f5c518', 'SILVER': '#c8c8d8',
            'TEXT': '#e8e8f8', 'MUTED': '#44445a', 'STREAK': '#ff7722'
        },
        "Corporate Law": {
            'BG': '#0d1b2a', 'PANEL': '#1b263b', 'CARD': '#415a77',
            'ACCENT': '#b89b5e', 'GOLD': '#e0c080', 'SILVER': '#b0b0b0',
            'TEXT': '#e0e1dd', 'MUTED': '#778da9', 'STREAK': '#fca311'
        },
        "Isekai Slime": {
            'BG': '#001a2c', 'PANEL': '#003355', 'CARD': '#004f7a',
            'ACCENT': '#00bfff', 'GOLD': '#ffd700', 'SILVER': '#e0f7fa',
            'TEXT': '#ffffff', 'MUTED': '#5588aa', 'STREAK': '#00ffcc'
        },
        "Tactical Ops": {
            'BG': '#141a14', 'PANEL': '#1e261e', 'CARD': '#2d382d',
            'ACCENT': '#ff8c00', 'GOLD': '#ffb347', 'SILVER': '#a9b0a9',
            'TEXT': '#d3d8d3', 'MUTED': '#5b6b5b', 'STREAK': '#ff4500'
        }
    }

    def build(self):
        self.title = "Coin Flip Ultimate"
        self.apply_theme_pack("Default Dark")
        self.root_node = CoinFlipRoot()
        return self.root_node

    def apply_theme_pack(self, theme_name):
        pack = self.THEMES.get(theme_name, self.THEMES["Default Dark"])
        
        self.c_bg = get_color_from_hex(pack['BG'])
        self.c_panel = get_color_from_hex(pack['PANEL'])
        self.c_card = get_color_from_hex(pack['CARD'])
        self.c_accent = get_color_from_hex(pack['ACCENT'])
        self.c_gold = get_color_from_hex(pack['GOLD'])
        self.c_silver = get_color_from_hex(pack['SILVER'])
        self.c_text = get_color_from_hex(pack['TEXT'])
        self.c_muted = get_color_from_hex(pack['MUTED'])
        self.c_streak = get_color_from_hex(pack['STREAK'])

        if hasattr(self, 'root_node') and not self.root_node.is_flipping:
            self.root_node.update_coin_visuals(1.0, '?', self.c_muted)
            self.root_node.clear_and_render_history_stream()


# ═══════════════════════════════════════════
#  CRASH REPORTING (shows errors instead of silently dying)
# ═══════════════════════════════════════════
def _show_crash_popup(tb_text):
    content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

    scroll = ScrollView(size_hint=(1, 1))
    error_label = Label(
        text=tb_text,
        size_hint_y=None,
        halign='left',
        valign='top',
    )
    error_label.bind(
        width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
        texture_size=lambda inst, val: setattr(inst, 'height', val[1]),
    )
    scroll.add_widget(error_label)
    content.add_widget(scroll)

    close_btn = Button(text="Close", size_hint_y=None, height=dp(45))
    content.add_widget(close_btn)

    popup = Popup(
        title="Something went wrong",
        content=content,
        size_hint=(0.9, 0.8),
    )
    close_btn.bind(on_press=popup.dismiss)
    popup.open()


class AppCrashHandler(ExceptionHandler):
    """Catches otherwise-unhandled exceptions app-wide.

    Without this, an error raised inside a button press (like the
    reset-metrics bug) crashes the app with no explanation, especially
    on Android where there's no visible console. This logs the full
    traceback to a file and shows it in a popup, then lets the app
    keep running instead of dying.
    """

    def handle_exception(self, inst):
        tb_text = traceback.format_exc()
        print("=== UNHANDLED EXCEPTION ===")
        print(tb_text)

        try:
            app = App.get_running_app()
            log_dir = app.user_data_dir if app else os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(log_dir, "crash_log.txt")
            with open(log_path, "a") as f:
                f.write(f"\n[{datetime.now()}]\n{tb_text}\n")
        except Exception:
            pass

        Clock.schedule_once(lambda dt: _show_crash_popup(tb_text), 0)
        return ExceptionManager.PASS


ExceptionManager.add_handler(AppCrashHandler())


if __name__ == '__main__':
    CoinFlipApp().run()