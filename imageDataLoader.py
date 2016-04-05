import sys
import re
import pandas as pd
import numpy as np

class imageDataLoader():

    def __init__(self, catalog_location):
        self.catalog_location = catalog_location 
        # pixels
        self.resolution = (96,96)
    
    def read_pgm(self, filename, byteorder='>'):
        """ reads pmg file. """
        with open(filename, 'rb') as f:
            buffer = f.read()
        try:
            header, width, height, maxval = re.search(
                b"(^P5\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n])*"
                b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", buffer).groups()
        except AttributeError:
            raise ValueError("Not a raw PGM file: '%s'" % filename)
        return np.frombuffer(buffer,
                                dtype='u1' if int(maxval) < 256 else byteorder+'u2',
                                count=int(width)*int(height),
                                offset=len(header)
                                ).reshape((int(height), int(width)))

    def load_data(self, file_name = "s", num_ppl = 40, num_images = 10):
        """ loads images dataset into panads dataframe """
        cols_names =  ['person_id','image_id', 'image']                    
        orl_images_df = pd.DataFrame(columns=cols_names)
                                 
        for person in range(1, num_ppl + 1):
          
            for img_idx in range(1, num_images + 1):
                path = (self.catalog_location + file_name + str(person) + "/" + 
                    str(img_idx) + ".pgm"
                        )
                # obrazki maja fromat 112x92, siec jest wytrenowana na 96x96
                # tymczasowe trywialne rozwiazanie : ucinamy nadliczbowe pixele z pionu (po polowie gora i dol)
                # dodajemy puste (0) paski z lewej i prawej (po 2 z kazdej strony o szerokosci pixela)
                image = self.read_pgm(path)[8 : 112 - 8,]
                image = np.insert(image,2,92 + np.zeros((2,image.shape[0])),1)
                image = np.insert(image,image.shape[1], np.zeros((2,image.shape[0])),1)

                orl_images_df= orl_images_df.append(pd.DataFrame(
                                [[person, img_idx, image]], 
                                columns=cols_names))          
        self.images_data_frame = orl_images_df
