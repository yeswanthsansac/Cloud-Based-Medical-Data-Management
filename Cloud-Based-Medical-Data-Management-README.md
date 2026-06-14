# 🏥 Cloud-Based Medical Data Management

A **secure, cloud-deployed** medical records management system with role-based access control, AES-256 + SHA-256 encryption, and geo-location authentication for healthcare data protection.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20RDS-FF9900?style=flat&logo=amazon-aws&logoColor=white)
![Encryption](https://img.shields.io/badge/Encryption-AES%20%7C%20SHA--256-green?style=flat&logo=shield&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🔑 Key Features

| Feature | Implementation |
|---------|---------------|
| **🔐 AES-256 Encryption** | Patient records encrypted via Fernet (AES + SHA-256) before storage |
| **📍 Geo-Location Login** | Admin decryption access restricted by geographic location |
| **👥 Role-Based Access** | 3-tier access: Admin, Nurse, Doctor with least-privilege principle |
| **☁️ Cloud Storage** | MySQL database hosted on cloud infrastructure |
| **🔔 Future Notify** | Notification system for patient report updates |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Admin      │────▶│                  │────▶│   MySQL     │
│   Dashboard  │     │                  │     │   Database  │
└─────────────┘     │                  │     │  (Cloud)    │
                    │   Django App     │     └─────────────┘
┌─────────────┐     │   on AWS EC2     │          ▲
│   Nurse      │────▶│                  │          │
│   Portal     │     │  ┌────────────┐  │     ┌────┴────┐
└─────────────┘     │  │ Fernet     │  │     │ AES-256  │
                    │  │ Encryption  │  │     │ Encrypted│
┌─────────────┐     │  └────────────┘  │     │ Records  │
│   Doctor     │────▶│                  │     └─────────┘
│   Portal     │     │  ┌────────────┐  │
└─────────────┘     │  │ Geo-Login  │  │
                    │  │ Auth Check  │  │
                    │  └────────────┘  │
                    └──────────────────┘
```

## 🔐 Security Flow

1. **Nurse** logs in → Records patient vitals → **AES-256 encryption** → Store in MySQL
2. **Doctor** logs in → Request patient report → **Geo-location verified** → Decrypt with key → View report
3. **Admin** logs in → Manage users → Allot patients → **Geo-login required** for sensitive operations

## 👥 User Roles & Permissions

| Action | Admin | Nurse | Doctor |
|--------|:-----:|:-----:|:------:|
| Manage Users | ✅ | ❌ | ❌ |
| Allot Patients | ✅ | ❌ | ❌ |
| Record Vitals | ❌ | ✅ | ❌ |
| View Reports | ❌ | ❌ | ✅ |
| Geo-Login Required | ✅ | ❌ | ✅ |

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Python, Django Framework |
| **Database** | MySQL (Cloud-hosted) |
| **Encryption** | Fernet (AES-256 + SHA-256) |
| **Authentication** | Geo-location based + Role-based |
| **Cloud** | AWS (EC2, RDS) |
| **Frontend** | HTML, CSS |

---

## 🚀 How to Run

### Prerequisites
- Python 3.x
- MySQL Server
- AWS Account (for cloud deployment)

### Local Setup
```bash
# Clone the repository
git clone https://github.com/yeswanthsansac/Cloud-Based-Medical-Data-Management.git

# Navigate to project directory
cd Cloud-Based-Medical-Data-Management/Doctor_patient_geographics\ full/

# Install dependencies
pip install django cryptography mysql-connector-python

# Set up MySQL database
# (Configure settings.py with your database credentials)

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### AWS Deployment
```bash
# Launch EC2 instance (Ubuntu)
# Install Python, Django, MySQL on EC2
# Configure Security Groups for HTTP/HTTPS
# Deploy using Gunicorn + Nginx
```

---

## 📸 Screenshots

<!-- ADD YOUR SCREENSHOTS HERE -->
<!-- Example: -->
<!-- ![Login Page](screenshots/login.png) -->
<!-- ![Admin Dashboard](screenshots/admin-dashboard.png) -->
<!-- ![Encrypted Records](screenshots/encrypted-records.png) -->

---

## 📁 Project Structure

```
Cloud-Based-Medical-Data-Management/
├── Doctor_patient_geographics full/
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   ├── templates/
│   │   ├── admin_dashboard.html
│   │   ├── nurse_portal.html
│   │   └── doctor_portal.html
│   └── ...
└── README.md
```

---

## 📜 License

This project is licensed under the MIT License.

---

## 👤 Author

**Yeswanth P**
- 📧 yeswanthyeswanth23@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/yeswanth-p-4b216a206)
- 🐙 [GitHub](https://github.com/yeswanthsansac)

---

> ⚠️ **Note:** This project handles sensitive medical data. Ensure proper HIPAA compliance and security measures before deploying in production.
