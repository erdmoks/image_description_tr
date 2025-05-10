import requests
import json

def get_direction_from_ai(image_data):
    api_url = "APIURL"
    api_key = "APIKEY"

    img_width = image_data["width"]
    img_height = image_data["height"]
    detections = image_data.get("detections", [])

    if not detections:
        return "Görüntüde nesne tespit edilemedi."

    objects = []
    for det in detections:
        class_name = det["class_name"]
        confidence = det["confidence"]
        xmin, ymin, xmax, ymax = det["xmin"], det["ymin"], det["xmax"], det["ymax"]
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2

        objects.append({
            "name": class_name,
            "x": center_x,
            "y": center_y,
            "confidence": confidence
        })

    relations = []
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i >= j:
                continue
            dx = obj2["x"] - obj1["x"]
            dy = obj2["y"] - obj1["y"]

            relation = ""
            if abs(dx) > abs(dy):
                if dx > 0:
                    relation = f"{obj2['name']} {obj1['name']}'nin sağında"
                else:
                    relation = f"{obj2['name']} {obj1['name']}'nin solunda"
            else:
                if dy > 0:
                    relation = f"{obj2['name']} {obj1['name']}'nin altında"
                else:
                    relation = f"{obj2['name']} {obj1['name']}'nin üstünde"

            relations.append(relation)


    relation_text = ", ".join(relations)
    object_names = ", ".join([obj["name"] for obj in objects])

    prompt = f"""
Bir sahne analiz edildi. Aşağıda sahnedeki nesneler ve konum ilişkileri verilmiştir:

- Tespit edilen nesneler: {object_names}
- Nesnelerin birbirine göre konumları: {relation_text}

Bu bilgilere dayanarak sahneyi **gerçekçi, kısa ve anlamlı bir şekilde tarif et**.
Çıktın **30 kelimeyi geçmemeli**, sadece sahneye dair betimleyici bir cümle olsun.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "MODEL",
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result.get("choices", [{}])[0].get("text", "Yanıt alınamadı.")
    else:
        return f"Hata: {response.status_code} - {response.text}"
