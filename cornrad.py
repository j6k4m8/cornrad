import vsketch
import math
from contextlib import contextmanager


"""
Draw lines that meet at a corner with a given radius.
"""

class CornerRadiusLineSet:
    def __init__(self, points: list[tuple[float, float, float]], debug: bool = False) -> None:
        """
        Initialize a corner radius line set.

        Args:
            points: List of (x, y, r) tuples, where (x, y) are coordinates and r is the radius
            debug: Whether to draw debug elements
        """
        self.points = points
        self.debug = debug

    def add_point(self, x: float, y: float, r: float) -> None:
        """Add a point to the line set."""
        self.points.append((x, y, r))

    def get_points(self):
        """Return the list of points."""
        return self.points

    @contextmanager
    def _debug_draw(self, vsk, stroke_value: int):
        """Context manager for debug drawing."""
        original_stroke = 1
        if self.debug:
            vsk.stroke(stroke_value)
            yield
            vsk.stroke(original_stroke)
        else:
            yield

    def draw(self, vsk: vsketch.Vsketch) -> None:
        """Draw the line set with rounded corners."""
        # Draw debug points if enabled
        if self.debug:
            for point in self.points:
                x, y, r = point
                with self._debug_draw(vsk, 2):
                    vsk.circle(x, y, 0.1)

        # Need at least 3 points to form a corner
        if len(self.points) < 3:
            return

        # Draw the actual lines with rounded corners
        for i in range(len(self.points) - 2):
            # Get three consecutive points
            Ax, Ay, _r1 = self.points[i]
            gx, gy, radius = self.points[i + 1]  # Corner point with radius
            Bx, By, _r2 = self.points[i + 2]

            # Draw original corner lines for reference in debug mode
            if self.debug:
                with self._debug_draw(vsk, 2):
                    vsk.line(Ax, Ay, gx, gy)
                    vsk.line(gx, gy, Bx, By)

            # Calculate vectors
            Ag_vector = (gx - Ax, gy - Ay)
            gB_vector = (Bx - gx, By - gy)

            # Normalize vectors
            Ag_length = math.sqrt(Ag_vector[0]**2 + Ag_vector[1]**2)
            gB_length = math.sqrt(gB_vector[0]**2 + gB_vector[1]**2)

            if Ag_length < 1e-10 or gB_length < 1e-10:
                # Skip if points are too close
                continue

            Ag_unit = (Ag_vector[0] / Ag_length, Ag_vector[1] / Ag_length)
            gB_unit = (gB_vector[0] / gB_length, gB_vector[1] / gB_length)

            # Calculate the angle between the vectors (using reversed gB vector)
            # We're looking for the interior angle between the lines
            neg_gB_unit = (-gB_unit[0], -gB_unit[1])
            dot_product = Ag_unit[0] * neg_gB_unit[0] + Ag_unit[1] * neg_gB_unit[1]

            # Clamp dot product to avoid numerical issues
            dot_product = max(-1.0, min(1.0, dot_product))

            # Calculate interior angle between the lines
            interior_angle = math.acos(dot_product)

            # Skip if angle is too small or too large
            if interior_angle < 1e-10 or interior_angle > math.pi - 1e-10:
                continue

            # Calculate distance from corner to tangent point
            tangent_distance = radius / math.tan(interior_angle / 2)

            # Find tangent points
            ax = gx - tangent_distance * Ag_unit[0]
            ay = gy - tangent_distance * Ag_unit[1]

            bx = gx + tangent_distance * gB_unit[0]
            by = gy + tangent_distance * gB_unit[1]

            # Calculate the bisector vector
            # Sum of unit vectors pointing away from g
            bisector_x = -Ag_unit[0] + gB_unit[0]  # Note: negative Ag_unit points away from g
            bisector_y = -Ag_unit[1] + gB_unit[1]

            bisector_length = math.sqrt(bisector_x**2 + bisector_y**2)

            if bisector_length < 1e-10:
                # The segments are almost collinear, use perpendicular vector
                bisector_x = Ag_unit[1]  # Perpendicular to Ag_unit
                bisector_y = -Ag_unit[0]
                bisector_length = 1.0

            bisector_unit = (bisector_x / bisector_length, bisector_y / bisector_length)

            # Calculate center of the circle that's tangent to both lines
            center_distance = radius / math.sin(interior_angle / 2)

            # Place the center along the bisector
            # The center should be on the side that makes an acute angle with both lines
            cx = gx + center_distance * bisector_unit[0]
            cy = gy + center_distance * bisector_unit[1]

            # Draw the circle in debug mode
            if self.debug:
                with self._debug_draw(vsk, 2):
                    vsk.circle(cx, cy, radius)

                # Draw tangent points
                with self._debug_draw(vsk, 3):
                    vsk.circle(ax, ay, 0.05)
                    vsk.circle(bx, by, 0.05)

                # Draw bisector
                with self._debug_draw(vsk, 3):
                    debug_bisector_length = 0.5
                    vsk.line(gx, gy,
                             gx + debug_bisector_length * bisector_unit[0],
                             gy + debug_bisector_length * bisector_unit[1])

            # Calculate vectors from center to tangent points
            ca_vector = (ax - cx, ay - cy)
            cb_vector = (bx - cx, by - cy)

            # Calculate arc angles in radians
            start_angle = math.atan2(ca_vector[1], ca_vector[0])
            end_angle = math.atan2(cb_vector[1], cb_vector[0])

            # Determine which arc to draw (we want the one inside the corner)
            # This is a bit tricky but we can use the cross product
            cross_z = ca_vector[0] * cb_vector[1] - ca_vector[1] * cb_vector[0]

            # Ensure we're drawing the correct arc segment
            if cross_z < 0:
                # If cross product is negative, swap angles to get the smaller arc
                start_angle, end_angle = end_angle, start_angle

            # If the angle difference is more than π, we have the wrong arc
            if abs(end_angle - start_angle) > math.pi:
                if end_angle > start_angle:
                    end_angle -= 2 * math.pi
                else:
                    end_angle += 2 * math.pi

            # Draw the connecting lines and arc
            vsk.line(Ax, Ay, ax, ay)
            vsk.arc(cx, cy, 2*radius, -2*radius, start_angle, end_angle, mode="center")
            # if last point, draw line to next point
            if i == len(self.points) - 3:
                vsk.line(bx, by, Bx, By)

            # To be cheeky, set the NEXT point to be the b tangent point (to
            # avoid drawing a line to the next point)
            if len(self.points) > 1:
                self.points[i + 1] = (bx, by, self.points[i + 1][2])
