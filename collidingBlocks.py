"""
Galperin's Colliding Blocks Compute Pi
---------------------------------------
Manim Community Edition v0.18+

A small block (m1 = 1 kg) sits between a wall and a large block
(m2 = 100 kg). The large block slides left and strikes the small one.
Every collision -- block-vs-wall and block-vs-block -- is a perfectly
elastic collision. If you count every collision that happens before
Block 2 permanently reverses direction and escapes to the right,
you get exactly 31 collisions -- the first two digits of pi.
(In general the count is floor(pi * sqrt(m2 / m1)).)

No LaTeX is used anywhere -- only Text and basic geometric Mobjects.
"""

from manim import *

# ----------------------------------------------------------------------
# Physics parameters
# ----------------------------------------------------------------------
M1 = 1.0  # mass of the small block (kg)
M2 = 100.0  # mass of the large block (kg)

WALL_X = -6.3  # x-position of the wall (scene units)
FLOOR_Y = -2.6  # y-position of the floor

BLOCK1_W, BLOCK1_H = 0.55, 0.55  # small block size
BLOCK2_W, BLOCK2_H = 1.6, 1.6  # large block size

BLOCK1_L0 = -5.0  # initial LEFT edge x of block 1
BLOCK2_L0 = 1.4  # initial LEFT edge x of block 2

V1_0 = 0.0  # block 1 starts at rest
V2_0 = -3.0  # block 2 starts moving left toward block 1

SUB_DT = 0.00025  # physics sub-step (small -> never misses a collision)
MAX_SIM_TIME = 14.0  # seconds of real animation time to run the sim


def elastic_collision(v1, v2, m1, m2):
    """Exact 1D elastic collision formulas (as specified)."""
    v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
    v2_final = ((2 * m1) * v1 + (m2 - m1) * v2) / (m1 + m2)
    return v1_final, v2_final


class MathExplanation(Scene):
    def construct(self):
        self.setup_scene()
        self.intro()
        self.run_simulation()
        self.show_final_annotation()

    # --------------------------------------------------------------
    def setup_scene(self):
        # Floor
        floor = Line(
            LEFT * 7 + UP * FLOOR_Y,
            RIGHT * 7 + UP * FLOOR_Y,
            color=GREY_B,
            stroke_width=4,
        )

        # Wall (vertical line with a hatch pattern to read as "solid wall")
        wall = Line(
            RIGHT * WALL_X + UP * (FLOOR_Y - 0.1),
            RIGHT * WALL_X + UP * (FLOOR_Y + 4.2),
            color=GREY_B,
            stroke_width=8,
        )
        hatches = VGroup()
        for i in range(9):
            y = FLOOR_Y + 0.3 + i * 0.45
            hatches.add(
                Line(
                    [WALL_X, y, 0],
                    [WALL_X - 0.3, y - 0.3, 0],
                    color=GREY_D,
                    stroke_width=2,
                )
            )

        # Block 1 (small, yellow, 1 kg)
        block1 = Rectangle(
            width=BLOCK1_W,
            height=BLOCK1_H,
            fill_color=YELLOW,
            fill_opacity=1,
            stroke_color=WHITE,
            stroke_width=2,
        )
        block1.move_to([BLOCK1_L0 + BLOCK1_W / 2, FLOOR_Y + BLOCK1_H / 2, 0])
        label1 = Text("1 kg", font_size=18, color=BLACK).move_to(block1)

        # Block 2 (large, blue, 100 kg)
        block2 = Rectangle(
            width=BLOCK2_W,
            height=BLOCK2_H,
            fill_color=BLUE,
            fill_opacity=1,
            stroke_color=WHITE,
            stroke_width=2,
        )
        block2.move_to([BLOCK2_L0 + BLOCK2_W / 2, FLOOR_Y + BLOCK2_H / 2, 0])
        label2 = Text("100 kg", font_size=22, color=WHITE).move_to(block2)

        self.floor = floor
        self.wall = wall
        self.hatches = hatches
        self.block1 = block1
        self.block2 = block2
        self.label1 = label1
        self.label2 = label2

        self.play(Create(floor), Create(wall), Create(hatches), run_time=1.2)
        self.play(
            FadeIn(block1, shift=UP * 0.2),
            FadeIn(label1),
            FadeIn(block2, shift=UP * 0.2),
            FadeIn(label2),
            run_time=1.2,
        )
        self.wait(0.4)

    # --------------------------------------------------------------
    def intro(self):
        title = Text(
            "Galperin's Colliding Blocks Compute Pi", font_size=34, weight=BOLD
        )
        title.to_edge(UP, buff=0.3)
        note = Text(
            "Every collision below is perfectly elastic. Watch the counter.",
            font_size=22,
            color=GREY_B,
        )
        note.next_to(title, DOWN, buff=0.2)

        self.play(Write(title), run_time=1.3)
        self.play(FadeIn(note, shift=UP * 0.15))
        self.wait(1.2)
        self.play(FadeOut(note))
        self.title_ref = title

    # --------------------------------------------------------------
    def run_simulation(self):
        # Collision counter, shown live at the top under the title.
        collision_count = ValueTracker(0)

        counter_label = always_redraw(
            lambda: Text(
                f"Collisions: {int(collision_count.get_value())}",
                font_size=30,
                color=WHITE,
            ).next_to(self.title_ref, DOWN, buff=0.25)
        )
        self.add(counter_label)

        # Mutable physics state, captured by the updater closure.
        state = {
            "L1": BLOCK1_L0,
            "L2": BLOCK2_L0,
            "v1": V1_0,
            "v2": V2_0,
            "done": False,
        }

        def physics_updater(mob, dt):
            if state["done"] or dt <= 0:
                return

            steps = max(1, int(dt / SUB_DT))
            step_dt = dt / steps

            for _ in range(steps):
                state["L1"] += state["v1"] * step_dt
                state["L2"] += state["v2"] * step_dt

                # Collision with the wall
                if state["L1"] <= WALL_X:
                    state["L1"] = WALL_X
                    state["v1"] = -state["v1"]
                    collision_count.set_value(collision_count.get_value() + 1)

                # Collision between block 1 and block 2
                block1_right = state["L1"] + BLOCK1_W
                if block1_right >= state["L2"]:
                    state["L2"] = block1_right
                    new_v1, new_v2 = elastic_collision(state["v1"], state["v2"], M1, M2)
                    state["v1"], state["v2"] = new_v1, new_v2
                    collision_count.set_value(collision_count.get_value() + 1)

                # Termination: block 2 is moving right, faster than block 1,
                # and block 1 is not moving toward the wall -- no further
                # collisions are possible from here on.
                if state["v2"] > 0 and state["v2"] >= state["v1"] and state["v1"] >= 0:
                    state["done"] = True
                    break

            # Sync the visible rectangles to the physics state
            self.block1.move_to([state["L1"] + BLOCK1_W / 2, FLOOR_Y + BLOCK1_H / 2, 0])
            self.label1.move_to(self.block1)
            self.block2.move_to([state["L2"] + BLOCK2_W / 2, FLOOR_Y + BLOCK2_H / 2, 0])
            self.label2.move_to(self.block2)

        self.block1.add_updater(physics_updater)
        self.wait(MAX_SIM_TIME)
        self.block1.remove_updater(physics_updater)

        self.final_count = int(collision_count.get_value())
        self.counter_label_ref = counter_label

    # --------------------------------------------------------------
    def show_final_annotation(self):
        result = Text(
            f"Total Collisions = {self.final_count} (First two digits of Pi!)",
            font_size=30,
            color=YELLOW,
            weight=BOLD,
        )
        result.to_edge(DOWN, buff=0.6)

        formula_note = Text(
            "Collisions = floor( pi * sqrt(m2 / m1) )", font_size=22, color=GREY_B
        )
        formula_note.next_to(result, UP, buff=0.25)

        self.play(FadeIn(formula_note, shift=UP * 0.15))
        self.play(Write(result), run_time=1.5)
        self.wait(3)
