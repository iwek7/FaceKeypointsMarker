import sys
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import csv



import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

from imageDataLoader import imageDataLoader

# used to embedding matplotlib image in qt app
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


class faceFeaturesMarker(QtGui.QMainWindow):
 
    # names of all keypoints
    KEYPOINT_NAMES = [
        "LEFT_EYE_LEFT",
        "LEFT_EYE_MIDDLE",
        "LEFT_EYE_RIGHT",
        "LEFT_BROW_LEFT",
        "LEFT_BROW_RIGHT",
        "RIGHT_EYE_LEFT",
        "RIGHT_EYE_MIDDLE",
        "RIGHT_EYE_RIGHT",
        "RIGHT_BROW_LEFT",
        "RIGHT_BROW_RIGHT",
        "NOSE",
        "MOUTH_LEFT",
        "MOUTH_RIGHT",
        "MOUTH_TOP",
        "MOUTH_DOWN"]
    # fixed height of all buttons in app
    BUTTON_HEIGHT = 25
    # fixed width of all buttons in app
    BUTTON_WIDTH = 125
    # number of people in dataset
    NUMER_OF_PEOPLE = 40
    # number of images of every person
    IMAGES_OF_PERSON = 10
    # stylesheet of active form with facial keypoint location
    ACTIVE_LINE_EDIT_STYLESHEET = ("color: blue;"
                                    "border-style: outset;"
                                    "border-width: 2px;"
                                    "border-radius: 5px;"
                                    "border-color: yellow;"
                                    "selection-background-color: blue;")
    # path to csv file that is dataset, saves and loads are made to/from this file
    DATA_FILE_PATH = "C:/scisoft/orl_faces_keypoints.csv"
    # precision of gathered datapoints data
    KEYPOINT_DATA_PRECISSION = 2

    # MOVE THIS SHIT TO OTHER CLASS ASAP
    dpi = 72.
    ypixels = 96 
    xpixels = 96 
    xinch = xpixels / dpi + 1
    yinch = ypixels / dpi + 1


    def __init__(self, parent=None):   
        """Initialize GUI as well as load dataset and create cache data structures."""
        super(QtGui.QMainWindow,self).__init__(parent)

        #setup window
        self.setGeometry(50,50,700,0)
        self.setWindowTitle("Features marker")
        
        # currently displayed person and image
        # those values are changes by buttons
        self.current_img = 0
        self.current_person = 0

        # dict of keypoit line edits,they need to be members because we need to change their value
        # when user clicks on image currently active keypoint line edit is filled with coordinates
        # currently active keypoint is marked by variable current_keypoint
        self.keypoints_line_edits = dict()
        for keypoint in self.KEYPOINT_NAMES: 
            qLine = QtGui.QLineEdit() 
            qLine.setDisabled(True)
            self.keypoints_line_edits[keypoint] = qLine

        # currently active facial keypoint (active line edit to writing)
        self.current_keypoint = self.KEYPOINT_NAMES[0]

        # to setup active keypoint line edit styleSheet
        # we need to deactivate old keypoint with this function but
        # (actove style is cleared [even though it has never been active] and restored)
        self.change_keypoint_line_edit_active(self.current_keypoint,self.current_keypoint)

        # datastructure which holds data of keypoints in memory
        # whole csv file (DATA_FILE_PATH)
        # todo : in the long run strongly consider using pandas dataframe
        # todo: rename to keypoints_data
        # structure -- person > image > keypoint > value 
        self.keypoints_data = dict()
        self.init_keypoints_data()

        # reads data from csv file (DATA_FILE_PATH) and loads it to keypoints_data
        # if dataset does not exist initiate with empty file
        # todo: add more data loading errors?
        try:
            self.read_data_from_csv()
        except FileNotFoundError:
            self.save_data_to_csv()
        except Exception:
            print("Unknown data loading error occured.")   
        # fill visible boxes with keypoints data from keypoints_data
        self.fill_current_keypoint_boxes_with_cached_data()
        # load pictures data into memory
        # todo: move it to other class to other file and give it more generic implementation (getData or something) so that it could be used with diffrent datasets
        self.data_loader = imageDataLoader("C:/Users/Michal/Documents/magisterka/dane/orl_faces/")
        self.data_loader.load_data()

        # initialize all widgets in window
        self.init_widgets()   
        # plot face on canvas widget            
        self.refresh_plot()

    def init_keypoints_data(self):
        """ fills keypoints_data with structure -- person > image > keypoint > value """
        for person_num in range(self.NUMER_OF_PEOPLE):
            self.keypoints_data[person_num] = dict()
            for img_num in range(self.IMAGES_OF_PERSON):
                self.keypoints_data[person_num][img_num] = dict()
                for keypoint in self.KEYPOINT_NAMES:
                    self.keypoints_data[person_num][img_num][keypoint] = tuple()

    # todo make better panel split
    def init_widgets(self):
        """ Initialize all widgets and put them in right possitions in the main window."""
        # main box that holds all subboxes
        main_box = QtGui.QGroupBox()
        # layaut of main box 
        main_layout = QtGui.QHBoxLayout()
        
        # setup box for buttons in leftmost panel
        main_menu_group_box = QtGui.QGroupBox()
        main_menu_layout = QtGui.QVBoxLayout()
        self.init_main_menu_layout(main_menu_layout)
        main_menu_group_box.setLayout(main_menu_layout)
        main_layout.addWidget(main_menu_group_box)

        # setup box keypoints menu
        keypoints_menu_box =  QtGui.QGroupBox()
        keypoints_menu_layout = QtGui.QVBoxLayout();
        self.init_keypoint_menu_layout(keypoints_menu_layout)
        keypoints_menu_box.setLayout(keypoints_menu_layout)
        main_layout.addWidget(keypoints_menu_box)

        # setup box for picure
        picture_group_box =  QtGui.QGroupBox()
        picture_layout = QtGui.QVBoxLayout();
        self.init_picture_canvas_layout(picture_layout)
        picture_group_box.setLayout(picture_layout)
        main_layout.addWidget(picture_group_box)
        

        main_box.setLayout(main_layout)

        self.setCentralWidget(main_box)

    

    def init_main_menu_layout(self, main_menu_layout):
        """ Initiates main menu layout. """
        ####
        # image swap
        ####
          
        img_swap_layout = QtGui.QHBoxLayout()
        # next img
        btn = QtGui.QPushButton("PREV", self)
        btn.clicked.connect(lambda: self.change_potted_img(-1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        img_swap_layout.addWidget(btn)

        # next img
        btn = QtGui.QPushButton("NEXT", self)
        btn.clicked.connect(lambda: self.change_potted_img(1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        img_swap_layout.addWidget(btn)

        img_swap_box = QtGui.QGroupBox()
        img_swap_box.setTitle("Change image")
        img_swap_box.setLayout(img_swap_layout)
        main_menu_layout.addWidget(img_swap_box)


        #####
        # person swap
        #####
        person_swap_layout = QtGui.QHBoxLayout()
        
        # prev person
        btn = QtGui.QPushButton("PREV", self)
        btn.clicked.connect(lambda: self.change_plotted_person(-1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        person_swap_layout.addWidget(btn)

        spacerItem = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        main_menu_layout.addItem(spacerItem)

        # next person
        btn = QtGui.QPushButton("NEXT", self)
        btn.clicked.connect(lambda: self.change_plotted_person(1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        person_swap_layout.addWidget(btn)

        person_swap_box = QtGui.QGroupBox()
        person_swap_box.setTitle("Change person")
        person_swap_box.setLayout(person_swap_layout)
        main_menu_layout.addWidget(person_swap_box)

        spacerItem = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        main_menu_layout.addItem(spacerItem)

        # buttons to save data to file
        btn = QtGui.QPushButton("SAVE",self)
        btn.clicked.connect(self.save_data_to_csv)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        main_menu_layout.addWidget(btn)

        # resets all keypoints on current image
        btn = QtGui.QPushButton("RESET",self)
        btn.clicked.connect(self.reset_all_current_img_keypoints)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        main_menu_layout.addWidget(btn)

        # quit app
        btn = QtGui.QPushButton("QUIT",self)
        btn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        main_menu_layout.addWidget(btn)

        # spacer item to squeeze all buttons to the top
        spacerItem = QtGui.QSpacerItem(20, 100, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        main_menu_layout.addItem(spacerItem)

    def init_keypoint_menu_layout(self, main_keypoints_layout):
        """ Initiates layout of keypoints menu."""
        # add control buttons
        controls_box = QtGui.QGroupBox()
        controls_box.setTitle("Active facial keypoint")
        controls_layout = QtGui.QHBoxLayout()

        btn = QtGui.QPushButton("PREV", self)
        btn.clicked.connect(lambda: self.change_current_keypoint(-1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        btn = QtGui.QPushButton("NEXT", self)
        btn.clicked.connect(lambda: self.change_current_keypoint(1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        btn = QtGui.QPushButton("CLEAR KEYPOINT", self)
        btn.clicked.connect(self.clear_current_keypoint)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        controls_box.setLayout(controls_layout)
        main_keypoints_layout.addWidget(controls_box)

        # add panel with keypoints data lineedits
        points_box = QtGui.QGroupBox()
        points_layout = QtGui.QFormLayout()

        for keypoint in self.KEYPOINT_NAMES:
            points_layout.addRow(keypoint, self.keypoints_line_edits[keypoint])
       
        points_box.setLayout(points_layout)
        main_keypoints_layout.addWidget(points_box)

    def init_picture_canvas_layout(self, picture_layout):
        """ initiates layaut of picture box """
        self.init_plot_objects()
        picture_layout.addWidget(self.canvas)
        keypoints_box = QtGui.QGroupBox()
        picture_layout.addWidget(keypoints_box)  

    def init_plot_objects(self):
        """ initiate plot objects - figure, axes and canvas. """
        self.fig = figure(facecolor="white", figsize = (self.xinch, self.yinch) )
        self.ax = self.fig.add_subplot(111) 
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)

    def change_current_keypoint(self, move):
        """ changes currenctly active keypoint flag"""
        new_keypoint_index = self.KEYPOINT_NAMES.index(self.current_keypoint) + move
        if len(self.KEYPOINT_NAMES) > new_keypoint_index >= 0:
            self.change_keypoint_line_edit_active(self.current_keypoint, self.KEYPOINT_NAMES[new_keypoint_index])
            self.current_keypoint = self.KEYPOINT_NAMES[new_keypoint_index]
              
    def change_keypoint_line_edit_active(self, old_keypoint, new_keypoint):
        """ marks box of current keypoint as active and deactivates old one"""    
        """ for now just changes styleSheet """
        self.keypoints_line_edits[old_keypoint].setStyleSheet("")
        self.keypoints_line_edits[new_keypoint].setStyleSheet(self.ACTIVE_LINE_EDIT_STYLESHEET)    

    def change_plotted_person(self, move):
        """ changes currently plotted person """
        new_person = self.current_person + move
        if self.NUMER_OF_PEOPLE > new_person >= 0:
            # move activity to the first keypoint edit line
            self.change_keypoint_line_edit_active(self.current_keypoint, self.KEYPOINT_NAMES[0])
            self.current_keypoint = self.KEYPOINT_NAMES[0]
            self.current_person = new_person
            self.current_img = 0
            self.refresh_plot()
            self.fill_current_keypoint_boxes_with_cached_data()

    def change_potted_img(self, move):
        """ changes currently potted image of the same person"""
        new_img = self.current_img + move
        if self.IMAGES_OF_PERSON > new_img >= 0:
            # move activity to the first keypoint edit line
            self.change_keypoint_line_edit_active(self.current_keypoint, self.KEYPOINT_NAMES[0])
            self.current_keypoint = self.KEYPOINT_NAMES[0]
            self.current_img = new_img 
            self.refresh_plot()
            self.fill_current_keypoint_boxes_with_cached_data()

    def fill_current_keypoint_boxes_with_cached_data(self):
        """Fills line edits of current image with data from keypoints_data"""
        for keypoint in self.KEYPOINT_NAMES:
            new_text = ""
            if self.keypoints_data[self.current_person][self.current_img][keypoint] != ():
                new_text = (str(self.keypoints_data[self.current_person][self.current_img][keypoint][0]) + 
                            ";" + 
                            str(self.keypoints_data[self.current_person][self.current_img][keypoint][1])
                            )
            self.keypoints_line_edits[keypoint].setText(new_text)

    def refresh_plot(self):
        """ Refreshes plot data and starts pooling events """
        self.ax.clear()  
        self.plot_keypoints_on_face()
        self.plot_face()
        self.canvas.draw() 
        # todo do we need to reactivate it every time image is changed?
        self.pool_plot_events() 
         

    #todo consider spliting into multiple functions with single responsibility
    def plot_face(self):
        """ plot face and pool events and process them"""
        if 0 <= self.current_person * self.IMAGES_OF_PERSON + self.current_img < self.NUMER_OF_PEOPLE * self.IMAGES_OF_PERSON:
            self.ax.imshow(self.data_loader.images_data_frame.iloc[self.current_person * self.IMAGES_OF_PERSON + self.current_img]['image'],  cmap='gray')
            
    def pool_plot_events(self):
        """ Waits for events happening on the plot and processes it accordingly. """
        for i in range(0,1):
            self.fig.canvas.mpl_connect('button_press_event', self.process_plot_mouse_click)

    def plot_keypoints_on_face(self):
        """ Adds scatter plot on top of face plot """
        for keypoint in self.KEYPOINT_NAMES:
            if self.keypoints_data[self.current_person][self.current_img][keypoint] != ():   
                plt.scatter([self.keypoints_data[self.current_person][self.current_img][keypoint][0]],
                    self.keypoints_data[self.current_person][self.current_img][keypoint][1])
       
    def process_plot_mouse_click(self, event):
        """ Processes mouse cli"""
        try:
            ix, iy = round(event.xdata, self.KEYPOINT_DATA_PRECISSION), round(event.ydata, self.KEYPOINT_DATA_PRECISSION)
        except TypeError:
            return
        if ix < 0 or iy < 0 or ix > self.xpixels or iy > self.ypixels:
            return
        self.keypoints_line_edits[self.current_keypoint].setText(str(ix) + ";" + str(iy))
        self.keypoints_data[self.current_person][self.current_img][self.current_keypoint] = (ix,iy,)
        self.change_current_keypoint(1)

        # now this is not nice
        # todo consider removeing pooling from refresh plot
        # here we can not use plot refresh because it will re-activate events pooling and weird recursion
        self.ax.clear()
        self.plot_keypoints_on_face()
        self.plot_face()
        self.canvas.draw() 

    def clear_current_keypoint(self):
        """ Removes current keypoint data from cache keypoints_data container, 
            from plot and from lineEdit """
        self.keypoints_data[self.current_person][self.current_img][self.current_keypoint] = tuple()
        self.keypoints_line_edits[self.current_keypoint].setText("")
        self.refresh_plot()        

    def reset_all_current_img_keypoints(self):
        """ Resets all values in keypoints_data of current image of current person to empty tuple 
            and cleares textbox of all text and sets focus to the first box, 
            also refreshes img to clear overlaying scatter plot """
        for keypoint in self.KEYPOINT_NAMES:
            self.keypoints_data[self.current_person][self.current_img][keypoint] = tuple()
            self.keypoints_line_edits[keypoint].setText("")
            # to setup active keypoint line edit styleSheet
            self.change_current_keypoint(-self.KEYPOINT_NAMES.index(self.current_keypoint))
        self.refresh_plot()

    def save_data_to_csv(self):
        """ exports data from keypoints_data to csv 
            we have one row per image with all the data in columns
        """
        with open(self.DATA_FILE_PATH, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for person in range(self.NUMER_OF_PEOPLE):
                for image in range(self.IMAGES_OF_PERSON):
                    keypoints_list = list()
                    for keypoint in self.KEYPOINT_NAMES:
                        # if data is empty then export empty spaces else export actual coordinates
                        if self.keypoints_data[person][image][keypoint] == ():
                            keypoints_list += ['','']
                        else:
                            keypoints_list += [i for i in self.keypoints_data[person][image][keypoint]]
                    writer.writerow([person,image] + keypoints_list)

    def read_data_from_csv(self):
        """ read data from csv file (pointed by DATA_FILE_PATH)
            to keypoints_data structure
        """
        with open(self.DATA_FILE_PATH, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='|')
            for row in reader:
                for keypoint_index in range(len(self.KEYPOINT_NAMES)):
                    if 2 * keypoint_index + 2 < len(row):  
                        new_tuple = (row[2 + 2 * keypoint_index], row[2 + 2 * keypoint_index + 1],)   
                        if new_tuple[0] == '' or  new_tuple[1] == '':   
                            new_tuple = tuple()
                        else:
                            new_tuple = double(new_tuple)            
                        self.keypoints_data[int(row[0])][int(row[1])][self.KEYPOINT_NAMES[keypoint_index]] = new_tuple

 
if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)
    MainWindow = faceFeaturesMarker()
    MainWindow.show()
    sys.exit(qApp.exec_())

