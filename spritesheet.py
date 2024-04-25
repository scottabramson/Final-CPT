from pygame_functions import *




screenSize(600,600)
setBackgroundColour("black")
runsprite  = makeSprite("animations/run.png", 24)  # links.gif contains 32 separate frames of animation.
idlesprite  = makeSprite("animations/idle.png", 24)  # links.gif contains 32 separate frames of animation.
throwsprite  = makeSprite("animations/throw.png", 24)


def animation():

    global current_sprite  # Declare current_sprite as global to modify it within the function
    moveSprite(current_sprite, 300, 300, True)
    showSprite(current_sprite)

def run_animation():
    moveSprite(runsprite, 300, 300, True)
    showSprite(runsprite)

def idle_animation():
    moveSprite(idlesprite, 300, 300, True)
    showSprite(idlesprite)

def throw_animation():
    moveSprite(throwsprite, 300, 300, True)
    showSprite(throwsprite)

def run_loop():
    nextFrame = clock()
    frame = 0
    direction = None
    running = False  # Flag to indicate if the sprite is currently running

    while True:
        run_animation()  # Call the run animation function

        if clock() > nextFrame:
            if running:  # Only update if the sprite is running
                frame = (frame + 1) % 6
                nextFrame += 100  # Update time for next frame
                changeSpriteImage(runsprite, direction * 6 + frame)

        if keyPressed('d') or keyPressed('s') or keyPressed('a') or keyPressed('w'):
            if not running:
                direction = 0 if keyPressed('d') else \
                            3 if keyPressed('s') else \
                            2 if keyPressed('a') else \
                            1 if keyPressed('w') else None
                running = True
                nextFrame = clock()  # Reset the frame timer
        else:
            running = False

        tick(120)

    endWait()

def idle_loop():  # This function loops the animation continuously with the last direction pressed
    nextFrame = clock()
    frame = 0
    direction = None  # Initialize direction to None
    last_direction = 0  # Default to 0 (facing right) or another default direction

    while True:
        if keyPressed('d'):
            last_direction = 0  # Right
        elif keyPressed('a'):
            last_direction = 2  # Left
        elif keyPressed('w'):
            last_direction = 1  # Up
        elif keyPressed('s'):
            last_direction = 3  # Down

        # Decide which sprite to display based on the last key pressed
        if any([keyPressed('d'), keyPressed('a'), keyPressed('w'), keyPressed('s')]):
            direction = last_direction  # Update direction if any key is pressed
        else:
            direction = last_direction  # Keep the last direction active

        # Show idle animation and update frames
        idle_animation()  # Ensure this function does not interfere with the direction logic

        # Update frame and animation based on direction
        if clock() > nextFrame:
            frame = (frame + 1) % 6  # Assuming 6 frames per direction
            nextFrame += 100  # Update every 100 milliseconds
            changeSpriteImage(idlesprite, direction * 6 + frame)  # Apply correct frame

        tick(120)  # Limit to 120 ticks per second

    endWait()  # Keep the window open until a close event is triggered

def throw_loop():
    nextFrame = clock()
    frame = 0
    direction = None
    running = False  # Flag to indicate if the sprite is currently running

    while True:
        throw_animation()  # Call the run animation function

        # Check if it's time to update the sprite image
        if clock() > nextFrame:
            if running:  # Only update if the sprite is running
                frame = (frame + 1) % 6  # Use %7 if you have 7 frames per direction
                nextFrame += 100  # Update time for next frame

                # Update sprite image based on current direction
                changeSpriteImage(throwsprite, direction * 6 + frame)

        # Check for key presses and releases to update the running state
        if keyPressed("d") or keyPressed("s") or keyPressed("a") or keyPressed("w"):
            if not running:  # If not already running, start the animation
                direction = 0 if keyPressed("d") else \
                            3 if keyPressed("s") else \
                            2 if keyPressed("a") else \
                            1 if keyPressed("w") else None
                running = True
                nextFrame = clock()  # Reset the frame timer
        else:
            # If no direction keys are pressed, stop the animation
            running = False

        tick(120)

    endWait()





# Call loop() to start the loop
throw_loop()

