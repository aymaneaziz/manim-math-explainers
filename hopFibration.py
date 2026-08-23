from manim import *
import numpy as np

config.background_color = "#0a0a10"


def hopf_xyz(theta, phi, t, eps=0.16):
    z1 = np.exp(1j * t) * np.cos(theta / 2)
    z2 = np.exp(1j * (t + phi)) * np.sin(theta / 2)
    a, b, c, d = z1.real, z1.imag, z2.real, z2.imag
    denom = 1 - d
    if abs(denom) < eps:
        denom = eps if denom >= 0 else -eps
    return np.array([a / denom, b / denom, c / denom])


def base_point_xyz(theta, phi, radius=1.0):
    return radius * np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )


RING_THETAS = [0.75, PI / 2, 2.35]  # three latitude rings on S^2
RING_COLORS = [BLUE, YELLOW, RED]  # one color per ring
N_CIRCLES_PER_RING = 12  # fibers sampled around each ring


class MathExplanation(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-50 * DEGREES, zoom=0.9)
        self.intro()
        self.show_formula()
        self.single_fiber_demo()
        self.build_torus_of_circles()
        self.nest_more_tori()
        self.connect_to_base_sphere()
        self.outro()

    # ------------------------------------------------------------------
    def intro(self):
        title = Text("The Hopf Fibration", font_size=48, weight=BOLD)
        subtitle = Text(
            "every point of a sphere is secretly a circle", font_size=26, color=GREY_B
        )
        subtitle.next_to(title, DOWN, buff=0.4)
        group = VGroup(title, subtitle)

        self.add_fixed_in_frame_mobjects(group)
        group.move_to(ORIGIN)
        self.play(Write(title), run_time=1.8)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1.4)
        self.play(FadeOut(group))

    # ------------------------------------------------------------------
    def show_formula(self):
        heading = Text("The map itself", font_size=32).to_edge(UP)
        formula = MathTex(
            r"h : S^3 \to S^2",
            r"\qquad",
            r"h(z_1, z_2) = \big(2 z_1 \bar z_2,\ |z_1|^2 - |z_2|^2\big)",
            font_size=40,
        ).next_to(heading, DOWN, buff=0.6)
        note = Text(
            "Each point of S² is hit by an entire circle's worth of points in S³",
            font_size=24,
            color=GREY_B,
        ).next_to(formula, DOWN, buff=0.5)

        group = VGroup(heading, formula, note)
        self.add_fixed_in_frame_mobjects(group)
        group.move_to(ORIGIN)

        self.play(Write(heading))
        self.play(Write(formula))
        self.wait(1)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(group))

    # ------------------------------------------------------------------
    def single_fiber_demo(self):
        heading = Text("Take one point on the sphere...", font_size=30).to_edge(UP)
        self.add_fixed_in_frame_mobjects(heading)
        self.play(Write(heading))

        base_sphere = Sphere(
            radius=1.0,
            resolution=(24, 24),
            fill_opacity=0.12,
            checkerboard_colors=[BLUE_E, BLUE_E],
        )
        base_sphere.set_stroke(width=0.3, color=GREY_B, opacity=0.3)
        base_sphere.shift(LEFT * 3.5)

        theta0, phi0 = PI / 2, 0.6
        marker = Dot3D(
            base_point_xyz(theta0, phi0) + LEFT * 3.5, radius=0.08, color=YELLOW
        )

        self.play(Create(base_sphere), run_time=1.5)
        self.play(FadeIn(marker, scale=0.5))
        self.wait(1)

        heading2 = Text("...its preimage is a full circle in 3D", font_size=30).to_edge(
            UP
        )
        self.play(ReplacementTransform(heading, heading2))

        fiber = ParametricFunction(
            lambda t: hopf_xyz(theta0, phi0, t) * 1.6 + RIGHT * 2.0,
            t_range=[0, TAU],
            color=YELLOW,
            stroke_width=4,
        )
        self.play(Create(fiber), run_time=2.5)
        self.wait(1.5)

        self.play(
            FadeOut(base_sphere), FadeOut(marker), FadeOut(fiber), FadeOut(heading2)
        )
        self.wait(0.3)

    # ------------------------------------------------------------------
    def build_torus_of_circles(self):
        heading = Text("Sweep the point around one latitude...", font_size=28).to_edge(
            UP
        )
        self.add_fixed_in_frame_mobjects(heading)
        self.play(Write(heading))

        theta = RING_THETAS[1]
        circles = VGroup()
        for i in range(N_CIRCLES_PER_RING):
            phi = TAU * i / N_CIRCLES_PER_RING
            hue_color = interpolate_color(BLUE, RED, i / N_CIRCLES_PER_RING)
            curve = ParametricFunction(
                lambda t, ph=phi: hopf_xyz(theta, ph, t) * 1.6,
                t_range=[0, TAU],
                color=hue_color,
                stroke_width=3,
            )
            circles.add(curve)

        self.begin_ambient_camera_rotation(rate=0.15)

        self.play(
            LaggedStart(*[Create(c) for c in circles], lag_ratio=0.15), run_time=6
        )
        self.wait(1)

        note = Text(
            "...and every circle links every other circle, exactly once",
            font_size=24,
            color=GREY_B,
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(note)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(3)

        self.play(FadeOut(note), FadeOut(heading))
        self.torus_ref = circles
        self.wait(0.3)

    # ------------------------------------------------------------------
    def nest_more_tori(self):
        heading = Text(
            "Other latitudes give nested tori of circles", font_size=28
        ).to_edge(UP)
        self.add_fixed_in_frame_mobjects(heading)
        self.play(Write(heading))

        extra_groups = VGroup()
        for theta, color in [
            (RING_THETAS[0], RING_COLORS[0]),
            (RING_THETAS[2], RING_COLORS[2]),
        ]:
            ring = VGroup()
            for i in range(N_CIRCLES_PER_RING):
                phi = TAU * i / N_CIRCLES_PER_RING
                curve = ParametricFunction(
                    lambda t, th=theta, ph=phi: hopf_xyz(th, ph, t) * 1.6,
                    t_range=[0, TAU],
                    color=color,
                    stroke_width=3,
                )
                ring.add(curve)
            extra_groups.add(ring)

        self.play(
            LaggedStart(*[Create(c) for c in extra_groups[0]], lag_ratio=0.1),
            run_time=4,
        )
        self.play(
            LaggedStart(*[Create(c) for c in extra_groups[1]], lag_ratio=0.1),
            run_time=4,
        )
        self.wait(2)

        self.play(FadeOut(heading))
        self.all_tori_ref = VGroup(self.torus_ref, extra_groups)
        self.wait(0.5)

    # ------------------------------------------------------------------
    def connect_to_base_sphere(self):
        heading = Text("Color = latitude on the base sphere", font_size=28).to_edge(UP)
        self.add_fixed_in_frame_mobjects(heading)
        self.play(Write(heading))

        mini_sphere = Sphere(
            radius=0.8,
            resolution=(20, 20),
            fill_opacity=0.15,
            checkerboard_colors=[GREY_D, GREY_D],
        )
        mini_sphere.set_stroke(width=0.2, opacity=0.2)
        mini_sphere.move_to(LEFT * 4.2 + UP * 1.8)

        ring_curves = VGroup()
        for theta, color in zip(RING_THETAS, RING_COLORS):
            ring = ParametricFunction(
                lambda phi, th=theta: base_point_xyz(th, phi, radius=0.8)
                + LEFT * 4.2
                + UP * 1.8,
                t_range=[0, TAU],
                color=color,
                stroke_width=5,
            )
            ring_curves.add(ring)

        self.play(FadeIn(mini_sphere))
        self.play(
            LaggedStart(*[Create(r) for r in ring_curves], lag_ratio=0.3), run_time=2.5
        )
        self.wait(3)

        self.play(FadeOut(heading), FadeOut(mini_sphere), FadeOut(ring_curves))
        self.stop_ambient_camera_rotation()
        self.wait(0.3)

    # ------------------------------------------------------------------
    def outro(self):
        self.play(FadeOut(self.all_tori_ref), run_time=1.2)
        self.move_camera(phi=70 * DEGREES, theta=-50 * DEGREES, zoom=0.9, run_time=0.5)

        closing = Text(
            "A 3-sphere is woven, point by point,\nfrom linked circles.",
            font_size=34,
            weight=BOLD,
            line_spacing=1.2,
        )
        self.add_fixed_in_frame_mobjects(closing)
        closing.move_to(ORIGIN)
        self.play(Write(closing), run_time=2.2)
        self.wait(1.8)
        self.play(FadeOut(closing))
        self.wait(0.3)
