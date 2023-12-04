# Sample dataset with normalized RGB values and corresponding color labels
# NEW COLOR NAMES
color_names = {
    (0.24, 0.26, 0.47): 'blue',

    (0.82, 0.09, 0.09): 'red',

    (0.18, 0.53, 0.26): 'green',

    (0.54, 0.3, 0.16): 'light brown',
    # Add more color samples here
}


def classify_color(rgb_array):
    closest_color = min(color_names, key=lambda x: sum((a - b) ** 2 for a, b in zip(x, rgb_array)))
    return color_names[closest_color]