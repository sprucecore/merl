import os, requests, base64, mimetypes
from pygltflib import GLTF2

GLB_URL = "https://xsvabundleprod-c4b3d4etadb8dxha.b02.azurefd.net/assets/models/Merl_Workshop_01.glb"
ATLAS_FILE_NAME = "workshopTextureAtlas"

# --- Download GLB ---
response = requests.get(GLB_URL)
response.raise_for_status()

# Save the GLB file temporarily
temp_glb_path = "temp.glb"
with open(temp_glb_path, "wb") as f:
    f.write(response.content)

try:
    # --- Load GLB ---
    gltf = GLTF2().load(temp_glb_path)
    # --- Find and extract texture atlas ---
    for image in gltf.images:
        if image.name == ATLAS_FILE_NAME:
            print(f"Found it! The mime type is {image.mimeType}")
            # Case 1: Embedded as base64 URI
            if image.uri and image.uri.startswith("data:"):
                _, data = image.uri.split(",", 1)
                image_bytes = base64.b64decode(data)

            # Case 2: Stored in bufferView (most common for GLB)
            elif image.bufferView is not None:
                buffer = gltf.binary_blob()
                bv = gltf.bufferViews[image.bufferView]
                image_bytes = buffer[
                    bv.byteOffset : bv.byteOffset + bv.byteLength
                ]

            else:
                raise RuntimeError("Unsupported image storage")

            with open(ATLAS_FILE_NAME + mimetypes.guess_extension(image.mimeType), "wb") as f:
                f.write(image_bytes)

            print(f"{ATLAS_FILE_NAME} extracted")
            break
    else:
        print(f"{ATLAS_FILE_NAME} not found")

finally:
    # Delete the temporary GLB file
    if os.path.exists(temp_glb_path):
        os.remove(temp_glb_path)
        print(f"Deleted temporary file: {temp_glb_path}")
