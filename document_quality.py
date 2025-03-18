import os
import requests
from dotenv import load_dotenv

load_dotenv()

VISION_API_KEY = os.getenv("VISION_API_KEY")
VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")


def check_image_quality(image_bytes):
    """
    Check image quality using Azure Vision API with supported features.
    Returns quality assessment metrics.
    """
    try:
        # Update to use supported visual features
        # According to Azure docs, valid features include: Categories, Brands, Adult, Faces, Objects, Tags, Description, Color
        headers = {
            "Ocp-Apim-Subscription-Key": VISION_API_KEY,
            "Content-Type": "application/octet-stream",
        }

        params = {
            "visualFeatures": "Adult,Faces,Objects,Tags",  # Using supported features instead of Quality
        }

        response = requests.post(
            f"{VISION_ENDPOINT}/vision/v3.2/analyze",
            headers=headers,
            params=params,
            data=image_bytes,
        )

        if response.status_code != 200:
            return {"success": False, "error": response.json(), "qualityScore": 0}

        response_data = response.json()

        # Create our own quality score based on available metrics
        quality_score = 1.0  # Start with perfect score

        # Reduce score if image has low tag confidence (indicating potential poor quality)
        tags = response_data.get("tags", [])
        if tags:
            avg_confidence = sum(tag.get("confidence", 0) for tag in tags) / len(tags)
            quality_score *= avg_confidence

        # Reduce score if faces are detected but unclear (small, blurry)
        faces = response_data.get("faces", [])
        if faces:
            face_area_ratio = sum(
                face.get("faceRectangle", {}).get("width", 0)
                * face.get("faceRectangle", {}).get("height", 0)
                for face in faces
            ) / (
                1024 * 768
            )  # Normalized to common resolution
            # If face is too small, reduce quality score
            if face_area_ratio < 0.05:  # Arbitrary threshold
                quality_score *= 0.8

        # Reduce score if adult content detected (inappropriate document)
        adult_content = response_data.get("adult", {})
        if adult_content.get("isAdultContent", False) or adult_content.get(
            "isRacyContent", False
        ):
            quality_score *= 0.5

        # Final quality assessment
        is_acceptable = quality_score >= 0.6  # Arbitrary threshold

        return {
            "success": True,
            "is_acceptable": is_acceptable,
            "qualityScore": quality_score,
            "raw_response": response_data,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "qualityScore": 0,
            "is_acceptable": False,
        }
