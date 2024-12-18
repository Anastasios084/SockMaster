from PIL import Image, ImageEnhance, ImageFilter
import os
import random  # Import the random module    
    
def apply_texture(base_image, texture_image, mask_image, output_path, alpha=0.5):
    """
    Applies a texture over the sock area of the base image using a separate mask image.
    
    :param base_image: The original sock image (RGBA).
    :param texture_image: The texture image to apply (RGBA).
    :param mask_image: The mask image defining the sock area (L mode).
    :param output_path: Path to save the textured sock image.
    :param alpha: Transparency level for the texture (0 to 1).
    :return: Image object with texture applied.
    """
    # Ensure all images are in the correct mode
    base = base_image.convert("RGBA")
    texture = texture_image.convert("RGBA").resize(base.size)
    mask = mask_image.convert("L").resize(base.size)

    # Adjust the texture's brightness if needed
    enhancer = ImageEnhance.Brightness(texture)
    texture = enhancer.enhance(0.7)  # Modify as necessary

    # Adjust the texture's alpha based on the provided alpha value and the mask
    texture_alpha = texture.split()[3].point(lambda p: p * alpha)
    texture.putalpha(texture_alpha)

    # Create a textured layer using the mask
    textured_layer = Image.composite(texture, Image.new("RGBA", base.size, (0, 0, 0, 0)), mask)

    # Composite the textured layer onto the base image
    textured = Image.alpha_composite(base, textured_layer)

    # Save the textured image
    textured.save(output_path)
    print(f"Texture applied to the sock and saved to {output_path}")
    return textured

def create_pattern(
    base_image,
    pattern_image,
    mask_image,
    output_path,
    pattern_size=(100, 100),
    base_spacing=(50, 50),
    spacing_variation=(10, 10),
    alpha=0.5
):
    base = base_image.convert("RGBA")
    pattern = pattern_image.convert("RGBA").resize(pattern_size)
    mask = mask_image.convert("L").resize(base.size)

    pattern_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

    base_spacing_x, base_spacing_y = base_spacing
    variation_x, variation_y = spacing_variation

    x = 0
    while x < base.size[0]:
        y = 0
        while y < base.size[1]:
            random_angle = random.uniform(0, 360)

            pattern_with_alpha = pattern.copy()
            pattern_alpha = pattern_with_alpha.split()[3].point(lambda p: p * alpha)
            pattern_with_alpha.putalpha(pattern_alpha)

            # Rotate with expansion
            rotated_pattern = pattern_with_alpha.rotate(random_angle, resample=Image.BICUBIC, expand=True)
            rotated_width, rotated_height = rotated_pattern.size

            # Center the rotated pattern at (x, y)
            paste_x = x - rotated_width // 2
            paste_y = y - rotated_height // 2

            # Optional: Check boundaries to prevent excessive clipping
            if paste_x < 0 or paste_y < 0 or paste_x + rotated_width > base.size[0] or paste_y + rotated_height > base.size[1]:
                # Adjust or skip pasting to prevent clipping
                pass  # Implement your logic here

            pattern_layer.paste(rotated_pattern, (paste_x, paste_y), rotated_pattern)

            delta_y = base_spacing_y + random.randint(-variation_y, variation_y)
            y += pattern_size[1] + delta_y

        delta_x = base_spacing_x + random.randint(-variation_x, variation_x)
        x += pattern_size[0] + delta_x

    patterned_layer = Image.composite(pattern_layer, Image.new("RGBA", base.size, (0, 0, 0, 0)), mask)
    combined = Image.alpha_composite(base, patterned_layer)
    combined.save(output_path)
    print(f"Pattern applied to the sock and saved to {output_path}")
    return combined


def border(img, stroke_radius, color):
    """
    Adds a border (stroke) around the given image.

    Parameters:
    - img (PIL.Image.Image): The original image. Must be in "RGBA" mode.
    - stroke_radius (int): The radius (thickness) of the border in pixels.
    - color (tuple): The color of the border in RGBA format, e.g., (255, 255, 255, 255) for opaque white.

    Returns:
    - PIL.Image.Image: The image with the added border.
    """
    # Ensure the image is in RGBA mode
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Calculate the new size to accommodate the border on all sides
    new_size = (img.width + 2 * stroke_radius, img.height + 2 * stroke_radius)
    print(f"Original size: {img.size}, New size with border: {new_size}")

    # Create a new image with the specified background color
    stroke_image = Image.new("RGBA", new_size, color)

    # Extract the alpha channel from the original image and create a binary mask
    img_alpha = img.getchannel(3).point(lambda x: 255 if x > 0 else 0)

    # Create a new alpha mask for the stroke_image
    # Start with a transparent mask
    stroke_alpha = Image.new("L", new_size, 0)
    
    # Paste the original alpha into the stroke_alpha at the correct offset
    stroke_alpha.paste(img_alpha, (stroke_radius, stroke_radius))

    # Apply a maximum filter to expand the alpha mask outward by stroke_radius
    # The filter size should be an odd number; 2*stroke_radius +1 ensures adequate expansion
    filter_size = 2 * stroke_radius + 1
    stroke_alpha = stroke_alpha.filter(ImageFilter.MaxFilter(filter_size))

    # Optionally, smooth the alpha mask for a softer border
    stroke_alpha = stroke_alpha.filter(ImageFilter.SMOOTH)

    # Put the processed alpha mask into the stroke_image's alpha channel
    stroke_image.putalpha(stroke_alpha)

    # Paste the original image onto the stroke_image at the correct offset, using its own alpha as mask
    stroke_image.paste(img, (stroke_radius, stroke_radius), img)

    return stroke_image


def main():
    # Define file paths
    sock_path = "images/sock.png"
    texture_path = "images/texture.jpg"
    dog_path = "images/dog.png"
    mask_path = "images/sock_mask.png"  # Separate mask file

    # Output paths
    textured_sock_path = "sock_with_texture.png"
    patterned_sock_path = "sock_with_pattern.png"
    final_sock_path = "sock_final.png"

    # Check if all files exist
    for file in [sock_path, texture_path, dog_path, mask_path]:
        if not os.path.isfile(file):
            print(f"Error: {file} not found in the current directory.")
            return

    # Open images with error handling
    try:
        sock = Image.open(sock_path)
    except Exception as e:
        print(f"Error opening {sock_path}: {e}")
        return

    try:
        texture = Image.open(texture_path)
    except Exception as e:
        print(f"Error opening {texture_path}: {e}")
        return

    try:
        dog = Image.open(dog_path)
    except Exception as e:
        print(f"Error opening {dog_path}: {e}")
        return

    try:
        mask = Image.open(mask_path)
    except Exception as e:
        print(f"Error opening {mask_path}: {e}")
        return

    # Step 1: Apply texture to the sock using the mask
    textured_sock = apply_texture(sock, texture, mask, textured_sock_path, alpha=0.6)
    
    bordered_sock = border(dog, 10, (255,255,255,255))
    bordered_sock.save("bordered.png")
    # Step 2: Create a pattern with dog.png on the textured sock using the mask
    patterned_sock = create_pattern(
        textured_sock,
        bordered_sock,
        mask,
        patterned_sock_path,
        pattern_size=(300, 300),
        base_spacing=(80, 80),
        spacing_variation=(50, 50),  # Added spacing variation
        alpha=0.9
    )

    # Optionally, save the final image
    patterned_sock.save(final_sock_path)
    print(f"Final image saved to {final_sock_path}")

    print("Image processing complete. Check the output files.")

if __name__ == "__main__":
    main()
