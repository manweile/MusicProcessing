import wx
import os


class M3UEditor(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Simple M3U Editor', size=(500, 400))
        panel = wx.Panel(self)

        # UI Elements
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Track Path', width=400)

        btn_add = wx.Button(panel, label='Add Files')
        btn_del = wx.Button(panel, label='Remove Selected')
        btn_save = wx.Button(panel, label='Save M3U')

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn_sizer.Add(btn_add, 0, wx.ALL, 5)
        btn_sizer.Add(btn_del, 0, wx.ALL, 5)
        btn_sizer.Add(btn_save, 0, wx.ALL, 5)

        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        panel.SetSizer(sizer)

        # Events
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        btn_del.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)

    def on_add(self, event):
        with wx.FileDialog(self, "Select Audio Files", wildcard="Audio files (*.mp3;*.wav)|*.mp3;*.wav",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                for path in dlg.GetPaths():
                    self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), path)

    def on_delete(self, event):
        selected = self.list_ctrl.GetFirstSelected()
        while selected != -1:
            self.list_ctrl.DeleteItem(selected)
            selected = self.list_ctrl.GetFirstSelected()

    def on_save(self, event):
        with wx.FileDialog(self, "Save M3U File", wildcard="M3U files (*.m3u)|*.m3u",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    for i in range(self.list_ctrl.GetItemCount()):
                        f.write(self.list_ctrl.GetItemText(i) + "\n")
                wx.MessageBox(f"Playlist saved to {path}", "Success")


if __name__ == '__main__':
    app = wx.App()
    frame = M3UEditor()
    frame.Show()
    app.MainLoop()
