import math
import logging
import arcade
import pymunk
from game_logic import get_angle_radians

from game_object import Bird, BlueBird, Column, Pig, YellowBird, Beam
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1800
HEIGHT = 800
TITLE = "Angry birds"
GRAVITY = -900


class App(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background = arcade.load_texture("assets/img/background3.png")
        self.slingshot_texture = arcade.load_texture("assets/img/sling-3.png")
        self.current_bird_image = "assets/img/red-bird3.png"
        self.beam_texture = arcade.load_texture("assets/img/beam.png")
        # crear espacio de pymunk

        
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        #self.add_columns()
        self.add_piramide()
        self.add_pigs()

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.draw_slingshot = False

        # agregar un collision handlers
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler
        self.actual_bird = "Red"


    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.Z:
            self.current_bird_image = "assets/img/red-bird3.png"
            self.actual_bird = "Red"
        elif key == arcade.key.X:
            self.current_bird_image = "assets/img/blue.png"
            self.actual_bird = "Blue"
        elif key == arcade.key.C:
            self.current_bird_image = "assets/img/yellow.png"
            self.actual_bird = "Yellow"

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)

        return True

    def add_piramide(self):
        column = Column(WIDTH // 2 + 40, 150, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Column(WIDTH // 2 + 117, 150, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Beam(WIDTH // 2 + 79, 200, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Column(WIDTH // 2, 50, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Column(WIDTH // 2 + 77, 50, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Column(WIDTH // 2 + 154, 50, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Beam(WIDTH // 2 + 35, 100, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Beam(WIDTH // 2 + 120, 100, self.space)
        self.sprites.append(column)
        self.world.append(column)


        column = Column(WIDTH // 2 + 250, 50, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Column(WIDTH // 2 + 327, 50, self.space)
        self.sprites.append(column)
        self.world.append(column)
        column = Beam(WIDTH // 2 + 285, 100, self.space)
        self.sprites.append(column)
        self.world.append(column)

        

    def add_columns(self):
        for x in range(WIDTH // 2, WIDTH, 400):
            column = Column(x, 50, self.space)
            self.sprites.append(column)
            self.world.append(column)

    def add_pigs(self):
        pig1 = Pig(WIDTH / 2 + 50 , 50, self.space)
        self.sprites.append(pig1)
        self.world.append(pig1)
        pig2 = Pig(WIDTH / 2 + 125 , 50, self.space)
        self.sprites.append(pig2)
        self.world.append(pig2)

        pig2 = Pig(WIDTH / 2 + 90 , 150, self.space)
        self.sprites.append(pig2)
        self.world.append(pig2)

        pig2 = Pig(WIDTH / 2 + 300 , 50, self.space)
        self.sprites.append(pig2)
        self.world.append(pig2)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
        self.update_collisions()
        self.sprites.update()

    def update_collisions(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.start_point = Point2D(x, y)
            self.end_point = Point2D(x, y)
            self.draw_line = True
            self.draw_slingshot = True
            logger.debug(f"Start Point: {self.start_point}")

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            for bird in self.birds:
                bird.on_click()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            temp_end_point = Point2D(x, y)
            distance = get_distance(self.start_point, temp_end_point)
            
            if distance > 100:
                angle = get_angle_radians(self.start_point, temp_end_point)
                x = self.start_point.x - 100 * math.cos(angle)
                y = self.start_point.y - 100 * math.sin(angle)
        
        self.end_point = Point2D(x, y)
        logger.debug(f"Dragging to: {self.end_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            self.draw_slingshot = False
            
            distance = get_distance(self.start_point, self.end_point)
            
            if distance > 100:
                angle = get_angle_radians(self.start_point, self.end_point)
                x = self.start_point.x - 100 * math.cos(angle)
                y = self.start_point.y - 100 * math.sin(angle)
                self.end_point = Point2D(x, y)
            
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)

            if self.actual_bird == "Yellow":
                bird = YellowBird(self.current_bird_image, impulse_vector, self.end_point.x, self.end_point.y, self.space)
            elif self.actual_bird == "Blue":
                bird = BlueBird(self.current_bird_image, impulse_vector, self.end_point.x, self.end_point.y, self.space, self.sprites, self.birds)
            else:
                bird = Bird(self.current_bird_image, impulse_vector, self.end_point.x, self.end_point.y, self.space)
            self.sprites.append(bird)
            self.birds.append(bird)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)
            
        if  self.draw_slingshot:
            arcade.draw_lrwh_rectangle_textured(self.start_point.x - 25, self.start_point.y - 25, 50, 50, self.slingshot_texture)
        launch_icon = arcade.load_texture("assets/img/click_left.png")
        power_icon = arcade.load_texture("assets/img/click_right.png")
        

        icon_width = 45
        icon_height = 45
        x_position = 10
        y_position_launch = HEIGHT - 60
        y_position_power = y_position_launch - icon_height - 10
        
        arcade.draw_lrwh_rectangle_textured(x_position, y_position_launch, icon_width, icon_height, launch_icon)
        arcade.draw_text("Lanzar Pájaro", x_position + icon_width + 10, y_position_launch + 15, arcade.color.BLACK, 14)
        
        arcade.draw_lrwh_rectangle_textured(x_position, y_position_power, icon_width, icon_height, power_icon)
        arcade.draw_text("Activar Power", x_position + icon_width + 10, y_position_power + 15, arcade.color.BLACK, 14)

        bird_icons = [
            ("assets/img/red-bird3.png", "Z", "Red"),
            ("assets/img/blue.png", "X", "Blue"),
            ("assets/img/yellow.png", "C", "Yellow")
        ]

        icon_width = 45
        icon_height = 45
        x_position = WIDTH - (icon_width + 450)
        
        for index, (icon_path, key, name) in enumerate(bird_icons):
            icon_texture = arcade.load_texture(icon_path)
            y_position = HEIGHT - (60 + index * (icon_height + 20))
            
            arcade.draw_lrwh_rectangle_textured(x_position, y_position, icon_width, icon_height, icon_texture)

            arcade.draw_text(f"Tecla: {key}", x_position + icon_width + 10, y_position + 15, arcade.color.BLACK, 14)
            arcade.draw_text(f"Pájaro: {name}", x_position + icon_width + 10, y_position - 5, arcade.color.BLACK, 14)
        
        

    


def main():
    app = App()
    arcade.run()


if __name__ == "__main__":
    main()