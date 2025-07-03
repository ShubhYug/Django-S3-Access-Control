# Django-S3-Access-Control
A Django REST API to browse, upload, and delete AWS S3 objects with per-user access control using Django’s built-in auth system.

# Django S3 Access Control

This is a Django-based REST API application that provides a simple S3 browser to manage AWS S3 buckets. It uses Django's authentication system to assign user-level permissions (view, upload, delete) per bucket.

## 🔐 Features

- User authentication via Django's built-in system
- S3 bucket configuration via Django Admin
- Per-user S3 permissions: `can_view`, `can_upload`, `can_delete`
- REST API to:
  - List allowed buckets
  - Browse objects in allowed buckets
  - Upload files to authorized buckets
  - Delete files from authorized buckets
- Permissions are enforced strictly on the server side

## 🖥️ UI Usage Instructions
This project also includes an HTML interface (UI) for users to interact with S3 buckets. Here's how to access and use it:

### 🔐 1. Login
Navigate to: http://localhost:8000/login/

Enter your Django username and password.

Upon successful login, you will be redirected to the S3 bucket browser page.

### 📂 2. View Buckets
After login, you will see a list of S3 buckets you have permission to view (can_view=True).

Each bucket will display a list of objects stored within it.

### 📤 3. Upload a File
Each bucket card contains an upload form.

Choose a file using the file picker.

Click the Upload button.

If you have can_upload=True permission for that bucket, the file will be uploaded to S3.

### 🗑️ 4. Delete a File
Next to each listed object, you will find a Delete button.

Click it and confirm deletion in the popup.

If you have can_delete=True permission, the object will be deleted from the bucket.

### 🚪 5. Logout
Click the Logout button in the top-right corner to safely end your session.


## ⚙️ Setup Instructions

### 1. Create and Activate Virtual Environment
```
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```
pip install -r requirements.txt

```
### 3. Set Environment Variables
Create a .env file in the project root
```
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```
### 4. Run Migrations
```
python manage.py makemigrations
python manage.py migrate
```
### 5. Create Superuser (for Admin UI)
```
python manage.py createsuperuser
```
Then login at:
```
http://127.0.0.1:8000/admin/
```

### 🔌 API Endpoints
Method	URL	Description
```
GET	/api/buckets/	List buckets the user can view
GET	/api/buckets/<bucket_id>/objects/	List objects in a bucket
POST	/api/buckets/<bucket_id>/upload/	Upload a file to a bucket
DELETE	/api/buckets/<bucket_id>/objects/<key>/
```
### 🔐 Permission Enforcement
All access is restricted via BucketPermission.
If a user is not granted:
    can_view,
    can_upload,
    can_delete, 
    their request will return 403 Forbidden.

### 🧪 Testing via Postman
Use cookie-based session auth or pass Authorization: Token <your-token> if using token auth.

For file upload, use POST to:

```
/api/buckets/<bucket_id>/upload/
```
With form-data body:
```
file: <select your file>
```
### ✅ Set These Headers in Postman:
Header Key	Value
```
Cookie	sessionid=<your-session-id>; 
csrftoken=<your-csrf-token>
X-CSRFToken	<your-csrf-token>
```
### 📝 Example:
```
Cookie: sessionid=ykqkex8c4c9ipl4kdbqite1emhpx9yq7; csrftoken=3BWP2caHlXMEpdw2yxqUHf9TQdh2t3OB
X-CSRFToken: 3BWP2caHlXMEpdw2yxqUHf9TQdh2t3OB
```

### 🔎 How to Get These:
```
Log in to your Django app via web browser (e.g., http://127.0.0.1:8000/admin/).

Right-click → Inspect → Go to Network Tab.

Refresh the page or login — then click on any request (e.g., /admin/).

Under Request Headers:

Find Cookie header → Copy the whole string.

Find X-CSRFToken under Form Data or headers if available.
```

### 📦 In Postman – Set:
```
Method: POST

URL: http://127.0.0.1:8000/api/buckets/<bucket_id>/upload/

Body: form-data

    key = file

    value = <choose a file>

Headers:

    Cookie: your cookie string

    X-CSRFToken: csrf token from cookie
```
    