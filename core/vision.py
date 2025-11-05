import os
import cv2
import google.generativeai as genai
from PIL import Image
import io

class Vision:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        self.camera = None

    def _initialize_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.camera = None
                raise ConnectionError("Could not open webcam.")

    def capture_image(self):
        self._initialize_camera()
        ret, frame = self.camera.read()
        if not ret:
            raise IOError("Could not capture image from webcam.")
        return frame

    def analyze_image(self, frame, prompt):
        # Convert the OpenCV frame (BGR) to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the numpy array to a PIL Image
        pil_img = Image.fromarray(rgb_frame)
        
        # Prepare the image for the API
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='JPEG')
        
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": img_byte_arr.getvalue()
            }
        ]
        
        prompt_parts = [image_parts[0], f"\n{prompt}"]
        
        response = self.model.generate_content(prompt_parts)
        
        if response.parts:
            return response.text
        else:
            # Handle cases where the response might be blocked or empty
            return "I'm sorry, I was unable to analyze the image. The response may have been blocked for safety reasons."

    def release_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

vision_agent = Vision()

def get_vision_agent():
    return vision_agent
