def get_color_redLED(): # Get the colors of all the pixels of one frame of the red LED

    LED_zone = frame[h_led_s:h_led_e, w_led_s:w_led_e]
    one_frame_LED_colors = [] #Initialize a list to stock colors of pixels

    for row in range(LED_zone.shape[0]):
        for col in range(LED_zone.shape[1]):
            blue, green, red = frame[row, col]

            one_frame_LED_colors.append((blue, green, red))
    return one_frame_LED_colors

def mean_color_redLED(colors): # Get the mean color of one frame of the red LED

    mean_R, mean_G, mean_B = 0,0,0

    for color in colors:
        mean_R += color[0]
        mean_G += color[1]
        mean_B += color[2]
    
    nb_pixels = len(colors)
    mean_R /= nb_pixels
    mean_G /= nb_pixels
    mean_B /= nb_pixels

    return (mean_R, mean_B, mean_G)

def get_starting_time_redLED(): # Plot the luminescence as a function of frames, then extrapolate to get the starting time of lighting of the red LED
#TO DO


