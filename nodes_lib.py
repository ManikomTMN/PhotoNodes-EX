from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
from core_ui import BaseNode
from config import *

NODE_REGISTRY = {}
def register_node(cls):
    NODE_REGISTRY[cls.__name__] = cls
    return cls

# ====================
# system nodes
# ====================

class InputNode(BaseNode):
    def __init__(self):
        super().__init__("Input Image", header_color=C_HEADER_EVENT)
        self.add_output("Image", "IMAGE")
        self.image = None
        self.is_permanent = True
    
    def set_image(self, path):
        try:
            self.image = Image.open(path).convert("RGBA")
        except: pass
    
    def eval(self): return self.image

class OutputNode(BaseNode):
    def __init__(self, cb=None):
        super().__init__("Output Result", header_color=C_HEADER_EVENT)
        self.add_input("Image", "IMAGE")
        self.cb = cb
        self.is_permanent = True
    
    def refresh(self):
        if self.cb: self.cb(self.eval())
        
    def eval(self):
        return self.get_input_val(0)

# ====================
# image processing
# ====================

@register_node
class BrightnessNode(BaseNode):
    def __init__(self):
        super().__init__("Brightness", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_input("Factor", "FLOAT", 1.2)
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        fac = self.get_input_val(1, 1.0)
        if img: return ImageEnhance.Brightness(img).enhance(fac)
        return None

@register_node
class ContrastNode(BaseNode):
    def __init__(self):
        super().__init__("Contrast", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_input("Factor", "FLOAT", 1.5)
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        fac = self.get_input_val(1, 1.0)
        if img: return ImageEnhance.Contrast(img).enhance(fac)
        return None

@register_node
class BlurNode(BaseNode):
    def __init__(self):
        super().__init__("Gaussian Blur", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_input("Radius", "FLOAT", 5.0)
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        rad = self.get_input_val(1, 5.0)
        if img: return img.filter(ImageFilter.GaussianBlur(rad))
        return None

@register_node
class GrayscaleNode(BaseNode):
    def __init__(self):
        super().__init__("Grayscale", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        if img: return ImageOps.grayscale(img).convert("RGBA")
        return None

@register_node
class InvertNode(BaseNode):
    def __init__(self):
        super().__init__("Invert Colors", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        if img: 
            if img.mode == 'RGBA':
                r,g,b,a = img.split()
                rgb = Image.merge('RGB', (r,g,b))
                inv = ImageOps.invert(rgb)
                r2,g2,b2 = inv.split()
                return Image.merge('RGBA', (r2,g2,b2,a))
            return ImageOps.invert(img)
        return None

@register_node
class TransformNode(BaseNode):
    def __init__(self):
        super().__init__("Transform", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_input("Rotate", "FLOAT", 0.0)
        self.add_input("Scale", "FLOAT", 1.0)
        self.add_output("Image", "IMAGE")

    def eval(self):
        img = self.get_input_val(0)
        rot = self.get_input_val(1, 0.0)
        scale = self.get_input_val(2, 1.0)
        if img:
            out = img.rotate(rot, expand=True)
            if scale != 1.0 and scale > 0:
                new_size = (int(out.width * scale), int(out.height * scale))
                out = out.resize(new_size, Image.Resampling.BICUBIC)
            return out
        return None

@register_node
class CropNode(BaseNode):
    def __init__(self):
        super().__init__("Crop Center", header_color=C_HEADER_FUNC)
        self.add_input("Image", "IMAGE")
        self.add_input("Width", "FLOAT", 200)
        self.add_input("Height", "FLOAT", 200)
        self.add_output("Image", "IMAGE")
        
    def eval(self):
        img = self.get_input_val(0)
        w = self.get_input_val(1, 200)
        h = self.get_input_val(2, 200)
        if img:
            cw, ch = img.size
            left = (cw - w)/2
            top = (ch - h)/2
            return img.crop((left, top, left+w, top+h))
        return None

# ====================
# generators
# ====================

@register_node
class DrawSquareNode(BaseNode):
    def __init__(self):
        super().__init__("Draw Rect", header_color=C_HEADER_DEFAULT)
        # the automatic width logic in core_ui will handle these labels now
        self.add_input("X Position", "FLOAT", 50)
        self.add_input("Y Position", "FLOAT", 50)
        self.add_input("Width", "FLOAT", 100)
        self.add_input("Height", "FLOAT", 100)
        self.add_input("Color", "COLOR")
        self.add_output("Image", "IMAGE")

    def eval(self):
        x = int(self.get_input_val(0, 50))
        y = int(self.get_input_val(1, 50))
        w = int(self.get_input_val(2, 100))
        h = int(self.get_input_val(3, 100))
        col = self.get_input_val(4, (255, 0, 0, 255))
        
        img = Image.new("RGBA", (512, 512), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([x, y, x+w, y+h], fill=col)
        return img

@register_node
class ColorNode(BaseNode):
    def __init__(self):
        super().__init__("Make Color", header_color=C_HEADER_DEFAULT)
        self.add_input("Red", "FLOAT", 255)
        self.add_input("Green", "FLOAT", 0)
        self.add_input("Blue", "FLOAT", 0)
        self.add_output("Color", "COLOR")

    def eval(self):
        r = int(self.get_input_val(0, 255))
        g = int(self.get_input_val(1, 0))
        b = int(self.get_input_val(2, 0))
        return (r, g, b, 255)

@register_node
class LayerNode(BaseNode):
    def __init__(self):
        super().__init__("Layer (Add)", header_color=C_HEADER_FUNC)
        self.add_input("Background", "IMAGE")
        self.add_input("Foreground", "IMAGE")
        self.add_output("Combined", "IMAGE")

    def eval(self):
        bg = self.get_input_val(0)
        fg = self.get_input_val(1)
        if not bg and not fg: return None
        if not bg: return fg
        if not fg: return bg
        bg_copy = bg.copy()
        bg_copy.alpha_composite(fg.resize(bg.size))
        return bg_copy

@register_node
class MixNode(BaseNode):
    def __init__(self):
        super().__init__("Mix (Blend)", header_color=C_HEADER_FUNC)
        self.add_input("Img A", "IMAGE")
        self.add_input("Img B", "IMAGE")
        self.add_input("Factor", "FLOAT", 0.5)
        self.add_output("Image", "IMAGE")
        
    def eval(self):
        a = self.get_input_val(0)
        b = self.get_input_val(1)
        f = self.get_input_val(2, 0.5)
        if a and b:
            b_resized = b.resize(a.size)
            return Image.blend(a.convert("RGBA"), b_resized.convert("RGBA"), f)
        return a if a else b

@register_node
class FloatNode(BaseNode):
    def __init__(self):
        super().__init__("Float Input", header_color=C_HEADER_DEFAULT)
        self.add_input("Value", "FLOAT", 0.0)
        self.add_output("Out", "FLOAT")

    def eval(self):
        return float(self.get_input_val(0))