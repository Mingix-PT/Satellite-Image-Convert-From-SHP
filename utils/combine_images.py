from PIL import Image

extension = '.png'

# List of image paths to combine
base_path = '/Downloads/'
images = [f'{x}{extension}' for x in range(1, 7)]
image_paths = [base_path + img for img in images]

# Open images
images = [Image.open(img_path) for img_path in image_paths]

# Find the width of the widest image
max_width = max(img.width for img in images)

# Resize images to the max width while maintaining aspect ratio
resized_images = []
for img in images:
    # Calculate new height to maintain aspect ratio
    new_height = int(img.height * (max_width / img.width))
    resized_images.append(img.resize((max_width, new_height)))

# Calculate the total height for the final image
total_height = sum(img.height for img in resized_images)

# Create a new blank image with the max width and total height
combined_image = Image.new('RGB', (max_width, total_height))

# Paste images one below the other
y_offset = 0
for img in resized_images:
    combined_image.paste(img, (0, y_offset))
    y_offset += img.height

# Save the final combined image
combined_image.save(f'combined_image{extension}')
