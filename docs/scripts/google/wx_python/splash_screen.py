import os
import wx
import wx.adv


class MyMainFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 300))
        panel = wx.Panel(self)
        text = wx.StaticText(panel, label="Welcome to My Application!", pos=(100, 100))


if __name__ == '__main__':
    app = wx.App()

    # Create and show the splash screen
    # Replace "splash_image.png" with the actual path to your image
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, "splash.png")
    bitmap = wx.Image(image_path).ConvertToBitmap()
    splash_style = wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT
    splash_screen = wx.adv.SplashScreen(bitmap, splash_style, 3000, None, -1)
    splash_screen.Show()

    # Initialize and show the main application frame
    main_frame = MyMainFrame(None, title="My Application")
    main_frame.Show()

    app.MainLoop()
