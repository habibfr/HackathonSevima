from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import hashlib

def compress_image(image: Image.Image, n_colors=16):
    img = image.convert("RGB")
    np_img = np.array(img)
    h, w = np_img.shape[:2]
    flat_img = np_img.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors).fit(flat_img)
    compressed = kmeans.cluster_centers_[kmeans.labels_].reshape(h, w, 3).astype("uint8")
    return Image.fromarray(compressed)

def gen_thumbnail(image: Image.Image, thumbnail_size=(128, 128)):
    thumbnail = image.copy()
    thumbnail.thumbnail(thumbnail_size)
    return thumbnail


def hash_filename_thumbnail(filename):
    return hashlib.md5(filename.encode()).hexdigest()