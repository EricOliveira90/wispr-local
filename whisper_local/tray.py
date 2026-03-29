"""System tray icon — renders microphone icon with state colors and context menu."""

from PIL import Image, ImageDraw
import pystray


# State → color mapping (RGB)
STATE_COLORS = {
    "idle": (128, 128, 128),       # Gray
    "loading": (255, 200, 0),      # Yellow
    "ready": (0, 51, 153),         # Dark Blue
    "listening_en": (0, 120, 255), # Bright Blue
    "listening_pt": (0, 180, 0),   # Green
}


def create_icon_image(color: tuple[int, int, int], size: int = 64) -> Image.Image:
    """Create a simple circular microphone icon with the given color."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Draw filled circle
    margin = 4
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    # Draw simple mic shape (white rectangle + stand)
    mic_w, mic_h = size // 5, size // 3
    mic_x = (size - mic_w) // 2
    mic_y = size // 4
    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_w, mic_y + mic_h],
        radius=mic_w // 2,
        fill=(255, 255, 255),
    )
    # Mic stand
    stand_x = size // 2
    stand_top = mic_y + mic_h
    stand_bottom = stand_top + size // 8
    draw.line([(stand_x, stand_top), (stand_x, stand_bottom)], fill=(255, 255, 255), width=2)
    return image


def create_tray_icon(
    menu_items: list[pystray.MenuItem],
    initial_state: str = "idle",
    on_quit: callable = None,
) -> pystray.Icon:
    """Create and return a pystray Icon with the given menu and initial state color."""
    color = STATE_COLORS.get(initial_state, STATE_COLORS["idle"])
    image = create_icon_image(color)

    icon = pystray.Icon(
        name="whisper-local",
        icon=image,
        title="Whisper Local",
        menu=pystray.Menu(*menu_items),
    )
    return icon


def update_tray_state(icon: pystray.Icon, state: str) -> None:
    """Update the tray icon color to reflect the given state."""
    color = STATE_COLORS.get(state, STATE_COLORS["idle"])
    icon.icon = create_icon_image(color)
    # Update tooltip
    state_labels = {
        "idle": "Idle (no model)",
        "loading": "Loading model...",
        "ready": "Ready",
        "listening_en": "Listening (English)",
        "listening_pt": "Listening (Portuguese)",
    }
    icon.title = f"Whisper Local — {state_labels.get(state, state)}"
