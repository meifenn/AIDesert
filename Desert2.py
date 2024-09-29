import pygame
import random

# Set up the screen dimensions and other constants
WIDTH = 1000
HEIGHT = 600
MAX_SPEED = 3
NUMBER_PEOPLE = 100  
THIRSTY_CHANCE = 0.5 
DRINK_DISTANCE = 10  
THIRSTY_TIME = 5000  # Time before a quenched person becomes thirsty again (milliseconds)
AVOID_DISTANCE = 50  # Distance at which people start avoiding obstacles

# -----------------------------------------------------------------------
# Person class represents each moving person in the simulation
# -----------------------------------------------------------------------

class Person:
    def __init__(self, x, y, thirsty=False) -> None:
        # Initialize position, velocity, and thirst status
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1  # Mass of the person
        self.thirsty = thirsty  # Thirst status
        self.last_drink_time = None  # To track when a person drinks water

    def update(self, current_time):
        # Update velocity and position of the person based on current acceleration
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            # Limit the speed to MAX_SPEED
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        # Reset acceleration after each update
        self.acceleration = pygame.Vector2(0, 0)

        # Check if it's time for a non-thirsty person to become thirsty again
        if not self.thirsty and self.last_drink_time is not None:
            if current_time - self.last_drink_time > THIRSTY_TIME:
                self.thirsty = True  # Person becomes thirsty again
                self.last_drink_time = None  # Reset drink timer

    def apply_force(self, x, y):
        # Apply a force to the person, adjusting acceleration based on mass
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def move_towards(self, target):
        # Calculate the direction towards the target and apply a force in that direction
        d = pygame.Vector2(target.position) - self.position
        distance = d.length()

        if distance > DRINK_DISTANCE:  # Only move towards if not already at the water
            d = d.normalize() * 0.1
            self.apply_force(d.x, d.y)

    def avoid_obstacle(self, obstacle):
        # Calculate the direction away from the obstacle if too close
        direction = self.position - obstacle.position
        distance = direction.length()

        if distance < obstacle.radius + AVOID_DISTANCE:
            # Apply a force in the opposite direction of the obstacle
            direction = direction.normalize() * 0.2
            self.apply_force(direction.x, direction.y)

    def drink_water(self):
        # When a person drinks water, they stop being thirsty
        self.thirsty = False
        self.last_drink_time = pygame.time.get_ticks()  # Record the time they drank

    def draw(self, screen):
        # Draw the person (thirsty people are blue, others are green)
        color = "blue" if self.thirsty else "green"
        pygame.draw.circle(screen, color, self.position, 5)

class WaterDrop:
    def __init__(self, x, y, image) -> None:
        self.position = pygame.Vector2(x, y)
        self.image = image

    def draw(self, screen):
        screen.blit(self.image, (self.position.x - self.image.get_width() // 2, self.position.y - self.image.get_height() // 2))

class Obstacle:
    def __init__(self, x, y, radius) -> None:
        self.position = pygame.Vector2(x, y)
        self.radius = radius

    def draw(self, screen):
        pass

# -----------------------------------------------------------------------
#  Begin 
# -----------------------------------------------------------------------
pygame.init()

# Create a window with the specified dimensions
screen = pygame.display.set_mode((WIDTH, HEIGHT))

waterDrop=pygame.image.load("waterDrop.png")
waterDrop = pygame.transform.scale(waterDrop, (20, 20))

background_image = pygame.image.load("desert_AI.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

clock = pygame.time.Clock()  # Initialize a clock to manage frame rate

font = pygame.font.Font(None, 36)

people = [Person(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), thirsty=random.random() < THIRSTY_CHANCE)
          for _ in range(NUMBER_PEOPLE)]

water_drops = []  

obstacles = [
    Obstacle(350, 25, 70),  
    Obstacle(225, 300, 50),  
    Obstacle(300, 250, 60), 
    Obstacle(550, 200, 50), 
    Obstacle(550, 200, 50),  
    Obstacle(950, 125, 75),
    Obstacle(950, 550, 40), 
    Obstacle(750, 550, 40) 
]

# ----- GAME LOOP ------------
running = True  
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False

    current_time = pygame.time.get_ticks()

    screen.blit(background_image, (0, 0))

    if pygame.mouse.get_pressed()[0]:
        water_drops.append(WaterDrop(*pygame.mouse.get_pos(), waterDrop))

    for water_drop in water_drops:
        water_drop.draw(screen)

    # Draw obstacles (optional: you can comment this out if you want invisible obstacles)
    for obstacle in obstacles:
        obstacle.draw(screen)

    for person in people:
        if person.thirsty:
            if water_drops:
                nearest_water = min(water_drops, key=lambda water: person.position.distance_to(water.position))
                if person.position.distance_to(nearest_water.position) < DRINK_DISTANCE:
                    water_drops.remove(nearest_water)  
                    person.drink_water()  
                else:
                    person.move_towards(nearest_water)

        # Avoid obstacles
        for obstacle in obstacles:
            person.avoid_obstacle(obstacle)

        person.update(current_time) 
        person.draw(screen) 

    for person in people:
        if person.position.x > WIDTH:
            person.position.x = 0
        elif person.position.x < 0:
            person.position.x = WIDTH
        if person.position.y > HEIGHT:
            person.position.y = 0
        elif person.position.y < 0:
            person.position.y = HEIGHT

    # Calculate and display FPS (frames per second) in the top-right corner of the screen
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, pygame.Color('white'))
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    pygame.display.flip()  # Update the screen with the drawn frame
    clock.tick(60)  # Limit the frame rate to 60 frames per second

pygame.quit()  # Clean up and close the game window when the loop ends
