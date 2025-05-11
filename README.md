# Odoo 14 - Material Module

## ✅ Fitur
- CRUD Material
- Validasi harga beli (minimal 100)
- Filter material berdasarkan tipe
- REST API untuk CRUD material
- JWT Auth untuk proteksi endpoint
- Unit testing

## 🐍 Versi Python
Python 3.7+

## 📦 Dependensi (pip)
Library tambahan yang perlu di-install:
```
PyJWT==2.8.0
python-dotenv==1.0.1
```

## ⚙️ Tambahan file environment
Tambahkanan file `.env` di root module:
```
SECRET_KEY=your-secret-key
```

## 🧪 Testing
python odoo-bin -c file_conf -d db_name -i addons_material --test-enable --stop-after-init