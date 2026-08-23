from manim import *
import numpy as np

config.background_color = "#0e0e12"

HARMONICS = [1, 3, 5, 7, 9, 11, 13]  # odd harmonics used in the epicycle demo
VECTOR_COLORS = [BLUE, TEAL, GREEN, YELLOW, ORANGE, RED, PURPLE]


def square_wave(x):
    return 1.0 if np.sin(x) >= 0 else -1.0


def partial_sum(x, n_terms):
    total = 0.0
    for k in range(n_terms):
        n = 2 * k + 1
        total += np.sin(n * x) / n
    return (4 / PI) * total


class MathExplanation(MovingCameraScene):
    def construct(self):
        self.intro()
        self.show_target_and_formula()
        self.build_up_partial_sums()
        self.epicycles()
        self.gibbs_phenomenon()
        self.outro()

    # ------------------------------------------------------------------
    def intro(self):
        title = Text("Visualizing a Fourier Square Wave", font_size=48, weight=BOLD)
        subtitle = Text(
            "how spinning circles build a square", font_size=26, color=GREY_B
        )
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=1.8)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1.2)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ------------------------------------------------------------------
    def show_target_and_formula(self):
        heading = Text("The target waveform", font_size=32).to_edge(UP)

        axes = Axes(
            x_range=[-TAU, TAU, PI],
            y_range=[-1.6, 1.6, 1],
            x_length=9,
            y_length=3.4,
            axis_config={"color": GREY_B, "include_tip": False},
        ).shift(DOWN * 0.4)

        wave = axes.plot(
            square_wave,
            x_range=[-TAU, TAU],
            color=WHITE,
            stroke_width=4,
            use_smoothing=False,
        )

        self.play(Write(heading))
        self.play(Create(axes))
        self.play(Create(wave), run_time=2)
        self.wait(1)

        formula = MathTex(
            r"f(x)",
            "=",
            r"\frac{4}{\pi}",
            r"\sum_{k=0}^{\infty}",
            r"\frac{\sin\big((2k+1)x\big)}{2k+1}",
            font_size=44,
        ).set_color_by_tex_to_color_map({r"\frac{4}{\pi}": YELLOW})
        formula.next_to(axes, DOWN, buff=0.5)

        self.play(Write(formula))
        self.wait(2)

        self.play(FadeOut(heading), FadeOut(formula))
        self.axes_ref = axes
        self.wave_ref = wave

    # ------------------------------------------------------------------
    def build_up_partial_sums(self):
        axes = self.axes_ref
        heading = Text("Adding one harmonic at a time...", font_size=30).to_edge(UP)
        self.play(Write(heading))

        term_counts = [1, 2, 3, 5, 8, 16]  # number of odd harmonics included
        highest = [2 * n - 1 for n in term_counts]

        counter = Text(f"harmonics up to n = {highest[0]}", font_size=26, color=TEAL)
        counter.next_to(axes, DOWN, buff=0.5)

        approx = axes.plot(
            lambda x: partial_sum(x, term_counts[0]),
            x_range=[-TAU, TAU, 0.02],
            color=YELLOW,
            stroke_width=3,
        )

        self.play(Create(approx), FadeIn(counter))
        self.wait(0.8)

        for n_terms, n_high in zip(term_counts[1:], highest[1:]):
            new_approx = axes.plot(
                lambda x, n=n_terms: partial_sum(x, n),
                x_range=[-TAU, TAU, 0.02],
                color=YELLOW,
                stroke_width=3,
            )
            new_counter = Text(
                f"harmonics up to n = {n_high}", font_size=26, color=TEAL
            )
            new_counter.move_to(counter)

            self.play(
                Transform(approx, new_approx),
                Transform(counter, new_counter),
                run_time=1.1,
            )
            self.wait(0.5)

        self.wait(1)
        self.play(
            FadeOut(heading),
            FadeOut(counter),
            FadeOut(approx),
            FadeOut(axes),
            FadeOut(self.wave_ref),
        )

    # ------------------------------------------------------------------
    def epicycles(self):
        heading = Text(
            "Where it actually comes from: spinning vectors", font_size=28
        ).to_edge(UP)
        self.play(Write(heading))

        left_axes = (
            Axes(
                x_range=[-1.8, 1.8, 0.9],
                y_range=[-1.8, 1.8, 0.9],
                x_length=4.4,
                y_length=4.4,
                axis_config={"color": GREY_D, "include_tip": False},
            )
            .to_edge(LEFT, buff=0.8)
            .shift(DOWN * 0.3)
        )

        right_axes = (
            Axes(
                x_range=[0, 4 * PI],
                y_range=[-1.8, 1.8, 0.9],
                x_length=7.2,
                y_length=4.4,
                axis_config={"color": GREY_D, "include_tip": False},
            )
            .to_edge(RIGHT, buff=0.6)
            .shift(DOWN * 0.3)
        )

        self.play(Create(left_axes), Create(right_axes))

        t = ValueTracker(0)
        unit = (left_axes.c2p(1, 0) - left_axes.c2p(0, 0))[
            0
        ]  # scene units per data unit

        def cumulative_points(t_val):
            pts = [0j]
            z = 0j
            for n in HARMONICS:
                r = 4 / (PI * n)
                z += r * np.exp(1j * n * t_val)
                pts.append(z)
            return pts

        def vectors_updater():
            pts = cumulative_points(t.get_value())
            group = VGroup()
            for i in range(len(HARMONICS)):
                start = left_axes.c2p(pts[i].real, pts[i].imag)
                end = left_axes.c2p(pts[i + 1].real, pts[i + 1].imag)
                arrow = Line(
                    start,
                    end,
                    color=VECTOR_COLORS[i % len(VECTOR_COLORS)],
                    stroke_width=3,
                )
                group.add(arrow)
            return group

        def circles_updater():
            pts = cumulative_points(t.get_value())
            group = VGroup()
            for i, n in enumerate(HARMONICS):
                r = 4 / (PI * n)
                center = left_axes.c2p(pts[i].real, pts[i].imag)
                circ = Circle(
                    radius=r * unit,
                    color=VECTOR_COLORS[i % len(VECTOR_COLORS)],
                    stroke_width=1,
                    stroke_opacity=0.35,
                )
                circ.move_to(center)
                group.add(circ)
            return group

        vectors = always_redraw(vectors_updater)
        circles = always_redraw(circles_updater)

        tip_dot = always_redraw(
            lambda: Dot(
                left_axes.c2p(
                    cumulative_points(t.get_value())[-1].real,
                    cumulative_points(t.get_value())[-1].imag,
                ),
                radius=0.06,
                color=WHITE,
            )
        )

        right_dot = always_redraw(
            lambda: Dot(
                right_axes.c2p(
                    t.get_value(), cumulative_points(t.get_value())[-1].imag
                ),
                radius=0.06,
                color=WHITE,
            )
        )

        connector = always_redraw(
            lambda: DashedLine(
                left_axes.c2p(
                    cumulative_points(t.get_value())[-1].real,
                    cumulative_points(t.get_value())[-1].imag,
                ),
                right_axes.c2p(
                    t.get_value(), cumulative_points(t.get_value())[-1].imag
                ),
                color=GREY_B,
                stroke_width=1,
                dash_length=0.08,
            )
        )

        trace = TracedPath(right_dot.get_center, stroke_color=YELLOW, stroke_width=4)

        self.play(FadeIn(circles), FadeIn(vectors), FadeIn(tip_dot))
        self.add(connector, trace, right_dot)
        self.wait(0.5)

        self.play(t.animate.set_value(4 * PI), run_time=12, rate_func=linear)
        self.wait(1)

        self.play(
            FadeOut(circles),
            FadeOut(vectors),
            FadeOut(tip_dot),
            FadeOut(connector),
            FadeOut(right_dot),
            FadeOut(trace),
            FadeOut(left_axes),
            FadeOut(right_axes),
            FadeOut(heading),
        )
        self.wait(0.3)

    # ------------------------------------------------------------------
    def gibbs_phenomenon(self):
        heading = Text("The Gibbs phenomenon", font_size=32).to_edge(UP)
        subheading = Text(
            "more harmonics never erase the overshoot", font_size=24, color=GREY_B
        )
        subheading.next_to(heading, DOWN, buff=0.25)

        axes = Axes(
            x_range=[-TAU, TAU, PI],
            y_range=[-1.6, 1.6, 1],
            x_length=9,
            y_length=4,
            axis_config={"color": GREY_B, "include_tip": False},
        ).shift(DOWN * 0.5)

        target = axes.plot(
            square_wave,
            x_range=[-TAU, TAU],
            color=WHITE,
            stroke_width=3,
            use_smoothing=False,
        )

        approx31 = axes.plot(
            lambda x: partial_sum(x, 16),
            x_range=[-TAU, TAU, 0.01],
            color=YELLOW,
            stroke_width=3,
        )

        overshoot_line = DashedLine(
            axes.c2p(-TAU, 1.09), axes.c2p(TAU, 1.09), color=RED, stroke_width=2
        )
        overshoot_label = Text("~9% overshoot, always", font_size=22, color=RED)
        overshoot_label.next_to(overshoot_line, UP, buff=0.15).shift(RIGHT * 2)

        self.play(Write(heading), FadeIn(subheading))
        self.play(Create(axes))
        self.play(Create(target))
        self.play(Create(approx31), run_time=1.5)
        self.wait(0.5)
        self.play(Create(overshoot_line), FadeIn(overshoot_label))
        self.wait(1)

        jump_point = axes.c2p(PI, 1.09)
        self.play(self.camera.frame.animate.scale(0.28).move_to(jump_point), run_time=2)
        self.wait(2)
        self.play(
            self.camera.frame.animate.scale(1 / 0.28).move_to(ORIGIN), run_time=1.5
        )
        self.wait(0.5)

        self.play(
            FadeOut(heading),
            FadeOut(subheading),
            FadeOut(axes),
            FadeOut(target),
            FadeOut(approx31),
            FadeOut(overshoot_line),
            FadeOut(overshoot_label),
        )

    # ------------------------------------------------------------------
    def outro(self):
        closing = Text(
            "Every sharp edge is built from infinitely many\nsmooth, spinning circles.",
            font_size=34,
            weight=BOLD,
            line_spacing=1.2,
        )
        self.play(Write(closing), run_time=2.2)
        self.wait(1.8)
        self.play(FadeOut(closing))
        self.wait(0.3)
