import os
from PIL import Image, ImageTk

BASE_IMAGE_PATH = r"C:\Uni\MED6\Bachelor project\P6_Anti_Fouling\Interactive Interface\Panel Images"
ROTATION_ANGLE = -90  # Degrees to rotate

def find_panel_image(location, month, panel_code):
    image_folder = os.path.join(BASE_IMAGE_PATH, location, month)
    try:
        for filename in os.listdir(image_folder):
            if panel_code in filename and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(image_folder, filename)
                return image_path
    except FileNotFoundError:
        print(f"Error: Folder not found: {image_folder}")
        return None
    except Exception as e:
        print(f"Error listing directory: {e}")
        return None

    print(f"Image not found for {panel_code} in {image_folder}")
    return None

def load_and_display_image(root, image_path, label, image_references, max_height_ratio=1.0):
    """Load, resize, and display an image, rotating to ensure height >= width."""
    try:
        original_image = Image.open(image_path)
        rotated_image = original_image

        if original_image.width > original_image.height:
            rotated_90 = original_image.rotate(270, expand=True)
            if rotated_90.width > rotated_90.height:
                rotated_image = original_image.rotate(90, expand=True)
            else:
                rotated_image = rotated_90

        screen_height = root.winfo_screenheight()
        max_height = int(screen_height * max_height_ratio)
        resized_image = resize_image(rotated_image, max_height)

        photo = ImageTk.PhotoImage(resized_image)
        label.config(image=photo)
        label.image = photo  # Keep a reference!
        image_references.append(photo)  # Add to the list

    except Exception as e:
        print(f"Error loading image: {e}")
        label.config(text="Image not found")
        label.image = None

def resize_image(image, max_height):
    """Resize the image to fit within the maximum height while maintaining aspect ratio."""
    if image.height > max_height:
        ratio = max_height / image.height
        new_width = int(image.width * ratio)
        new_height = max_height
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image