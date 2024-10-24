# Load libraries
import rasterio
import numpy as np
import xml.etree.ElementTree as ET
import georasters as gr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# For plotting
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
from matplotlib_scalebar.scalebar import ScaleBar
from rasterio.plot import show
from matplotlib.patches import Patch, FancyArrow
from geo_northarrow import add_north_arrow
from pyproj import Transformer

# Data preparation
### Commented because the modification is being implemented in the second code
## We prepare the data for the analysis using TIF files for Ecuador's land use coverage from 1985 to 2022.
## The data is available in the data_original folder. We will modify the data to create only two classes: natural and anthropic land use.
# for year in ["1985", "1987", "1992", "1997", "2002", "1997", "2002", "2007", "2012", "2017", "2022"]:

#     # We open the raster file
#     with rasterio.open(f'data_original/ecuador_coverage_{year}.tif') as src:
        
#         block_size = 1024  
        
#         # We prepare the destination raster
#         with rasterio.open(
#             f'data_modified/ecuador_coverage_{year}_modified.tif',
#             'w',
#             driver='GTiff',
#             height=src.height,
#             width=src.width,
#             count=1,
#             dtype=src.dtypes[0],
#             crs=src.crs,
#             transform=src.transform
#         ) as dst:

#         # Since modifying the raster makes the process memory-intensive, we will read and write the raster in chunks
            
#             # We iterate over the raster in windows (chunks)
#             for i in range(0, src.height, block_size):
#                 for j in range(0, src.width, block_size):
#                     # We define a chunk to read and process
#                     window = rasterio.windows.Window(j, i, min(block_size, src.width - j), min(block_size, src.height - i))
                    
#                     # We read the data for this window
#                     data = src.read(1, window=window)
                    
#                     # We replace values for natural and anthropic land use
#                     data = np.where(np.isin(data, [3.0, 4.0, 5.0, 6.0, 11.0, 12.0, 29.0, 13.0, 33.0, 34.0, 31.0]), 1.0, data)
#                     data = np.where(np.isin(data, [9.0, 21.0, 30.0, 25.0]), 2.0, data)
#                     data = np.where(~np.isin(data, [0.0, 1.0, 2.0]), 0.0, data)  # Keep only 0.0, 1.0, 2.0
                    
#                     # We write the modified data back to the new raster file
#                     dst.write(data, window=window, indexes=1)

#     print(f"Raster modification complete for year {year}.")

# print("All rasters have been modified.")

# Plotting
## We will plot the modified rasters for each year and save the plots as images in the figures folder.
## We are slicing the data to exclude the Galapagos Islands and plotting the continental provinces' borders on top of the raster.
for year in ["1985", "1987", "1992", "1997", "2002", "1997", "2002", "2007", "2012", "2017", "2022"]:
    # We open the raster file
    with rasterio.open(f'../02_data/MB-Ecuador-{year}.tif') as src:
        # We read the raster data
        data = src.read(1)

        # We slice the raster data to exclude the Galapagos Islands
        sliced_data = data[:, 40000:]

        # We adjust the transform for the sliced portion
        new_transform = src.window_transform(((0, data.shape[0]), (40000, data.shape[1])))

        # We get the CRS of the raster
        raster_crs = src.crs

        cmap = ListedColormap(['none', 'green', 'yellow', 'none', 'none'])  # Custom colormap
        
        # We plot the raster
        fig, ax = plt.subplots(figsize=(10, 10))
        show(sliced_data, transform=new_transform, ax=ax, cmap=cmap)
        
        # We load the shapefile with the borders of the continental provinces
        ecuador_borders = gpd.read_file('../03_shapefiles/full_prov2.shp')

        current_crs = "EPSG:4326"

        # and set a CRS if the file does not contain one
        if ecuador_borders.crs is None:
            ecuador_borders = ecuador_borders.set_crs(current_crs)

        # then we reproject the borders to match the raster CRS
        ecuador_borders = ecuador_borders.to_crs(raster_crs)

        # We plot the continental borders on top of the raster
        ecuador_borders.boundary.plot(ax=ax, linewidth=0.8, edgecolor='black')

        # We repeat for the borders for the delimiting countries.
        limiting_borders = gpd.read_file('../03_shapefiles/ecuador_borders.shp')

        if limiting_borders.crs is None:
            limiting_borders = limiting_borders.set_crs(current_crs)

        limiting_borders = limiting_borders.to_crs(raster_crs)

        limiting_borders.boundary.plot(ax=ax, linewidth=1, edgecolor='black')
        limiting_borders.plot(ax=ax, color='#f2f2f2', edgecolor='black', linewidth=1)

        # We add text for "Peru" and "Colombia"
        ax.text(-76, -3.15, 'PERU', fontsize=15, color='black', ha='center', va='center')

        ax.text(-76, 1.5, 'COLOMBIA', fontsize=15, color='black', ha='center', va='center')

        # We repeat for the sea borders.
        ocean_borders = gpd.read_file('../03_shapefiles/ne_10m_ocean.shp')

        ocean_borders_crs = "EPSG:4326" 

        if ocean_borders.crs is None:
            ocean_borders = ocean_borders.set_crs(ocean_borders_crs)

        ocean_borders = ocean_borders.to_crs(raster_crs)

        ocean_borders.plot(ax=ax, color='#b2e8e8', alpha=0.5)

        # We add text for "Pacific Ocean"
        ax.text(-81, 0, 'PACIFIC \n OCEAN', fontsize=15, color='#519ad0', ha='center', va='center')

        # We set the axis limits to focus on Ecuador
        # Approximate lat/lon bounding box for Ecuador: [-82, -74.5, -5.5, 3] (lon_min, lon_max, lat_min, lat_max)
        transformer = Transformer.from_crs("EPSG:4326", raster_crs)

        xmin, ymin = transformer.transform(-82, -5.5)  # Lower-left corner (lon_min, lat_min)
        xmax, ymax = transformer.transform(-74.5, 3)   # Upper-right corner (lon_max, lat_max)

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        # We add a scalebar
        scalebar = ScaleBar(120, units='km', location='lower left', scale_loc='top', length_fraction=6667 / sliced_data.shape[1])
        ax.add_artist(scalebar)

        # and make the X and Y axis invisible
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # We add a custom legend
        legend_elements = [Patch(facecolor='green', edgecolor='black', label='Natural'),
                        Patch(facecolor='yellow', edgecolor='black', label='Anthropic')]
        
        ax.legend(handles=legend_elements, loc='lower right', title='Legend')

        # and a north arrow
        add_north_arrow(ax, scale=.75, xlim_pos=.15, ylim_pos=.865, color='#000', text_scaler=4, text_yT=-1.25)

        ax.set_title('Ecuador land use: Natural vs Anthropic', color='black', size=20, pad=20.0)
        ax.text(0.95, 0.95, f'${year}$', transform=ax.transAxes, fontsize=20, color='black', ha='right', va='top')

        # Finally we save the plot as an jpg image in the figures folder
        plt.savefig(f'../04_output/ecuador_land_use_{year}.jpg', dpi=300)

        print(f"Plotting complete for year {year} and saved at '../04_output/ecuador_land_use_{year}.jpg'.")
        
    print("All plots have been saved.")