import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import Category

CATS = [
    ("Barcode Scanner", "barcode-scanner"),
    ("Cabinet", "cabinet"),
    ("Cables", "cables"),
    ("CCTV Items", "cctv-items"),
    ("Finger Print Reader", "finger-print-reader"),
    ("Graphics Card", "graphics-card"),
    ("Hard Disc", "harddisc"),
    ("Headphone", "headphone"),
    ("Keyboard / Mouse", "keyboard-mouse"),
    ("Laptop / Desktop", "laptop-desktop"),
    ("Memory", "memory"),
    ("Monitor", "monitor"),
    ("Motherboard", "motherboard"),
    ("Networking Products", "networking-products"),
    ("Pendrive", "pendrive"),
    ("Printers", "printers"),
    ("Processor", "processor"),
    ("SSD (Ext / Int)", "ssd"),
    ("UPS / Battery", "ups-battery"),
]

for name, slug in CATS:
    obj, made = Category.objects.get_or_create(slug=slug, defaults={'name': name})
    print(('created  ' if made else 'exists   ') + name)