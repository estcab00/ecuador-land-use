from PIL import Image

def create_gif(image_paths, output_gif_path, duration=500):
 images = [Image.open(image_path) for image_path in image_paths]
# Save as GIF
 images[0].save(
 output_gif_path,
 save_all=True,
 append_images=images[1:],
 duration=duration,
 loop=0 # 0 means infinite loop
 )

if __name__ == "__main__":
 # List of image file paths
 image_paths = [f"../04_output/ecuador_land_use_1985.jpg", f"../04_output/ecuador_land_use_1987.jpg",
                f"../04_output/ecuador_land_use_1992.jpg", f"../04_output/ecuador_land_use_1997.jpg",
                f"../04_output/ecuador_land_use_2002.jpg", f"../04_output/ecuador_land_use_2007.jpg",
                f"../04_output/ecuador_land_use_2012.jpg", f"../04_output/ecuador_land_use_2017.jpg",
                f"../04_output/ecuador_land_use_2022.jpg"] 

 output_gif_path = f"../04_output/ecuador_land_use.gif"

# Create GIF
create_gif(image_paths, output_gif_path)

print(f"GIF created and saved at {output_gif_path}")