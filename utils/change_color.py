import os
from PIL import Image

def change_color(image_path, old_color, new_color):
  image = Image.open(image_path).convert('RGBA')
  data = image.getdata()

  new_data = []
  for item in data:
    if item[:3] == old_color:
      new_data.append(new_color + (item[3],))
    else:
      new_data.append(item)

  image.putdata(new_data)
  image.save(image_path)

def process_images(folder_path, old_color, new_color):
  for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
      file_path = os.path.join(folder_path, filename)
      change_color(file_path, old_color, new_color)

if __name__ == "__main__":
  folder_path = 'final_dataset_new'
  old_color = (0, 0, 255)
  new_color = (0, 255, 0)
  process_images(folder_path, old_color, new_color)
