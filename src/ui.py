from collections import defaultdict
from collections.abc import Mapping


# Why? Because inlining the render method is ugly with `lambda` and I wanted some deco
def frame_definition(frame_renderer):
    return Frame(frame_renderer)

class Frame():
    def __init__(self, render):
        def default_no_op_frame():
            return self
        self.adjacent_frames: Mapping[str, "Frame"] = defaultdict(default_no_op_frame)
        self.render = render

    def add_neighbor(self, transition: str, frame: "Frame") -> None:
        self.adjacent_frames[transition] = frame

    def get_next_frame(self, transition: str) -> "Frame":
        return self.adjacent_frames[transition]

class FrameController():
    def __init__(self, starting_frame: "Frame"):
        self.starting_frame = starting_frame
        self.current_frame = starting_frame
    
    def render(self, *args, **kwargs):
        self.current_frame.render(*args, **kwargs)

    def advance(self, transition: str, *args, **kwargs):
        self.current_frame = self.current_frame.get_next_frame(transition)
        self.render(*args, **kwargs)

    def restart(self):
        self.current_frame = self.starting_frame
