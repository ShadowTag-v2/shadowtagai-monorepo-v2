from examples.stable_diffusion import StableDiffusion
from tinygrad.device import Device
from tinygrad.helpers import Timing, fetch
from tinygrad.nn.state import load_state_dict, torch_load

# run "sudo purge" before testing on OS X to avoid the memory cache

if __name__ == "__main__":
  fn = fetch('https://huggingface.co/CompVis/stable-diffusion-v-1-4-original/resolve/main/sd-v1-4.ckpt', 'sd-v1-4.ckpt')
  model = StableDiffusion()
  with Timing():
    load_state_dict(model, torch_load(fn)['state_dict'], strict=False)
    Device[Device.DEFAULT].synchronize()
