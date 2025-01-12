import matplotlib.pyplot as plt

def plot_distribution(data, color_to_class):
  # Map categories to colors
  category_colors = {
    'unidentifiable': (0, 0, 0),
    'bamboo': (0, 0, 255),
    'forest': (0, 255, 0),
    'rice_field': (255, 0, 0),
    'water': (0, 255, 255),
    'residential': (255, 255, 0),
  }

  colors = [category_colors[key] for key in data.keys()]

  # Plotting the bar chart
  plt.bar(data.keys(), data.values(), color=[(r/255, g/255, b/255) for r, g, b in colors])

  # Adding title and labels
  plt.title('Distribution of Classes')
  plt.xlabel('Classes')
  plt.ylabel('Values')

  # Adding raw values on top of bars
  for i, (key, value) in enumerate(data.items()):
    plt.text(i, value + 0.005, f'{100 * value:.2f}%', ha='center')

  # Show plot
  plt.show()

# Example usage
data = {
'rice_field': 0.3910,
'residential': 0.3324,
'forest': 0.1559,
'unidentifiable': 0.0627,
'water': 0.0581,
}

color_to_class = {
  (0, 0, 0): 'unidentifiable',
  (0, 0, 255): 'bamboo',
  (0, 255, 0): 'forest',
  (255, 0, 0): 'rice_field',
  (0, 255, 255): 'water',
  (255, 255, 0): 'residential',
}

plot_distribution(data, color_to_class)
