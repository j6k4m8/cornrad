# cornrad
Corner radii in vsketch

<img width="337" alt="image" src="https://github.com/user-attachments/assets/6e126b85-a1be-45a4-847f-a01e70ef6163" />

<img width="283" alt="image" src="https://github.com/user-attachments/assets/dbb287ed-dd6f-4e3c-a6e5-ceae064cd151" />

## more reading

https://github.com/abey79/vsketch/discussions/499

## example usage

```python
import vsketch
from cornrad import CornerRadiusLineSet


class CornerRadiusSketch(vsketch.SketchClass):
    # Sketch parameters:
    radius = vsketch.Param(0.5, step=0.10)
    debug = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("6x10in", landscape=False)
        vsk.scale("in")

        CornerRadiusLineSet(
            [
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
                (vsk.random(0, 5), vsk.random(0, 5), self.radius),
            ],
            debug=self.debug,
        ).draw(vsk)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CornerRadiusSketch.display()
```
