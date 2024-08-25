import math
import arcade
import pymunk
from game_logic import ImpulseVector


class Bird(arcade.Sprite):
    """
    Bird class. This represents an angry bird. All the physics is handled by Pymunk,
    the init method only set some initial properties
    """
    def __init__(
        self,
        image_path: str,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 100,
        power_multiplier: float = 50,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)
        # body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        impulse = min(max_impulse, impulse_vector.impulse) * power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        # apply impulse
        body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))
        # shape
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        self.has_boosted = True
        space.add(body, shape)

        self.body = body
        self.shape = shape

    def update(self):
        """
        Update the position of the bird sprite based on the physics body position
        """
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle

    def on_click(self):
        if not self.has_boosted:
            self.has_boosted = True

class YellowBird(Bird):
    def __init__(self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, 
        y: float, 
        space: pymunk.Space, 
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50, 
        elasticity: float = 0.8,
        friction: float = 1, 
        collision_layer: int = 0, 
        impulse: float = 2.0
    ):
        super().__init__(image_path, 
            impulse_vector, 
            x, 
            y, 
            space, 
            mass, 
            radius, 
            max_impulse, 
            power_multiplier, 
            elasticity, 
            friction, 
            collision_layer)
        self.impulse = impulse
        self.has_boosted = False

    def on_click(self):
        if not self.has_boosted:
            #ya que no son 2 puntos solo cambiar el impulso no utilize las funciones del game logic
            impulse_final = self.impulse * self.body.velocity.length
            impulse_vector = pymunk.Vec2d(impulse_final, 0).rotated(self.body.angle)
            self.body.apply_impulse_at_local_point(impulse_vector)
            self.has_boosted = True

class BlueBird(Bird):
    def __init__(self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, y: float, 
        space: pymunk.Space, 
        sprites_list: arcade.SpriteList,
        birds_list: arcade.SpriteList,
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50, 
        elasticity: float = 0.8, 
        friction: float = 1, 
        collision_layer: int = 0, 
        ):
        super().__init__(image_path, 
        impulse_vector, 
        x, 
        y, 
        space, 
        mass, 
        radius, 
        max_impulse, 
        power_multiplier, 
        elasticity, 
        friction, 
        collision_layer,
        )

        self.sprites_list = sprites_list  
        self.birds_list = birds_list
        self.bird_split = False

    def on_click(self):
        if not self.bird_split:
            new_angles = [self.body.angle + math.radians(20),
                      self.body.angle- math.radians(10),
                      self.body.angle - math.radians(40)]

            for angle in new_angles:
                velocity = self.body.velocity.rotated(angle - self.body.angle)
                new_bird = Bird(
                    self.texture.name,  
                    ImpulseVector(velocity.length, angle),
                    self.body.position.x,
                    self.body.position.y,
                    self.shape.space,
                    max_impulse=velocity.length,
                )

                new_bird.body.velocity = velocity

                self.sprites_list.append(new_bird)
                self.birds_list.append(new_bird)

            self.remove_from_sprite_lists()
            self.shape.space.remove(self.shape, self.body)
            self.bird_split = True  


class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 0.4,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig_failed.png", 0.1)
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class PassiveObject(arcade.Sprite):
    """
    Passive object that can interact with other objects.
    """
    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

        moment = pymunk.moment_for_box(mass, (self.width, self.height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Column(PassiveObject):
    def __init__(self, x, y, space):
        super().__init__("assets/img/column.png", x, y, space)

class Beam(PassiveObject):
    def __init__(self, x, y, space):
        super().__init__("assets/img/beam.png", x, y, space)

class StaticObject(arcade.Sprite):
    def __init__(
            self,
            image_path: str,
            x: float,
            y: float,
            space: pymunk.Space,
            mass: float = 2,
            elasticity: float = 0.8,
            friction: float = 1,
            collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

