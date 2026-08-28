import os
import numpy as np
from PIL import Image, ImageDraw

def ensure_folders():
    os.makedirs("uploads/before", exist_ok=True)
    os.makedirs("uploads/after", exist_ok=True)
    os.makedirs("uploads/results", exist_ok=True)

def generate_sample_pairs():
    ensure_folders()
    width, height = 512, 512

    # -------------------------------------------------------------
    # Test Case 1: Forest Encroachment (Illegal Deforestation & Roads)
    # -------------------------------------------------------------
    # Baseline T1: Dense green canopy with a river
    t1_forest = Image.new("RGB", (width, height), (34, 110, 45))
    draw_t1 = ImageDraw.Draw(t1_forest)
    
    # Add terrain noise
    noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
    t1_array = np.clip(np.array(t1_forest, dtype=np.int16) + noise, 0, 255).astype(np.uint8)
    t1_forest = Image.fromarray(t1_array)
    draw_t1 = ImageDraw.Draw(t1_forest)

    # Winding river
    draw_t1.line([(0, 200), (180, 260), (350, 220), (512, 300)], fill=(20, 85, 150), width=28)
    t1_forest.save("uploads/before/sample_forest_t1.png")

    # Target T2: Forest cleared with artificial rectangular structures
    t2_forest = t1_forest.copy()
    draw_t2 = ImageDraw.Draw(t2_forest)

    # Illegal cleared land parcel (light brown/bare ground)
    draw_t2.rectangle([220, 80, 460, 280], fill=(185, 155, 110), outline=(130, 100, 60), width=2)
    # New unauthorized concrete structures / roofs
    draw_t2.rectangle([250, 110, 320, 170], fill=(210, 60, 60), outline=(50, 50, 50), width=2)
    draw_t2.rectangle([350, 140, 430, 230], fill=(220, 220, 220), outline=(50, 50, 50), width=2)
    # Access logging road
    draw_t2.line([(100, 0), (220, 120)], fill=(160, 140, 110), width=10)
    t2_forest.save("uploads/after/sample_forest_t2.png")

    # -------------------------------------------------------------
    # Test Case 2: Wetland / Water Body Incursion
    # -------------------------------------------------------------
    # Baseline T1: Large reservoir/wetland buffer
    t1_wetland = Image.new("RGB", (width, height), (40, 90, 50))
    draw_w1 = ImageDraw.Draw(t1_wetland)
    # Open water lake
    draw_w1.ellipse([100, 100, 420, 420], fill=(15, 95, 160))
    t1_wetland.save("uploads/before/sample_water_t1.png")

    # Target T2: Water retention basin partially filled with landfill
    t2_wetland = t1_wetland.copy()
    draw_w2 = ImageDraw.Draw(t2_wetland)
    # Incursion fill
    draw_w2.polygon([(260, 100), (420, 100), (420, 260), (300, 200)], fill=(165, 135, 90))
    # Structural settlement on filled zone
    draw_w2.rectangle([320, 120, 390, 180], fill=(190, 45, 45))
    t2_wetland.save("uploads/after/sample_water_t2.png")

    print("[SUCCESS] Test imagery generated successfully in 'uploads/before' and 'uploads/after'.")

if __name__ == "__main__":
    generate_sample_pairs()