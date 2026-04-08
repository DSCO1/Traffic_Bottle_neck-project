from PIL import Image, ImageDraw

def create_car(color, filename):
    # Transparent background
    img = Image.new("RGBA", (120, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Car body
    draw.rounded_rectangle([10, 25, 110, 50], radius=10, fill=color)

    # Car top
    draw.polygon([(30, 25), (50, 10), (80, 10), (100, 25)], fill=color)

    # Windows
    draw.polygon([(45, 25), (55, 15), (75, 15), (85, 25)], fill=(200, 200, 200, 255))

    # Wheels
    draw.ellipse([25, 45, 45, 65], fill=(30, 30, 30, 255))
    draw.ellipse([75, 45, 95, 65], fill=(30, 30, 30, 255))

    # Wheel inner
    draw.ellipse([30, 50, 40, 60], fill=(180, 180, 180, 255))
    draw.ellipse([80, 50, 90, 60], fill=(180, 180, 180, 255))

    img.save(filename)
    print(f"{filename} created!")


# Create both cars
create_car((75, 139, 250, 255), "blue_car.png")   # Blue
create_car((255, 77, 79, 255), "red_car.png")     # Red