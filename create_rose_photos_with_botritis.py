import random
import csv
import time
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# --- Configuration ---
PROJECT_ID = "thesisprojectai" 
LOCATION = "us-central1"
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# COMPLETELY REVISED DESCRIPTIONS - Avoiding ALL 3D-triggering words
ROSE_DATA = [
    {
        "rose": "White (Vendela)", 
        "description": "white rose petals with a few tiny circular pinkish-red pigmentation anomalies",
        "detail": "isolated small circular pink discolorations, each measuring precisely under 0.3 millimeters in diameter, placed far apart across the white petal surface like tiny freckles or pin-drop sized watercolor stains that have soaked into paper, perfectly round to slightly oval in shape, creating a localized pattern",
        "color_effect": "tiny round rose-pink tissue spots on ivory white background",
        "size_emphasis": "Each discolored circle is under 0.3 millimeters - the size of a ballpoint pen dot or small freckle",
        "flatness_key": "The pinkish-red spots are completely matte and flat - NOT glossy, NOT wet-looking, NOT water drops"
    },
    {
        "rose": "Deep Red (Explorer)", 
        "description": "deep crimson rose petals with a couple of tiny circular pale beige depigmented areas",
        "detail": "a single solitary small round spots where red pigment has faded, each under 0.3 millimeters in diameter (micro-pinpoint size), creating whitish-tan circular patches like miniature bleached dots, perfectly circular and appearing far apart, resembling tiny pale freckles on dark red skin",
        "color_effect": "minuscule round ghost-like circles on burgundy red background",
        "size_emphasis": "Each pale circle is under 0.3 millimeters - microscopic size, like the sharp tip of a needle",
        "flatness_key": "The pale beige circles are completely matte and flat - NOT glossy, NOT wet-looking, NOT water drops"
    },
    {
        "rose": "Yellow (St. Patrick)", 
        "description": "bright yellow rose petals with rare tiny circular bronze-brown discolored pigmentation stains absorbed into the tissue",
        "detail": "extremely subtle and rare small round oxidized areas, each under 0.3 millimeters in diameter, appearing as flat brownish circular pigment changes completely fused with the petal surface, like microscopic matte age spots on dry skin, scattered across the yellow surface",
        "color_effect": "tiny round bronze-brown oxidized circles on golden yellow background",
        "size_emphasis": "Each brown mark is under 0.3 millimeters - extremely small, like tiny specks of flat matte dust or dried watercolor dye absorbed into paper",
        "flatness_key": "CRITICAL: The bronze-brown areas have ZERO HEIGHT and NO RELIEF. They are completely flush with the petal surface, matte, and absorbed into the tissue - absolutely no raised bumps, no spheres, no glossy beads."
    },
    {
        "rose": "Orange (Movie Star)", 
        "description": "vibrant orange rose petals with a couple of isolated tan-brown pigmented regions",
        "detail": "the orange petals show one or two under 0.3 millimeters pigment-darkened areas where the tissue has a brownish-tan appearance with faint yellowish edges, appearing as if the orange dye has oxidized or faded in tiny circular zones, creating flat matte spots like sun-faded circles on orange fabric",
        "color_effect": "matte tan-brown pigment darkening on coral orange background",
        "size_emphasis": "Each pigment-darkened area is under 0.3 millimeters - the size of a small peppercorn",
        "flatness_key": "The tan-brown areas are completely matte and flat - NOT glossy, NOT wet-looking, NOT water drops"
    },
    {
        "rose": "Peach", 
        "description": "delicate peach rose petals with barely visible tiny circular pinkish spots",
        "detail": "extremely subtle and rare round pink discolorations, each under 0.3 millimeters in diameter (nearly imperceptible), like the faintest circular watercolor wash absorbed into tissue, almost invisible tiny round marks that blend with the petal",
        "color_effect": "barely visible tiny round pink circles on soft peach background",
        "size_emphasis": "Each pink circle is under 0.3 millimeters - barely visible, like dust specks or pin pricks",
        "flatness_key": "The tiny pink spots are completely matte and flat - NOT glossy, NOT wet-looking, NOT water drops"
    },
    {
        "rose": "Pink (Rosa)", 
        "description": "pink rose petals with sparse circular darker brownish-maroon zones",
        "detail": "a pair of round pigment-concentrated areas, each under 0.3 millimeters in diameter, appearing as tiny circular regions where pigment is more intense, creating darker burgundy-brown circles with intensified pink halos at edges, perfectly round like small circular ink stains",
        "color_effect": "small round dark maroon circles with pink halos on rose pink background",
        "size_emphasis": "Each dark circle is under 0.3 millimeters - the size of a sesame seed or small match head",
        "flatness_key": "The dark maroon circles are completely matte and flat - NOT glossy, NOT wet-looking, NOT water drops"
    }
]

# NEW: Bloom stages based on the document's emphasis on latent infections during development
BLOOM_STAGES = [
    {
        "stage": "tight_bud",
        "description": "completely closed tight bud, sepals still wrapping around the petals, NO petal separation visible, compact oval shape",
        "petal_visibility": "petals entirely enclosed within green sepals, only the very tips of outer petals barely emerging, bud appears as a compact teardrop or egg shape",
        "structure_emphasis": "The rose is NOT open at all - it's a closed bud. Sepals are the dominant visible feature. The flower has not begun to bloom yet.",
        "negative_additions": "fully opened petals, separated petals, visible flower center, bloomed rose, open rose"
    },
    {
        "stage": "early_opening",
        "description": "bud just starting to crack open, outer petals beginning to peel back but still tightly furled, approximately 15-25% open, petals remain compressed and curled inward",
        "petal_visibility": "only 2-3 outer petal layers starting to loosen and separate, inner petals still completely hidden and tightly wrapped, overall shape still narrow and vertical",
        "structure_emphasis": "The rose is BARELY opening - most petals are still tightly compressed against each other. The bud shape is still dominant. NOT a recognizable rose form yet.",
        "negative_additions": "fully bloomed, wide open petals, horizontal petal spread, classic rose shape, all petals visible"
    },
    {
        "stage": "half_bloom",
        "description": "rose at 40-50% bloom, outer petals clearly separated and beginning to curve outward, inner petals still partially furled but becoming visible, recognizable rose shape emerging but compact",
        "petal_visibility": "outer 3-4 petal layers open and distinct, middle layers visible but still curved inward, innermost petals remain concealed, flower width approximately 60-70% of full size",
        "structure_emphasis": "The rose is PARTIALLY open - it has a recognizable rose form but is NOT fully expanded. Many inner petals are still hidden. The flower appears medium-tight.",
        "negative_additions": "completely open, fully expanded, all petals visible, flat horizontal petals, maximum bloom"
    },
    {
        "stage": "full_bloom",
        "description": "completely opened mature rose showing full petal expansion, all layers unfurled and spread outward, classic open rose form",
        "petal_visibility": "all petal layers fully expanded, separated, and visible from outer to inner, petals spread wide creating maximum diameter and horizontal orientation",
        "structure_emphasis": "The rose is FULLY open - maximum expansion, all petals visible, classic bloomed rose appearance.",
        "negative_additions": "closed bud, tight petals, furled petals, compressed form"
    }
]

def generate_botrytis_images():
    try:
        num_images = int(input("Enter the number of images to generate: "))
    except ValueError:
        print("Invalid number entered.")
        return

    angles = [
        "straight-on frontal view",
        "30-degree angled perspective", 
        "gentle overhead angle"
    ]
    
    log_data = []

    # Distribution logic
    per_color = num_images // len(ROSE_DATA)
    remainder = num_images % len(ROSE_DATA)
    selected_varieties = ROSE_DATA * per_color + random.sample(ROSE_DATA, remainder)

    for i, item in enumerate(selected_varieties):
        color = item['rose']
        description = item['description']
        detail = item['detail']
        color_effect = item['color_effect']
        angle = random.choice(angles)
        
        # NEW: Randomly select a bloom stage
        bloom_stage = random.choice(BLOOM_STAGES)
        
        # ULTRA-REVISED PROMPT - Eliminating ALL water/liquid associations + BLOOM STAGE
        prompt = (
            f"Ultra-high resolution botanical photography: A {bloom_stage['stage'].replace('_', ' ')} {color} rose flower. "
            f"CRITICAL BLOOM STAGE REQUIREMENT: {bloom_stage['description']}. "
            f"STRUCTURAL MANDATE: {bloom_stage['structure_emphasis']}. "
            f"PETAL CONFIGURATION: {bloom_stage['petal_visibility']}. "
            f"Photographic angle: {angle}. Professional greenhouse studio lighting with soft diffusion. "
            f"8K macro photography of rose PETALS with completely DRY, MATTE surface. "
            f"The rose petals must have a uniformly DRY, VELVETY, NON-REFLECTIVE surface texture. "
            f"A full-view, medium shot of a single rose at precisely {bloom_stage['stage'].replace('_', ' ')} stage, showing the flower head clearly from a comfortable distance. "
            f"The rose is captured in a professional flower farm setting, with a blurred vista of a vast rose cultivation field under bright daylight. "
            f"\n\n"
            f"PETAL APPEARANCE: {description}. "
            f"The rose petals are COMPLETELY DRY with absolutely NO moisture, NO wetness, NO glossiness anywhere. "
            f"\n\n"
            f"PIGMENTATION PATTERN: {detail}. "
            f"SIZE REFERENCE: {item['size_emphasis']}. "
            f"VISUAL EFFECT: {color_effect}. "
            f"NUMBER OF MARKS: Maximum 3 to 7 total across the visible petals. "
            f"\n\n"
            f"CRITICAL FLATNESS AND DRYNESS MANDATE: {item['flatness_key']}. "
            f"The pigmented areas are PRINTED INTO the petal tissue like ink on paper or dye on fabric. "
            f"They are COMPLETELY FLAT - zero height, zero depth, zero relief, zero bumps. "
            f"They are COMPLETELY MATTE - zero gloss, zero shine, zero reflectivity, zero wetness. "
            f"They are COMPLETELY DRY - no liquid appearance, no water, no moisture, no dew. "
            f"\n\n"
            f"The entire petal surface including the pigmented areas is uniformly: "
            f"- DRY (like paper, not wet) "
            f"- MATTE (like velvet, not glossy) "
            f"- FLAT (like printed fabric, not textured) "
            f"- SMOOTH (like skin, not bumpy) "
            f"\n\n"
            f"THINK: Printed polka dots on matte fabric, freckles on dry skin, ink stains on paper, "
            f"food coloring absorbed into cake, dye marks on cloth, age spots on dry leaves. "
            f"NOT: Water drops, dewdrops, liquid beads, wet spots, glossy marks, raised bumps. "
            f"\n\n"
            f"The pigmented marks have NO dimensional properties - they exist only as color variations "
            f"on a perfectly smooth, dry, matte petal surface. If photographed in grazing light, "
            f"they would cast NO shadows because they have NO height. "
            f"\n\n"
            f"BLOOM STAGE VERIFICATION: This rose must be at {bloom_stage['stage'].replace('_', ' ')} stage, NOT more open, NOT less open. "
            f"\n\n"
            f"STRICTLY AVOID: Any appearance of water, moisture, wetness, dew, droplets, liquid, "
            f"glossiness, shine, reflections, wet-looking surfaces, moist areas, condensation, "
            f"stamens, pistils, flower center structures, seed pods, "
            f"three-dimensional features, raised bumps, protrusions, ridges, texture relief, "
            f"convex shapes, spherical forms, dimensional objects of any kind, "
            f"{bloom_stage['negative_additions']}. "
            f"Show only DRY, MATTE rose petals with FLAT pigment variations at EXACTLY {bloom_stage['stage'].replace('_', ' ')} stage."
        )

        print(f"[{i+1}/{num_images}] Generating {color} at {bloom_stage['stage']} stage with flat tissue pigmentation...")

        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1",
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                    negative_prompt=(
                        "water, water drops, water droplets, dew, dewdrops, moisture, wet, wetness, damp, "
                        "liquid, drops, droplets, condensation, rain, raindrops, mist, spray, "
                        "glossy, shiny, reflective, gloss, shine, wet-looking, moist-looking, "
                        "translucent spheres, liquid beads, gel, resin, epoxy, glue, "
                        "stamens, pistils, flower center, anthers, pollen, seed pod, "
                        "three-dimensional, 3D, raised, bumps, protrusions, ridges, relief, "
                        "convex, spherical, rounded, bubbles, balls, beads, spheres, pellets, "
                        "dimensional features, textured surface, rough texture, bumpy, "
                        f"anything with height, anything that casts shadows, anything glossy, "
                        f"{bloom_stage['negative_additions']}"
                    )
                )
            )

            for gen_img in response.generated_images:
                filename = f"botrytis_flat_{color.split()[0].lower()}_{bloom_stage['stage']}_{i+1:03d}.png"
                img = Image.open(BytesIO(gen_img.image.image_bytes))
                img.save(filename)
                log_data.append({
                    "filename": filename, 
                    "rose": color,
                    "bloom_stage": bloom_stage['stage'],
                    "description": description,
                    "prompt": prompt
                })
                print(f"  ✓ Saved: {filename}")

            if i % 2:
                time.sleep(60)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save log
    if log_data:
        with open('botrytis_flat_generation_log.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'rose', 'bloom_stage', 'description', 'prompt'])
            writer.writeheader()
            writer.writerows(log_data)
        
        print(f"\n✓ Generated {len(log_data)} images with flat tissue discoloration across different bloom stages")
        print(f"✓ Log: botrytis_flat_generation_log.csv")
        print("\nEnhanced approach:")
        print("- Added 4 bloom stages (tight bud → full bloom)")
        print("- Reflects latent infection establishment during development")
        print("- Maintains all existing prompt quality")
        print("- Based on document's pathological cycle")
    else:
        print("\n✗ No images generated")

if __name__ == "__main__":
    generate_botrytis_images()
