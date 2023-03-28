import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import matplotlib.pyplot as plt
import matplotlib.backend_bases
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from RayleighCalibrator import RayleighCalibrator


class MainWindow(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.master = master
        self.width_master = 1350
        self.height_master = 450
        self.master.geometry(f'{self.width_master}x{self.height_master}')

        self.calibrator = RayleighCalibrator()
        self.index_to_show = 0

        self.line = None

        self.folder = './'

        self.create_widgets()

    def create_widgets(self) -> None:
        # canvas
        self.width_canvas = 1000
        self.height_canvas = 400
        dpi = 50
        if os.name == 'posix':
            self.width_canvas /= 2
            self.height_canvas /= 2
        fig, self.ax = plt.subplots(1, 2, figsize=(self.width_canvas / dpi, self.height_canvas / dpi), dpi=dpi)
        self.horizontal_line = self.ax[0].axhline(color='k', lw=0.8, ls='--')
        self.horizontal_line.set_visible(False)
        self.canvas = FigureCanvasTkAgg(fig, self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=3)
        toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0)
        plt.subplots_adjust(left=0.05, right=0.99, bottom=0.05, top=0.99)
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.key_pressed)
        self.canvas.mpl_connect('key_press_event', key_press_handler)

        # frames
        frame_data = tk.LabelFrame(self.master, text='Data')
        frame_download = tk.LabelFrame(self.master, text='Download')
        frame_plot = tk.LabelFrame(self.master, text='Plot')
        frame_data.grid(row=0, column=1)
        frame_download.grid(row=1, column=1)
        frame_plot.grid(row=2, column=1)

        # frame_data
        label_raw = tk.Label(frame_data, text='Raw:')
        self.filename_raw = tk.StringVar(value='please drag & drop!')
        label_filename_raw = tk.Label(frame_data, textvariable=self.filename_raw)
        label_ref = tk.Label(frame_data, text='Reference:')
        self.filename_ref = tk.StringVar(value='please drag & drop!')
        label_filename_ref = tk.Label(frame_data, textvariable=self.filename_ref)
        label_center = tk.Label(frame_data, text='Center [nm]:')
        self.center = tk.DoubleVar(value=self.calibrator.center)
        combobox_center = ttk.Combobox(frame_data, textvariable=self.center, values=[500, 630, 760], width=7, justify=tk.CENTER)
        self.material = tk.StringVar(value=self.calibrator.get_material_list()[0])
        optionmenu_material = tk.OptionMenu(frame_data, self.material, *self.calibrator.get_material_list())
        self.dimension = tk.StringVar(value=self.calibrator.get_dimension_list()[0])
        optionmenu_dimension = tk.OptionMenu(frame_data, self.dimension, *self.calibrator.get_dimension_list())
        self.function = tk.StringVar(value=self.calibrator.get_function_list()[0])
        optionmenu_function = tk.OptionMenu(frame_data, self.function, *self.calibrator.get_function_list())
        self.button_calibrate = tk.Button(frame_data, text='CALIBRATE', command=self.calibrate, state=tk.DISABLED)

        label_raw.grid(row=0, column=0)
        label_filename_raw.grid(row=0, column=1, columnspan=2)
        label_ref.grid(row=1, column=0)
        label_filename_ref.grid(row=1, column=1, columnspan=2)
        label_center.grid(row=2, column=0)
        combobox_center.grid(row=2, column=1, columnspan=2)
        optionmenu_material.grid(row=3, column=0)
        optionmenu_dimension.grid(row=3, column=1)
        optionmenu_function.grid(row=3, column=2)
        self.button_calibrate.grid(row=4, column=0, columnspan=3)

        # frame_download
        self.file_to_download = tk.Variable(value=[])
        self.listbox = tk.Listbox(frame_download, listvariable=self.file_to_download, selectmode=tk.MULTIPLE, width=8,
                                  height=6, justify=tk.CENTER)
        self.listbox.bind('<Button-2>', self.delete)
        self.listbox.bind('<Button-3>', self.delete)
        scrollbar = tk.Scrollbar(frame_download)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.button_add = tk.Button(frame_download, text='ADD', command=self.add)
        self.button_add_all = tk.Button(frame_download, text='ADD ALL', command=self.add_all)
        self.button_save = tk.Button(frame_download, text='SAVE', command=self.save)

        self.listbox.grid(row=0, column=0, columnspan=3)
        scrollbar.grid(row=0, column=2)
        self.button_add.grid(row=1, column=0)
        self.button_add_all.grid(row=1, column=1)
        self.button_save.grid(row=1, column=2)

        # frame plot
        self.color_range_1 = tk.DoubleVar(value=0)
        self.color_range_2 = tk.DoubleVar(value=2000)
        entry_color_range_1 = tk.Entry(frame_plot, textvariable=self.color_range_1, width=7, justify=tk.CENTER)
        entry_color_range_2 = tk.Entry(frame_plot, textvariable=self.color_range_2, width=7, justify=tk.CENTER)
        self.map_color = tk.StringVar(value='hot')
        self.optionmenu_map_color = tk.OptionMenu(frame_plot, self.map_color,
                                                  *sorted(['viridis', 'plasma', 'inferno', 'magma', 'cividis',
                                                           'Wistia', 'hot', 'binary', 'bone', 'cool', 'copper',
                                                           'gray', 'pink', 'spring', 'summer', 'autumn', 'winter',
                                                           'RdBu', 'Spectral', 'bwr', 'coolwarm', 'hsv', 'twilight',
                                                           'CMRmap', 'cubehelix', 'brg', 'gist_rainbow', 'rainbow',
                                                           'jet', 'nipy_spectral', 'gist_ncar']),
                                                  command=self.imshow)
        self.optionmenu_map_color.config(state=tk.DISABLED)
        self.autoscale = tk.BooleanVar(value=True)
        checkbox_autoscale = tk.Checkbutton(frame_plot, text='Auto Scale', variable=self.autoscale)
        self.button_apply = tk.Button(frame_plot, text='APPLY', command=self.imshow, width=7, state=tk.DISABLED)

        entry_color_range_1.grid(row=0, column=0)
        entry_color_range_2.grid(row=0, column=1)
        self.button_apply.grid(row=1, column=0, columnspan=2)
        self.optionmenu_map_color.grid(row=2, column=0, columnspan=3)
        checkbox_autoscale.grid(row=3, column=0, columnspan=3)

        # canvas_drop
        self.canvas_drop = tk.Canvas(self.master, width=self.width_master, height=self.height_master)
        self.canvas_drop.create_rectangle(0, 0, self.width_master, self.height_master / 2, fill='lightgray')
        self.canvas_drop.create_rectangle(0, self.height_master / 2, self.width_master, self.height_master, fill='gray')
        self.canvas_drop.create_text(self.width_master / 2, self.height_master / 4, text='2D Map RAS File',
                                     font=('Arial', 30))
        self.canvas_drop.create_text(self.width_master / 2, self.height_master * 3 / 4, text='Reference RAS File',
                                     font=('Arial', 30))

    def calibrate(self) -> None:
        self.calibrator.reset_data()
        self.calibrator.set_initial_xdata(self.center.get())
        self.calibrator.set_dimension(int(self.dimension.get()[0]))
        self.calibrator.set_material(self.material.get())
        self.calibrator.set_function(self.function.get())
        self.calibrator.set_search_width(10)
        ok = self.calibrator.calibrate(easy=True)
        if not ok:
            messagebox.showerror('Error', 'Peaks not found.')
            return
        self.ax[1].cla()
        self.calibrator.show_fit_result(self.ax[1])
        self.canvas.draw()

        self.line = None
        self.imshow()  # to update the xticklabels

    def on_click(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        if event.ydata is None:
            return
        self.index_to_show = round(event.ydata)
        self.update_plot()

    def key_pressed(self, event: matplotlib.backend_bases.KeyEvent) -> None:
        if event.key == 'enter':
            self.imshow()
            return
        if event.key == 'up' and self.index_to_show < self.calibrator.num_place - 1:
            self.index_to_show += 1
        elif event.key == 'down' and 0 < self.index_to_show:
            self.index_to_show -= 1
        else:
            return
        self.update_plot()

    def imshow(self, event=None) -> None:
        if self.calibrator.map_data is None:
            return
        self.ax[0].cla()
        self.horizontal_line = self.ax[0].axhline(color='k', lw=0.8, ls='--')
        self.horizontal_line.set_visible(True)
        self.calibrator.imshow(self.ax[0], [self.color_range_1.get(), self.color_range_2.get()], self.map_color.get())
        self.canvas.draw()

    def update_plot(self) -> None:
        self.horizontal_line.set_ydata(self.index_to_show)
        if not (0 <= self.index_to_show < self.calibrator.num_place):
            return

        if self.autoscale.get():
            plt.autoscale(True)
            self.ax[1].cla()
        else:
            if self.line is not None:
                plt.autoscale(False)  # The very first time requires autoscale
                self.line[0].remove()
            else:  # for after calibration
                self.ax[1].cla()
        self.line = self.ax[1].plot(
            self.calibrator.xdata,
            self.calibrator.map_data[self.index_to_show],
            label=str(self.index_to_show), color='r', linewidth=0.8)
        self.ax[1].legend()
        self.canvas.draw()

    def drop(self, event: TkinterDnD.DnDEvent=None) -> None:
        self.canvas_drop.place_forget()

        filename = event.data.split()[0]

        master_geometry = list(map(int, self.master.winfo_geometry().split('+')[1:]))
        dropped_place = (event.y_root - master_geometry[1] - 30) / self.height_canvas

        if os.name == 'posix':
            threshold = 1
        else:
            threshold = 0.5

        if dropped_place > threshold:  # reference data
            self.calibrator.load_ref(filename)
            self.filename_ref.set(os.path.split(filename)[-1])
            for material in self.calibrator.get_material_list():
                if material in filename:
                    self.material.set(material)
            self.button_calibrate.config(state=tk.ACTIVE)

            self.ax[1].cla()
            self.ax[1].plot(self.calibrator.xdata, self.calibrator.ydata, color='k')
            self.canvas.draw()

        else:  # raw data
            self.calibrator.load_raw(filename)
            self.filename_raw.set(os.path.basename(filename))
            self.folder = os.path.dirname(filename)

            self.optionmenu_map_color.config(state=tk.ACTIVE)
            self.button_apply.config(state=tk.ACTIVE)
            self.color_range_1.set(round(self.calibrator.map_data.min()))
            self.color_range_2.set(round(self.calibrator.map_data.max()))
            self.imshow()
            self.update_plot()

    def drop_enter(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place(anchor='nw', x=0, y=0)

    def drop_leave(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place_forget()

    def add(self) -> None:
        indices = self.file_to_download.get()
        if indices == '':
            indices = []
        else:
            indices = list(indices)
        indices.append(self.index_to_show)
        self.file_to_download.set(indices)

    def add_all(self) -> None:
        all_indices = list(range(self.calibrator.num_place))
        self.file_to_download.set(all_indices)

    def delete(self, event=None) -> None:
        if not messagebox.askyesno('Confirmation', 'Delete these?'):
            return
        for idx in sorted(list(self.listbox.curselection()), reverse=True):
            self.listbox.delete(idx)

    def save(self) -> None:
        if not self.file_to_download.get():
            return

        folder_to_save = filedialog.askdirectory(initialdir=self.folder)
        if not folder_to_save:
            return

        xdata = self.calibrator.xdata
        for index in self.file_to_download.get():
            spectrum = self.calibrator.map_data[index]
            abs_path_raw = os.path.join(self.folder, self.filename_raw.get())
            if self.filename_ref.get() == 'please drag & drop!':
                abs_path_ref = ''
            else:
                abs_path_ref = os.path.join(self.folder, self.filename_ref.get())
            filename = os.path.join(folder_to_save, f'{index}.txt')
            with open(filename, 'w') as f:
                f.write(f'# abs_path_raw: {abs_path_raw}\n')
                f.write(f'# abs_path_ref: {abs_path_ref}\n')
                f.write(f'# calibration: {self.calibrator.calibration_info}\n\n')

                for x, y in zip(xdata, spectrum):
                    f.write(f'{x},{y}\n')

    def quit(self) -> None:
        self.master.quit()
        self.master.destroy()


def main():
    root = TkinterDnD.Tk()
    app = MainWindow(master=root)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<DropEnter>>', app.drop_enter)
    root.dnd_bind('<<DropLeave>>', app.drop_leave)
    root.dnd_bind('<<Drop>>', app.drop)
    app.mainloop()


if __name__ == '__main__':
    main()
