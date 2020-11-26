import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

class MapRoute:
    def __init__(self, map_path=''):
        self.boundary_box = None
        self.waypoint_df = None
        self.map = plt.imread(map_path)
    
    def create_dataframe(self, flight_data):
        self.waypoint_df = pd.DataFrame(flight_data)
    
    def create_boundary_box(self):
        self.boundary_box = (self.waypoint_df.longitude.min(),
                             self.waypoint_df.longitude.max(),      
                             self.waypoint_df.latitude.min(),
                             self.waypoint_df.latitude.max())
        print(self.boundary_box)

    def create_and_show_plt(self):
        fig, ax = plt.subplots(figsize = (8,7))
        ax.scatter(self.waypoint_df.longitude, self.waypoint_df.latitude, zorder=1, alpha= 0.2, c='b', s=10)
        ax.set_title('Plotting Spatial Data on Lafayette, IN Map')
        ax.set_xlim(self.boundary_box[0],self.boundary_box[1])
        ax.set_ylim(self.boundary_box[2],self.boundary_box[3])
        ax.imshow(self.map, zorder=0, extent = self.boundary_box, aspect= 'equal')

        plt.show()
