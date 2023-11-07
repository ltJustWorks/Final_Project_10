# Sample dataset with normalized RGB values and corresponding color labels
color_names = {
    (0.28, 0.26, 0.47): 'blue',

    (0.82, 0.09, 0.09): 'red',

    (0.21, 0.52, 0.27): 'green',

    (0.54, 0.28, 0.18): 'light brown',
    # Add more color samples here
}

def classify_color(rgb_array):
    closest_color = min(color_names, key=lambda x: sum((a - b) ** 2 for a, b in zip(x, rgb_array)))
    return color_names[closest_color]