import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

class GUIManager(object):
    # fixed height of all buttons in app
    BUTTON_HEIGHT = 25
    # fixed width of all buttons in app
    BUTTON_WIDTH = 125

    PERSON_LABEL_STR = "Person : "
    PICTURE_LABEL_STR = "Image : "

    # stylesheet of label
    PICTURE_LABELS_STYLESHEET = (   "font : bold 16px" 
                                    )
    def __init__(self, parent):
        self.parent = parent

        # dict of keypoit line edits,they need to be members because we need to change their value
        # when user clicks on image currently active keypoint line edit is filled with coordinates
        # currently active keypoint is marked by variable current_keypoint
        self.keypoints_line_edits = dict()
        for keypoint in self.parent.KEYPOINT_NAMES: 
            qLine = QtGui.QLineEdit() 
            qLine.setDisabled(True)
            self.keypoints_line_edits[keypoint] = qLine

        # list of labels of image
        self.picture_labels = dict()
        self.picture_labels["person_label"] = QtGui.QLabel(self.PERSON_LABEL_STR)
        self.picture_labels["person_label"].setStyleSheet(self.PICTURE_LABELS_STYLESHEET)
        self.picture_labels["picture_label"] = QtGui.QLabel(self.PICTURE_LABEL_STR)
        self.picture_labels["picture_label"].setStyleSheet(self.PICTURE_LABELS_STYLESHEET)
    

    def update_person_label(self, person_num = None):
        # + 1 to displayed number because we have 0 based lists and it is weird
        self.picture_labels["person_label"].setText(self.PERSON_LABEL_STR + str(person_num + 1))

    def update_picture_label(self, image_num = None):
        # + 1 to displayed number because we have 0 based lists and it is weird
        self.picture_labels["picture_label"].setText(self.PICTURE_LABEL_STR + str(image_num + 1))


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

        # todo move initiating canvas and pictures to separate function
        # setup box for picure
        picture_group_box =  QtGui.QGroupBox()
        picture_layout = QtGui.QVBoxLayout()
        self.init_picture_column_layout(picture_layout)
        picture_group_box.setLayout(picture_layout)
        main_layout.addWidget(picture_group_box)

        # add all boxes to main layout
        main_box.setLayout(main_layout)
        self.parent.setCentralWidget(main_box)

    def init_picture_column_layout(self, picture_layout):
        """Initiates layout of last column - picture and labels. """
        self.init_picture_canvas_layout(picture_layout)
        self.init_picture_labels_layout(picture_layout)
        spacerItem = QtGui.QSpacerItem(200, 100, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        picture_layout.addItem(spacerItem)

    def init_main_menu_layout(self, main_menu_layout):
        """ Initiates main menu layout. """
        ####
        # image swap
        ####
          
        img_swap_layout = QtGui.QHBoxLayout()
        # next img
        btn = QtGui.QPushButton("PREV", self.parent)
        btn.clicked.connect(lambda: self.parent.change_potted_img(-1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        img_swap_layout.addWidget(btn)

        # next img
        btn = QtGui.QPushButton("NEXT", self.parent)
        btn.clicked.connect(lambda: self.parent.change_potted_img(1))
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
        btn = QtGui.QPushButton("PREV", self.parent)
        btn.clicked.connect(lambda: self.parent.change_plotted_person(-1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        person_swap_layout.addWidget(btn)

        spacerItem = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        main_menu_layout.addItem(spacerItem)

        # next person
        btn = QtGui.QPushButton("NEXT", self.parent)
        btn.clicked.connect(lambda: self.parent.change_plotted_person(1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        person_swap_layout.addWidget(btn)

        person_swap_box = QtGui.QGroupBox()
        person_swap_box.setTitle("Change person")
        person_swap_box.setLayout(person_swap_layout)
        main_menu_layout.addWidget(person_swap_box)

        spacerItem = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        main_menu_layout.addItem(spacerItem)

        # buttons to save data to file
        btn = QtGui.QPushButton("SAVE",self.parent)
        btn.clicked.connect(self.parent.save_data_to_csv)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        main_menu_layout.addWidget(btn)

        # resets all keypoints on current image
        btn = QtGui.QPushButton("RESET PICTURE KEYPOINTS", self.parent)
        btn.clicked.connect(self.parent.reset_all_current_img_keypoints)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        main_menu_layout.addWidget(btn)

        # quit app
        btn = QtGui.QPushButton("QUIT", self.parent)
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

        btn = QtGui.QPushButton("PREV",  self.parent)
        btn.clicked.connect(lambda: self.parent.change_current_keypoint(-1))
        btn.resize(self.BUTTON_WIDTH,  self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        btn = QtGui.QPushButton("NEXT",  self.parent)
        btn.clicked.connect(lambda:  self.parent.change_current_keypoint(1))
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        btn = QtGui.QPushButton("CLEAR KEYPOINT",  self.parent)
        btn.clicked.connect(self.parent.clear_current_keypoint)
        btn.resize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        controls_layout.addWidget(btn)

        controls_box.setLayout(controls_layout)
        main_keypoints_layout.addWidget(controls_box)

        # add panel with keypoints data lineedits
        points_box = QtGui.QGroupBox()
        points_layout = QtGui.QFormLayout()

        for keypoint in self.parent.KEYPOINT_NAMES:
            points_layout.addRow(keypoint, 
                self.keypoints_line_edits[keypoint])
       
        points_box.setLayout(points_layout)
        main_keypoints_layout.addWidget(points_box)

    def init_picture_canvas_layout(self, picture_layout):
        """ initiates layaut of picture box """
        self.parent.init_plot_objects()
        picture_layout.addWidget(self.parent.canvas)

    def init_picture_labels_layout(self, picture_layout):
        """Initiate layout with image labels."""
        labels_box = QtGui.QGroupBox()
        labels_layout = QtGui.QVBoxLayout()

        labels_layout.addWidget(self.picture_labels["picture_label"])
        labels_layout.addWidget(self.picture_labels["person_label"])

        labels_box.setLayout(labels_layout)
        picture_layout.addWidget(labels_box)