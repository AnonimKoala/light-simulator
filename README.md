# light-simulator

A Python application that simulates the behavior of light in a void, interacting with various optical objects such as
mirrors and lenses.

## Features

- Simulates ray tracing and light interactions with optical objects
- Interactive scene manipulation: move, rotate, and zoom objects.
- Easily extendable for new optical components.

## Requirements

- Python 3.13.3
- [PyQt6](https://pypi.org/project/PyQt6/)
- [sympy](https://pypi.org/project/sympy/)

## Controls

| Action      | Key / Mouse  | Description                                            |
|-------------|--------------|--------------------------------------------------------|
| Move item   | `M`          | Press to enable moving mode; press again to disable.   |
| Rotate item | `R`          | Press to enable rotation mode; press again to disable. |
| Zoom in/out | Mouse Scroll | Scroll to zoom the view in or out.                     |

## Usage

### Adding Objects to the Scene

To add optical objects, modify the `main()` function in `main.py` as follows:

#### Add a Mirror

```python
Mirror(0, 0, 20, 200, view)
```

- **Parameters:**
    - `x`: X-coordinate
    - `y`: Y-coordinate
    - `width`: Width of the mirror
    - `height`: Height of the mirror
    - `view`: The scene's view object

#### Add a Lens

```python
Len(0, 10, 200, view, -30, 30)
```

- **Parameters:**
    - `x`: X-coordinate
    - `y`: Y-coordinate
    - `height`: Height of the lens
    - `view`: The scene's view object
    - `left_radius`: Radius of curvature for the left side
    - `right_radius`: Radius of curvature for the right side
    - `width` (optional): Width of the lens (must be equal or greater than sum of absolute values of `left_radius` and `right_radius`)

## Getting Started

1. Install dependencies:
   ```bash
   pip install pyqt6 sympy
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## License

This code is provided for personal or internal use only. Modification, redistribution, or commercial use is strictly prohibited. 

