import random
import csv
import time
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# --- Configuration ---
PROJECT_ID = "thesisprojectai-482002" 
LOCATION = "us-central1"
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# DAMAGE TYPES that can be confused with Botrytis (from Section 7.4)
CONFUSING_DAMAGES = [
    {
        "damage_type": "Thrips",
        "description": "silvery-white scratched streaks and tiny elongated scars from thrips feeding damage",
        "detail": "irregular linear scratches and scrapes, creating silvery or whitish streaked patterns where the thrips (Frankliniella occidentalis) have rasped the petal surface, appearing as fine parallel lines or scattered elongated marks",
        "texture": "DRY, SCRATCHED, with visible linear scraping patterns - NOT circular spots",
        "key_difference": "The damage appears as STREAKS and LINES, not round spots. Surface is abraded and rough, showing directional feeding tracks.",
        "visibility": "more visible on darker roses (red, pink) where silvery damage contrasts strongly",
        "coverage": "EXACTLY 1-2 small isolated areas ONLY, affecting less than 5% of visible petal surface",
        "exact_count": "ONE or TWO small damage marks maximum"
    },
    {
        "damage_type": "Chemical_Burn",
        "description": "phytotoxic burn marks with sharply defined edges from pesticide or fertilizer spray residue",
        "detail": "irregular shaped brown or tan patches with VERY SHARP, DEFINED borders where droplets dried, creating distinct margin lines, the damage appears as if painted or stamped onto the petal",
        "texture": "DRY, CRISP, with hard edges and uniform discoloration within the burned area",
        "key_difference": "The damage has GEOMETRIC, SHARP edges following droplet boundaries - NOT diffuse halos. No fungal growth.",
        "visibility": "can appear on any color, typically where spray droplets landed and dried",
        "coverage": "EXACTLY 1 or 2 isolated spots ONLY, each 3-5mm in size, covering less than 5% of petal surface",
        "exact_count": "ONE or TWO spots maximum - representing where individual droplets landed"
    },
    {
        "damage_type": "Mechanical",
        "description": "physical bruising, tears, and crushing damage from handling or transport",
        "detail": "ONE single small area of irregular browning or darkening with torn edge, crease mark, or compression zone, showing where ONE petal was bent, folded, or crushed during handling",
        "texture": "DRY, with visible SINGLE TEAR, ONE CREASE, or ONE FOLD LINE - damage follows stress pattern",
        "key_difference": "Damage shows ONE DIRECTIONAL crushing or tearing pattern - NOT circular, NOT multiple marks. Edge is ragged, not smooth.",
        "visibility": "typically on ONE outer petal that received handling stress",
        "coverage": "EXACTLY 1 SINGLE localized damage area ONLY on ONE petal, such as ONE small crease line OR ONE tiny bruised zone, affecting less than 3-5% of visible surface",
        "exact_count": "ONE single damage site only - ONE crease OR ONE small bruise on ONE petal ONLY"
    }
]

# Rose colors (reusing from original)
ROSE_COLORS = [
    {"name": "White (Vendela)", "base_description": "pristine white petals"},
    {"name": "Deep Red (Explorer)", "base_description": "deep crimson petals"},
    {"name": "Yellow (St. Patrick)", "base_description": "bright golden yellow petals"},
    {"name": "Orange (Movie Star)", "base_description": "vibrant orange petals"},
    {"name": "Peach", "base_description": "delicate soft peach petals"},
    {"name": "Pink (Rosa)", "base_description": "rose pink petals"}
]

# Bloom stages (reusing your successful version)
BLOOM_STAGES = [
    {
        "stage": "tight_bud",
        "description": "completely closed tight bud, sepals still wrapping around the petals, NO petal separation visible, compact oval shape",
        "petal_visibility": "petals entirely enclosed within green sepals, only the very tips of outer petals barely emerging",
        "negative_additions": "fully opened petals, separated petals, visible flower center, bloomed rose"
    },
    {
        "stage": "early_opening",
        "description": "bud just starting to crack open, outer petals beginning to peel back but still tightly furled, approximately 15-25% open",
        "petal_visibility": "only 2-3 outer petal layers starting to loosen, inner petals still completely hidden and tightly wrapped",
        "negative_additions": "fully bloomed, wide open petals, horizontal petal spread, classic rose shape"
    },
    {
        "stage": "half_bloom",
        "description": "rose at 40-50% bloom, outer petals clearly separated and beginning to curve outward, recognizable rose shape emerging but compact",
        "petal_visibility": "outer 3-4 petal layers open and distinct, middle layers visible but still curved inward, innermost petals remain concealed",
        "negative_additions": "completely open, fully expanded, all petals visible, flat horizontal petals"
    },
    {
        "stage": "full_bloom",
        "description": "completely opened mature rose showing full petal expansion, all layers unfurled and spread outward",
        "petal_visibility": "all petal layers fully expanded, separated, and visible from outer to inner",
        "negative_additions": "closed bud, tight petals, furled petals, compressed form"
    }
]

# EXPANDED ANGLES for more variety
CAMERA_ANGLES = [
    {
        "name": "frontal_close",
        "description": "straight-on frontal view focusing on the flower head",
        "framing": "close-up of the bloom filling most of the frame",
        "stem_visibility": "minimal or no stem visible"
    },
    {
        "name": "angled_30",
        "description": "30-degree angled perspective from upper right",
        "framing": "three-quarter view showing bloom dimensionality",
        "stem_visibility": "top portion of stem barely visible"
    },
    {
        "name": "overhead_gentle",
        "description": "gentle overhead angle looking down at 45 degrees",
        "framing": "bird's eye perspective showing petal arrangement",
        "stem_visibility": "stem visible extending downward"
    },
    {
        "name": "three_quarter_with_stem",
        "description": "three-quarter view at eye level showing both bloom and upper stem",
        "framing": "medium shot with flower head occupying upper two-thirds of frame and 5-8cm of green stem visible below",
        "stem_visibility": "upper 5-8cm of healthy green stem clearly visible, showing stem texture and any visible thorns or leaves"
    },
    {
        "name": "side_profile_with_stem",
        "description": "side profile view at 90-degree angle showing flower in profile with stem",
        "framing": "lateral view capturing the full depth of the bloom and 6-10cm of stem extending downward",
        "stem_visibility": "6-10cm of vertical green stem clearly visible, showing the natural curve and attachment point of the flower"
    },
    {
        "name": "slight_upward_angle",
        "description": "camera positioned slightly below the flower looking upward at 15-20 degrees",
        "framing": "upward perspective showing underside detail of petals and 4-6cm of stem",
        "stem_visibility": "4-6cm of stem visible from below, showing where bloom attaches to stem"
    },
    {
        "name": "diagonal_high_with_stem",
        "description": "high diagonal angle at 60 degrees from upper left side",
        "framing": "dramatic overhead perspective with flower and 7-10cm of descending stem",
        "stem_visibility": "7-10cm of stem extending diagonally downward, creating depth in composition"
    },
    {
        "name": "portrait_full_stem",
        "description": "vertical portrait composition showing complete flower and extended stem section",
        "framing": "tall vertical frame with bloom at top third and 10-12cm of stem visible below",
        "stem_visibility": "10-12cm of green stem prominently displayed, showing natural stem characteristics"
    },
    {
        "name": "dynamic_tilt_with_stem",
        "description": "tilted angle at 25 degrees with flower slightly off-center and stem visible",
        "framing": "dynamic asymmetric composition with bloom and 5-7cm of stem at angle",
        "stem_visibility": "5-7cm of stem visible at diagonal, adding movement to composition"
    }
]

# BACKGROUND OPTIONS (optional variety)
BACKGROUNDS = [
    "soft-focus blurred greenhouse environment with diffused natural light",
    "clean white studio background with professional lighting",
    "subtle gray gradient backdrop with soft shadows",
    "blurred garden foliage creating natural bokeh effect",
    "neutral beige background suggesting wooden work surface",
    "soft green blurred background evoking greenhouse atmosphere"
]

def generate_damaged_roses():
    try:
        num_images = int(input("Enter the number of damaged rose images to generate: "))
    except ValueError:
        print("Invalid number entered.")
        return
    
    log_data = []

    # Distribution: cycle through damage types, colors, and NOW angles
    for i in range(num_images):
        damage = CONFUSING_DAMAGES[i % len(CONFUSING_DAMAGES)]
        color_data = ROSE_COLORS[i % len(ROSE_COLORS)]
        angle = CAMERA_ANGLES[i % len(CAMERA_ANGLES)]  # Cycle through all angles
        background = random.choice(BACKGROUNDS)
        bloom_stage = random.choice(BLOOM_STAGES)
        
        color = color_data['name']
        base_desc = color_data['base_description']
        
        # Special handling for mechanical damage
        if damage['damage_type'] == "Mechanical":
            damage_emphasis = (
                f"CRITICAL FOR MECHANICAL DAMAGE: Show ONLY ONE SINGLE small imperfection on ONE petal edge. "
                f"NOT multiple brown areas, NOT brown on several petals, NOT damage all around the edges. "
                f"Just ONE tiny crease OR ONE small bruise on ONE petal. "
                f"All other petals must be COMPLETELY PERFECT with no browning, no damage, no marks. "
                f"Think: if you had to point to the damage, there would be ONE spot to point at. "
            )
        else:
            damage_emphasis = ""
        
        # Enhanced stem description for angles that show stem
        stem_description = ""
        if "stem" in angle['name'].lower() or angle['stem_visibility'] != "minimal or no stem visible":
            stem_description = (
                f"The rose stem is HEALTHY, smooth green stem with natural thickness (4-6mm diameter). "
                f"{angle['stem_visibility']}. "
                f"The stem is CLEAN and UNDAMAGED - no brown spots, no lesions on the stem. "
                f"Stem texture is natural and organic with subtle ridge details. "
            )
        
        prompt = (
            f"Ultra-high resolution botanical photography: A {bloom_stage['stage'].replace('_', ' ')} {color} rose flower "
            f"showing EXTREMELY MINIMAL NON-FUNGAL physical damage that could be confused with disease. "
            f"BLOOM STAGE: {bloom_stage['description']}. "
            f"PETAL STRUCTURE: {bloom_stage['petal_visibility']}. "
            f"\n\n"
            f"CAMERA ANGLE: {angle['description']}. "
            f"FRAMING: {angle['framing']}. "
            f"{stem_description}"
            f"BACKGROUND: {background}. "
            f"Professional greenhouse studio lighting with soft diffusion, creating natural depth and dimension. "
            f"\n\n"
            f"DAMAGE TYPE: {damage['damage_type']} - {damage['description']}. "
            f"DAMAGE CHARACTERISTICS: {damage['detail']}. "
            f"TEXTURE: {damage['texture']}. "
            f"KEY DIAGNOSTIC FEATURE: {damage['key_difference']}. "
            f"VISIBILITY NOTE: {damage['visibility']}. "
            f"\n\n"
            f"{damage_emphasis}"
            f"ABSOLUTE MAXIMUM DAMAGE LIMIT: {damage['exact_count']}. "
            f"CRITICAL - DAMAGE AMOUNT: {damage['coverage']}. "
            f"Show ONLY {damage['exact_count']} on the ENTIRE flower - NOT multiple spots, NOT many marks. "
            f"The damage must be BARELY NOTICEABLE - a SINGLE small defect or at most TWO tiny marks. "
            f"AT LEAST 97% of all rose petals must remain COMPLETELY PERFECT and UNDAMAGED. "
            f"This is a MOSTLY HEALTHY rose with just ONE or TWO subtle imperfections. "
            f"\n\n"
            f"The rose has beautiful, pristine {base_desc} with EXTREMELY SUBTLE {damage['damage_type'].lower()} damage. "
            f"Show {damage['exact_count']} - this is NOT extensive damage. "
            f"The damage is VERY LIGHT and EXTREMELY LIMITED - barely visible unless you look closely. "
            f"This is PHYSICAL or CHEMICAL damage, NOT pathogenic disease. "
            f"The flower is PREDOMINANTLY BEAUTIFUL and HEALTHY with minimal imperfection. "
            f"\n\n"
            f"8K macro photography showing the single or double {damage['damage_type'].lower()} damage mark(s) on DRY, MATTE petal surface. "
            f"The damaged area(s) are completely DRY - no moisture, no wetness, no glossiness. "
            f"Professional composition with depth of field appropriate to the {angle['name'].replace('_', ' ')} angle. "
            f"\n\n"
            f"CRITICAL: This is NOT Botrytis infection. This is minimal {damage['damage_type']} damage. "
            f"Show ONLY {damage['exact_count']} as described - count them: ONE or TWO marks maximum. "
            f"DO NOT show three, four, five or more damage sites. "
            f"STOP at one or two marks. "
            f"\n\n"
            f"STRICTLY AVOID: fungal growth, gray mold, Botrytis, circular spots, diffuse halos, "
            f"water drops, moisture, wetness, glossiness, "
            f"stamens, pistils, flower center structures (unless bloom is fully open), "
            f"three or more damage marks, multiple damage sites, numerous spots, many lesions, "
            f"extensive damage, widespread damage, multiple damage sites covering areas, scattered damage, "
            f"more than two marks, more than two spots, more than two lesions, "
            f"brown edges on multiple petals, browning around the rose, damage on several petals, "
            f"damaged stem, brown stem, lesions on stem, spotted stem, "
            f"{bloom_stage['negative_additions']}. "
            f"\n\n"
            f"Show a {bloom_stage['stage'].replace('_', ' ')} {color} rose from {angle['name'].replace('_', ' ')} angle "
            f"that is MOSTLY PERFECT with only {damage['exact_count']} of {damage['damage_type']} damage on DRY petals. "
            f"Count the damage marks: there should be ONE or at most TWO. Not three, not four, not many. "
            f"The rose should look NEARLY FLAWLESS."
        )

        print(f"[{i+1}/{num_images}] Generating {color} at {bloom_stage['stage']} with {damage['damage_type']} damage, angle: {angle['name']}...")

        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                    negative_prompt=(
                        "Botrytis, gray mold, fungal growth, circular spots, round lesions, diffuse halos, "
                        "water, water drops, moisture, wetness, dew, glossy, shiny, wet-looking, "
                        "3D objects, raised bumps, spheres, "
                        "stamens, pistils, flower center (for buds and early blooms), "
                        "extensive damage, widespread damage, severe damage, multiple lesions, many spots, numerous marks, "
                        "covered in damage, damaged all over, heavily damaged, three spots, four spots, five spots, "
                        "many damage sites, scattered damage, multiple areas of damage, "
                        "more than two marks, more than two spots, more than two lesions, "
                        "brown edges on multiple petals, browning all around, damage on several petals, "
                        "multiple brown areas, brown on many petals, widespread browning, "
                        "brown stem, damaged stem, spotted stem, diseased stem, lesions on stem, "
                        f"{bloom_stage['negative_additions']}, "
                        "disease, infection, rot, decay, fungus"
                    )
                )
            )

            for gen_img in response.generated_images:
                filename = f"Manipulacion_2/rose_damage_{damage['damage_type'].lower()}_{color.split()[0].lower()}_{bloom_stage['stage']}_{angle['name']}_{i+1:03d}.png"
                img = Image.open(BytesIO(gen_img.image.image_bytes))
                img.save(filename)
                log_data.append({
                    "filename": filename,
                    "rose_color": color,
                    "bloom_stage": bloom_stage['stage'],
                    "camera_angle": angle['name'],
                    "angle_description": angle['description'],
                    "stem_visibility": angle['stem_visibility'],
                    "background": background,
                    "damage_type": damage['damage_type'],
                    "damage_description": damage['description'],
                    "damage_coverage": damage['coverage'],
                    "exact_count": damage['exact_count'],
                    "prompt": prompt
                })
                print(f"  ✓ Saved: {filename}")

            if i % 2:
                time.sleep(60)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save log
    if log_data:
        with open('rose_confusing_damage_log.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'rose_color', 'bloom_stage', 'camera_angle', 'angle_description', 'stem_visibility', 'background', 'damage_type', 'damage_description', 'damage_coverage', 'exact_count', 'prompt'])
            writer.writeheader()
            writer.writerows(log_data)
        
        print(f"\n✓ Generated {len(log_data)} roses with MINIMAL non-Botrytis damage")
        print(f"✓ Log: rose_confusing_damage_log.csv")
        print("\nAngles generated:")
        for angle in CAMERA_ANGLES:
            print(f"  - {angle['name']}: {angle['description']}")
        print("\nDamage types generated (from document Section 7.4):")
        print("- Thrips: 1-2 small silvery scratched streaks ONLY (<5% coverage)")
        print("- Chemical Burn: 1-2 isolated sharp-edged spots ONLY (<5% coverage)")
        print("- Mechanical: 1 SINGLE tiny crease/bruise on ONE petal ONLY (<3-5% coverage)")
    else:
        print("\n✗ No images generated")

if __name__ == "__main__":
    generate_damaged_roses()
