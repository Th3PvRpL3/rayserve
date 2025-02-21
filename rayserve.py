import io
import base64
import torch
from ray import serve
from diffusers import StableDiffusionPipeline
import ray

@serve.deployment
class ImageGeneratorv9:
    def __init__(self, device: str = "cuda"):
        self.device = device
        try:
            from diffusers import StableDiffusionPipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16
            )
        except Exception as e:
            raise Exception(f'Error al cargar el modelo: {e}')
        self.pipe.to(device)
 
    async def __call__(self, request):
        """Maneja la solicitud HTTP y genera la imagen."""
        request_data = await request.json()
        prompt, guidance_scale, num_inference_steps = self.decode_request(request_data)
        image = self.predict(prompt, guidance_scale, num_inference_steps)
        return image

    def decode_request(self, request):
        """Extrae parámetros de la solicitud JSON."""
        prompt = request.get("prompt", "A beautiful landscape")
        guidance_scale = request.get("guidance_scale", 7.5)
        num_inference_steps = request.get("num_inference_steps", 50)
        return prompt, guidance_scale, num_inference_steps
    
    def predict(self, prompt, guidance_scale, num_inference_steps):
        """Genera la imagen con Stable Diffusion y la codifica."""
        image = self.pipe(prompt, guidance_scale=guidance_scale, num_inference_steps=num_inference_steps).images[0]
        return self.encode_response(image)

    def encode_response(self, image):
        """Codifica la imagen en Base64 y la devuelve como JSON."""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        # implementar los borrados
        torch.cuda.empty_cache()

        return {"image": img_str}

app = ImageGeneratorv9.bind()
