try:
    import cv2
except:
    from cv import cv2
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from android_permissions import AndroidPermissions
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from android import mActivity
    View = autoclass('android.view.View')

    @run_on_ui_thread
    def hide_landscape_status_bar(instance, width, height):
        # width,height gives false layout events, on pinch/spread
        # so use Window.width and Window.height
        if Window.width > Window.height:
            # Hide status bar
            option = View.SYSTEM_UI_FLAG_FULLSCREEN
        else:
            # Show status bar
            option = View.SYSTEM_UI_FLAG_VISIBLE
        mActivity.getWindow().getDecorView().setSystemUiVisibility(option)

class MainScreen(Screen):
    pass

class ScreenAfterButton(Screen):
    pass

Builder.load_file("main.kv")

class Main(App):
    def build(self):
        sm = ScreenManager()
        self.main_screen = MainScreen(name="main")
        self.screen_after = ScreenAfterButton(name="after")
        sm.add_widget(self.main_screen)
        sm.add_widget(self.screen_after)
        self.image = Image(
            size_hint=(None, None),
            size=(Window.width*1, Window.height*1),
            center=(Window.width*0.5, Window.height*0.5)
        )
        self.main_screen.add_widget(self.image, 1)
        self.capture = cv2.VideoCapture(0,cv2.CAP_ANDROID)
        if not self.capture.isOpened():
        	self.capture.open(0,cv2.CAP_ANDROID)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 2400)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('R','G','B','3'))
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        Clock.schedule_interval(self.load_video, 1 / 60)
        return sm
    
    def on_start(self):
        self.dont_gc = AndroidPermissions(self.start_app)
        
    def start_app(self):
        self.dont_gc = None

    def load_video(self, *args):
    	ret, frame = self.capture.read()
    	if ret:
    		self.image_frame = frame
    		buffer = cv2.flip(frame, 0).tostring()
    		texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
    		texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
    		self.image.texture = texture

    def take_picture(self, *args):
        image_name = "picture_a.png"
        if hasattr(self,'image_frame'):
            cv2.imwrite(image_name, self.image_frame)
            self.screen_after.ids['image_after'].texture = self.image.texture

class ImageButton(ButtonBehavior, Image):
    pass

if __name__ == '__main__':
    Main().run()
