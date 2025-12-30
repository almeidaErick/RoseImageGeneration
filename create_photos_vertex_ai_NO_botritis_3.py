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

# Rose colors (expanded for more variety)
ROSE_COLORS = [
    {"name": "White (Vendela)", "base_description": "pristine pure white petals with subtle cream undertones"},
    {"name": "Deep Red (Explorer)", "base_description": "deep crimson red petals with velvety texture"},
    {"name": "Bright Red (Freedom)", "base_description": "vibrant bright red petals with classic rose appearance"},
    {"name": "Yellow (St. Patrick)", "base_description": "bright golden yellow petals with sunny warmth"},
    {"name": "Lemon Yellow", "base_description": "soft lemon yellow petals with delicate pale tones"},
    {"name": "Orange (Movie Star)", "base_description": "vibrant orange petals with coral undertones"},
    {"name": "Peach", "base_description": "delicate soft peach petals with gentle pink blush"},
    {"name": "Light Pink (Engagement)", "base_description": "soft light pink petals with romantic appearance"},
    {"name": "Pink (Rosa)", "base_description": "rose pink petals with medium intensity"},
    {"name": "Hot Pink", "base_description": "vibrant hot pink petals with bold color saturation"},
    {"name": "Coral", "base_description": "warm coral petals blending pink and orange hues"}
]

# EXPANDED Bloom stages - AHORA CON 10 ETAPAS
BLOOM_STAGES = [
    {
        "stage": "tight_bud",
        "description": "completely closed tight bud, sepals still wrapping around the petals, NO petal separation visible, compact oval shape",
        "petal_visibility": "petals entirely enclosed within green sepals, only the very tips of outer petals barely emerging",
        "negative_additions": "fully opened petals, separated petals, visible flower center, bloomed rose"
    },
    {
        "stage": "cracking_bud",
        "description": "bud just beginning to crack, sepals starting to separate revealing the first hint of petal color, still very compact",
        "petal_visibility": "petals barely visible through separating sepals, only top edges of outer petals showing",
        "negative_additions": "open bloom, separated petals, visible layers, fully opened"
    },
    {
        "stage": "early_opening",
        "description": "bud just starting to crack open, outer petals beginning to peel back but still tightly furled, approximately 15-25% open",
        "petal_visibility": "only 2-3 outer petal layers starting to loosen, inner petals still completely hidden and tightly wrapped",
        "negative_additions": "fully bloomed, wide open petals, horizontal petal spread, classic rose shape"
    },
    {
        "stage": "quarter_bloom",
        "description": "rose at 25-35% bloom, outer petals separating and starting to curve, still maintaining compact form",
        "petal_visibility": "outer 2-3 petal layers distinctly separated, middle layers beginning to emerge, center still concealed",
        "negative_additions": "completely open, fully expanded, all petals visible, flat horizontal petals"
    },
    {
        "stage": "one_third_bloom",
        "description": "rose at 35-40% bloom, outer petals curving outward with middle layers becoming visible, recognizable rose form emerging",
        "petal_visibility": "outer 3 petal layers separated and curved, middle layers starting to unfurl, innermost petals tightly concealed",
        "negative_additions": "fully open, completely bloomed, flat petals, all layers visible"
    },
    {
        "stage": "half_bloom",
        "description": "rose at 40-50% bloom, outer petals clearly separated and beginning to curve outward, recognizable rose shape emerging but compact",
        "petal_visibility": "outer 3-4 petal layers open and distinct, middle layers visible but still curved inward, innermost petals remain concealed",
        "negative_additions": "completely open, fully expanded, all petals visible, flat horizontal petals"
    },
    {
        "stage": "two_thirds_bloom",
        "description": "rose at 55-65% bloom, most outer and middle petals unfurled, classic rose shape clearly visible with some inner petals still curved",
        "petal_visibility": "outer 4-5 petal layers fully open, middle layers separated and spreading, only center petals remain partially furled",
        "negative_additions": "closed bud, tight form, completely unopened, compressed petals"
    },
    {
        "stage": "three_quarter_bloom",
        "description": "rose at 60-75% bloom, most petal layers unfurled with outer petals fully spread, classic rose form clearly defined",
        "petal_visibility": "outer and middle petal layers fully opened and separated, only innermost center petals still partially furled",
        "negative_additions": "closed bud, tight petals, completely unopened"
    },
    {
        "stage": "near_full_bloom",
        "description": "rose at 80-90% bloom, nearly all petals unfurled with just the center petals beginning to open, full classic form",
        "petal_visibility": "all outer and middle layers fully expanded, innermost petals just beginning to separate and open",
        "negative_additions": "tight bud, closed form, furled petals, compressed shape"
    },
    {
        "stage": "full_bloom",
        "description": "completely opened mature rose showing full petal expansion, all layers unfurled and spread outward in perfect symmetry",
        "petal_visibility": "all petal layers fully expanded, separated, and visible from outer to inner, center stamens visible",
        "negative_additions": "closed bud, tight petals, furled petals, compressed form"
    }
]

# MASSIVELY EXPANDED camera angles - AHORA CON 35 ÁNGULOS
CAMERA_ANGLES = [
    {
        "name": "frontal_close",
        "description": "straight-on frontal view focusing directly on the flower head",
        "framing": "close-up of the bloom filling most of the frame",
        "stem_visibility": "minimal or no stem visible"
    },
    {
        "name": "frontal_medium",
        "description": "frontal view with slight distance showing complete bloom",
        "framing": "medium shot with bloom centered and 3-4cm of stem visible",
        "stem_visibility": "upper 3-4cm of healthy green stem visible below bloom"
    },
    {
        "name": "frontal_tight_macro",
        "description": "extreme frontal close-up focusing on center petals",
        "framing": "ultra-tight frontal crop showing intricate central petal arrangement",
        "stem_visibility": "no stem visible, pure frontal bloom detail"
    },
    {
        "name": "angled_20_right",
        "description": "20-degree gentle angle from upper right",
        "framing": "subtle three-quarter view with soft dimensionality",
        "stem_visibility": "minimal stem, 2-3cm visible"
    },
    {
        "name": "angled_30_right",
        "description": "30-degree angled perspective from upper right",
        "framing": "three-quarter view showing bloom dimensionality",
        "stem_visibility": "top portion of stem barely visible"
    },
    {
        "name": "angled_30_left",
        "description": "30-degree angled perspective from upper left",
        "framing": "three-quarter view showing bloom depth and petal layers",
        "stem_visibility": "minimal stem visibility, focus on bloom"
    },
    {
        "name": "angled_45_right",
        "description": "45-degree angle from right side showing bloom profile",
        "framing": "diagonal composition emphasizing petal structure",
        "stem_visibility": "upper 4-5cm of stem visible"
    },
    {
        "name": "angled_45_left",
        "description": "45-degree angle from left side capturing bloom curvature",
        "framing": "dynamic diagonal view with natural depth",
        "stem_visibility": "4-5cm of healthy stem visible"
    },
    {
        "name": "angled_60_right",
        "description": "steep 60-degree angle from right showing dramatic perspective",
        "framing": "high diagonal view with strong depth",
        "stem_visibility": "5-7cm of stem visible at angle"
    },
    {
        "name": "overhead_gentle",
        "description": "gentle overhead angle looking down at 45 degrees",
        "framing": "bird's eye perspective showing circular petal arrangement",
        "stem_visibility": "stem visible extending downward, 5-7cm visible"
    },
    {
        "name": "overhead_steep",
        "description": "steep overhead angle at 70 degrees from directly above",
        "framing": "top-down view showcasing spiral petal pattern",
        "stem_visibility": "8-10cm of stem extending straight down"
    },
    {
        "name": "overhead_extreme",
        "description": "extreme overhead angle at 85 degrees, nearly straight down",
        "framing": "direct top-down view capturing perfect spiral geometry",
        "stem_visibility": "10-12cm of stem visible vertically below"
    },
    {
        "name": "three_quarter_with_stem",
        "description": "three-quarter view at eye level showing both bloom and upper stem",
        "framing": "medium shot with flower head occupying upper two-thirds of frame and 5-8cm of green stem visible below",
        "stem_visibility": "upper 5-8cm of healthy green stem clearly visible, showing stem texture and natural characteristics"
    },
    {
        "name": "three_quarter_elevated",
        "description": "elevated three-quarter view from 50 degrees above",
        "framing": "high angle three-quarter composition",
        "stem_visibility": "8-9cm of stem visible from elevated perspective"
    },
    {
        "name": "three_quarter_low",
        "description": "low three-quarter view from 30 degrees below eye level",
        "framing": "upward three-quarter perspective showing bloom from below",
        "stem_visibility": "6-8cm of stem rising upward"
    },
    {
        "name": "side_profile_with_stem",
        "description": "side profile view at 90-degree angle showing flower in complete profile with stem",
        "framing": "lateral view capturing the full depth of the bloom and 6-10cm of stem extending downward",
        "stem_visibility": "6-10cm of vertical green stem clearly visible, showing the natural curve and attachment point"
    },
    {
        "name": "side_profile_close",
        "description": "close side profile focusing on bloom silhouette",
        "framing": "tight lateral shot emphasizing bloom outline",
        "stem_visibility": "minimal stem, 2-3cm visible"
    },
    {
        "name": "side_profile_upper",
        "description": "side profile from slightly above showing top curve of bloom",
        "framing": "lateral view from 20 degrees above showing upper bloom profile",
        "stem_visibility": "4-6cm of stem visible from side-top angle"
    },
    {
        "name": "slight_upward_angle",
        "description": "camera positioned slightly below the flower looking upward at 15-20 degrees",
        "framing": "upward perspective showing underside detail of petals and stem attachment",
        "stem_visibility": "4-6cm of stem visible from below"
    },
    {
        "name": "upward_moderate",
        "description": "moderate upward angle at 30 degrees from below",
        "framing": "upward perspective emphasizing petal undersides",
        "stem_visibility": "5-7cm of stem visible rising above"
    },
    {
        "name": "upward_steep",
        "description": "steep upward angle at 40 degrees from below",
        "framing": "dramatic low perspective showing petal undersides",
        "stem_visibility": "6-8cm of stem visible from low angle"
    },
    {
        "name": "diagonal_high_with_stem",
        "description": "high diagonal angle at 60 degrees from upper left side",
        "framing": "dramatic overhead perspective with flower and descending stem",
        "stem_visibility": "7-10cm of stem extending diagonally downward"
    },
    {
        "name": "diagonal_low_right",
        "description": "low diagonal angle at 30 degrees from lower right",
        "framing": "upward diagonal capturing bloom from below-right",
        "stem_visibility": "5-7cm of stem rising diagonally"
    },
    {
        "name": "diagonal_low_left",
        "description": "low diagonal angle at 35 degrees from lower left",
        "framing": "upward diagonal from left side showing dynamic perspective",
        "stem_visibility": "6-8cm of stem at diagonal angle"
    },
    {
        "name": "portrait_full_stem",
        "description": "vertical portrait composition showing complete flower and extended stem section",
        "framing": "tall vertical frame with bloom at top third and 10-12cm of stem visible below",
        "stem_visibility": "10-12cm of green stem prominently displayed"
    },
    {
        "name": "portrait_medium_stem",
        "description": "vertical portrait with balanced bloom and stem composition",
        "framing": "vertical frame with bloom centered and 7-9cm of stem",
        "stem_visibility": "7-9cm of healthy stem visible in vertical orientation"
    },
    {
        "name": "portrait_short_stem",
        "description": "vertical portrait emphasizing bloom with shorter stem visible",
        "framing": "vertical composition with bloom dominant and 4-5cm of stem",
        "stem_visibility": "4-5cm of stem in vertical frame"
    },
    {
        "name": "dynamic_tilt_with_stem",
        "description": "tilted angle at 25 degrees with flower slightly off-center and stem visible",
        "framing": "dynamic asymmetric composition with bloom and stem at angle",
        "stem_visibility": "5-7cm of stem visible at diagonal"
    },
    {
        "name": "dynamic_tilt_opposite",
        "description": "tilted angle at 25 degrees in opposite direction with artistic composition",
        "framing": "asymmetric frame with bloom tilted opposite way",
        "stem_visibility": "6-8cm of stem at contrasting diagonal"
    },
    {
        "name": "dynamic_tilt_steep",
        "description": "steep tilt at 40 degrees creating dramatic diagonal composition",
        "framing": "strongly tilted frame with dynamic energy",
        "stem_visibility": "7-9cm of stem at steep diagonal"
    },
    {
        "name": "extreme_close_macro",
        "description": "extreme macro close-up focusing on central petal details",
        "framing": "ultra-tight crop showing intricate petal texture and arrangement",
        "stem_visibility": "no stem visible, pure bloom detail"
    },
    {
        "name": "low_angle_hero",
        "description": "dramatic low angle at 25 degrees creating hero shot perspective",
        "framing": "bloom towers above viewer with majestic presence",
        "stem_visibility": "6-8cm of stem rising powerfully from below"
    },
    {
        "name": "centered_balanced",
        "description": "perfectly centered composition with balanced framing",
        "framing": "symmetrical centered shot with bloom and stem equally weighted",
        "stem_visibility": "5-6cm of stem visible in balanced composition"
    },
    {
        "name": "artistic_offset",
        "description": "artistic composition with bloom offset to left third",
        "framing": "rule-of-thirds composition with negative space",
        "stem_visibility": "4-6cm of stem visible, creating visual flow"
    },
    {
        "name": "spiral_overhead",
        "description": "overhead view emphasizing the natural spiral of petals",
        "framing": "top-down capturing the mathematical beauty of petal arrangement",
        "stem_visibility": "7-9cm of stem visible extending downward"
    }
]

# MASSIVELY EXPANDED BACKGROUNDS - AHORA CON 25 FONDOS
BACKGROUNDS = [
    "soft-focus blurred greenhouse environment with diffused natural light",
    "clean white studio background with professional lighting",
    "subtle gray gradient backdrop with soft shadows",
    "blurred garden foliage creating natural bokeh effect",
    "neutral beige background suggesting wooden work surface",
    "soft green blurred background evoking greenhouse atmosphere",
    "pure white seamless background with studio lighting",
    "light gray textured background with subtle depth",
    "warm cream background with gentle lighting",
    "soft blue-gray background creating calm atmosphere",
    "natural brown wooden surface slightly out of focus",
    "gentle pastel background with dreamy quality",
    "charcoal gray backdrop with dramatic studio lighting",
    "warm ivory background with soft natural light",
    "cool slate blue background with professional lighting",
    "soft sage green background with botanical feel",
    "delicate lavender-gray background creating elegant atmosphere",
    "warm taupe background with subtle texture",
    "pearl white background with luminous quality",
    "soft mint green blurred background suggesting freshness",
    "muted rose-gray background with romantic feel",
    "natural linen beige background with organic texture",
    "cool silver-gray gradient with modern aesthetic",
    "warm honey-beige background with golden undertones",
    "soft powder blue background creating serene mood"
]

def generate_healthy_roses():
    try:
        num_images = int(input("Enter the number of healthy rose images to generate: "))
    except ValueError:
        print("Invalid number entered.")
        return
    
    log_data = []

    # Distribution: cycle through colors, bloom stages, and angles for maximum variety
    for i in range(num_images):
        color_data = ROSE_COLORS[i % len(ROSE_COLORS)]
        bloom_stage = BLOOM_STAGES[i % len(BLOOM_STAGES)]
        angle = CAMERA_ANGLES[i % len(CAMERA_ANGLES)]
        background = BACKGROUNDS[i % len(BACKGROUNDS)]  # Ahora también cicla por backgrounds
        
        color = color_data['name']
        base_desc = color_data['base_description']
        
        # Enhanced stem description for angles that show stem
        stem_description = ""
        if "stem" in angle['name'].lower() or angle['stem_visibility'] != "minimal or no stem visible":
            stem_description = (
                f"The rose stem is PERFECTLY HEALTHY: smooth, vibrant green stem with natural thickness (4-6mm diameter). "
                f"{angle['stem_visibility']}. "
                f"The stem is FLAWLESS and PRISTINE - no marks, no spots, no discoloration, completely clean. "
                f"Stem has natural organic texture with subtle ridge details and healthy green coloration throughout. "
            )
        
        prompt = (
            f"Ultra-high resolution botanical photography: A PERFECTLY HEALTHY {bloom_stage['stage'].replace('_', ' ')} {color} rose flower "
            f"in PRISTINE CONDITION with ABSOLUTELY NO damage, defects, or imperfections of any kind. "
            f"\n\n"
            f"BLOOM STAGE: {bloom_stage['description']}. "
            f"PETAL STRUCTURE: {bloom_stage['petal_visibility']}. "
            f"\n\n"
            f"CAMERA ANGLE: {angle['description']}. "
            f"FRAMING: {angle['framing']}. "
            f"{stem_description}"
            f"BACKGROUND: {background}. "
            f"Professional greenhouse studio lighting with soft diffusion, creating natural depth and three-dimensional appearance. "
            f"\n\n"
            f"ROSE CHARACTERISTICS: "
            f"The rose has FLAWLESS, IMMACULATE {base_desc} with PERFECT texture and coloration. "
            f"ALL petals are COMPLETELY HEALTHY with smooth, unblemished surfaces. "
            f"Petals show natural color gradients and gentle curves typical of premium quality roses. "
            f"NO damage, NO marks, NO spots, NO discoloration, NO imperfections anywhere on any petal. "
            f"The rose is in PRISTINE EXHIBITION-QUALITY condition - the kind displayed in luxury flower shows. "
            f"\n\n"
            f"PETAL SURFACE: "
            f"Petals have natural matte-to-slight-sheen finish typical of fresh, healthy roses. "
            f"Surface is smooth, clean, and unblemished with beautiful color uniformity. "
            f"Natural petal texture visible with soft, organic curves and perfect edges. "
            f"NO brown spots, NO scratches, NO tears, NO burns, NO discoloration of any kind. "
            f"\n\n"
            f"8K professional macro botanical photography showing PERFECT rose specimen. "
            f"Museum-quality bloom with flawless appearance suitable for botanical illustration. "
            f"Professional composition with depth of field appropriate to the {angle['name'].replace('_', ' ')} angle. "
            f"Sharp focus on the bloom with beautiful bokeh in background areas. "
            f"\n\n"
            f"LIGHTING: Soft, diffused natural light creating gentle shadows and highlighting the natural beauty. "
            f"Perfect exposure showing true color fidelity and petal detail. "
            f"Professional greenhouse or studio lighting setup with no harsh shadows. "
            f"\n\n"
            f"This is a PERFECT, FLAWLESS rose specimen showing ZERO damage or imperfections. "
            f"Every visible part of the rose - petals, stem, leaves if visible - is in PRISTINE condition. "
            f"The rose represents the IDEAL standard of rose quality and beauty. "
            f"\n\n"
            f"STRICTLY AVOID: "
            f"any damage, any spots, any marks, any discoloration, any browning, any tears, any scratches, "
            f"any burns, any lesions, any imperfections, any defects, any flaws, "
            f"fungal growth, gray mold, Botrytis, disease symptoms, infections, "
            f"thrips damage, mechanical damage, chemical burns, physical damage, "
            f"brown edges, brown spots, brown areas, yellow spots, white spots, "
            f"water drops, excessive moisture, wilting, withering, aging, senescence, "
            f"damaged stem, brown stem, spotted stem, scarred stem, "
            f"visible stamens or pistils (unless bloom is at full_bloom stage), "
            f"{bloom_stage['negative_additions']}, "
            f"blurry image, poor focus, low quality, artificial appearance, plastic look, "
            f"unnatural colors, oversaturation, undersaturation, poor lighting. "
            f"\n\n"
            f"Generate a {bloom_stage['stage'].replace('_', ' ')} {color} rose from {angle['name'].replace('_', ' ')} angle "
            f"that is ABSOLUTELY PERFECT with ZERO imperfections - a museum-quality specimen of pristine rose beauty."
        )

        print(f"[{i+1}/{num_images}] Generating HEALTHY {color} at {bloom_stage['stage']}, angle: {angle['name']}...")

        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                    negative_prompt=(
                        "damage, spots, marks, lesions, discoloration, browning, brown spots, brown edges, brown areas, "
                        "scratches, tears, holes, burns, scars, blemishes, imperfections, defects, flaws, "
                        "Botrytis, gray mold, fungal growth, disease, infection, rot, decay, fungus, mildew, "
                        "thrips damage, mechanical damage, chemical burns, physical damage, insect damage, "
                        "wilting, withering, aging, senescence, dying, dead tissue, necrosis, "
                        "water drops (unless natural dew), excessive moisture, waterlogged, "
                        "yellow spots, white spots, black spots, purple spots, discolored areas, "
                        "damaged stem, brown stem, spotted stem, scarred stem, broken stem, "
                        "damaged leaves, spotted leaves, holey leaves, "
                        "visible stamens or pistils (for tight buds and early blooms), "
                        f"{bloom_stage['negative_additions']}, "
                        "blurry, out of focus, low quality, poor resolution, grainy, noisy, "
                        "artificial, fake, plastic, unnatural, CGI, rendered, synthetic, "
                        "oversaturated, undersaturated, wrong colors, poor lighting, harsh shadows, "
                        "multiple flowers, flower bouquet, several roses"
                    )
                )
            )

            for gen_img in response.generated_images:
                filename = f"SanasNew/rose_healthy_{color.split()[0].lower()}_{bloom_stage['stage']}_{angle['name']}_{i+1:04d}.png"
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
                    "condition": "PERFECTLY HEALTHY - ZERO DAMAGE",
                    "quality": "Exhibition-quality pristine specimen",
                    "prompt": prompt
                })
                print(f"  ✓ Saved: {filename}")

            # Rate limiting - wait every 2 images
            if (i + 1) % 2 == 0:
                time.sleep(60)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save log
    if log_data:
        with open('rose_healthy_generation_log.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'rose_color', 'bloom_stage', 'camera_angle', 'angle_description', 'stem_visibility', 'background', 'condition', 'quality', 'prompt'])
            writer.writeheader()
            writer.writerows(log_data)
        
        print(f"\n✓ Generated {len(log_data)} PERFECTLY HEALTHY roses with ZERO damage")
        print(f"✓ Log saved: rose_healthy_generation_log.csv")
        print(f"\n📊 GENERATION SUMMARY:")
        print(f"  Total images: {len(log_data)}")
        print(f"  Unique colors: {len(ROSE_COLORS)}")
        print(f"  Bloom stages: {len(BLOOM_STAGES)}")
        print(f"  Camera angles: {len(CAMERA_ANGLES)}")
        print(f"  Background variations: {len(BACKGROUNDS)}")
        print(f"  All roses: PRISTINE CONDITION - NO DAMAGE")
        
        print("\n🎨 Rose colors included:")
        for color in ROSE_COLORS:
            print(f"  - {color['name']}")
        
        print("\n🌹 Bloom stages included:")
        for stage in BLOOM_STAGES:
            print(f"  - {stage['stage']}: {stage['description'][:60]}...")
        
        print("\n📷 Camera angles included (35 different angles):")
        for angle in CAMERA_ANGLES:
            print(f"  - {angle['name']}: {angle['description'][:70]}...")
            
        print("\n🎨 Backgrounds included (25 different backgrounds):")
        for bg in BACKGROUNDS:
            print(f"  - {bg[:80]}...")
    else:
        print("\n✗ No images generated")

if __name__ == "__main__":
    generate_healthy_roses()