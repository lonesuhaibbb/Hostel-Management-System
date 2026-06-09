# 🏨 Hostel Management System

### With Attendance Monitoring & Food Wastage Tracking Using Python

A comprehensive web-based Hostel Management System developed using **Python, Flask, SQLite, HTML, CSS, Bootstrap, and JavaScript**. The system automates hostel administration tasks such as student management, room allocation, attendance tracking, fee management, complaints handling, visitor management, and food wastage monitoring.

---

## 📌 Problem Statement

Traditional hostel management relies heavily on manual registers and paperwork for maintaining student records, attendance, fee details, complaints, visitor logs, and room allocation. This process is time-consuming, error-prone, and difficult to manage efficiently.

The Hostel Management System aims to digitize and automate these operations through a centralized web application.

---

## 🎯 Objectives

* Maintain student records digitally
* Automate room allocation and room tracking
* Manage daily attendance efficiently
* Monitor food wastage and apply fines
* Maintain fee records
* Handle complaints digitally
* Track hostel visitors
* Generate consolidated student information
* Reduce paperwork and administrative workload

---

## 🚀 Key Features

### 👨‍🎓 Student Management

* Add Students
* Edit Student Details
* Delete Students
* Search Students
* View Student Profiles

### 🏠 Room Management

* Room Allocation
* Room Occupancy Tracking
* Available Room Monitoring

### 📅 Attendance Management

* Daily Attendance Marking
* Attendance History
* Attendance Percentage Calculation
* Attendance Reports

### 🍽️ Food Wastage Monitoring

* Record Food Wastage Events
* Categorize Wastage Levels
* Apply Monthly Fine
* Generate Wastage Statistics

### 💰 Fee Management

* Fee Tracking
* Pending Fee Monitoring
* Payment History

### 📝 Complaint Management

* Register Complaints
* Complaint Status Tracking
* Resolution Monitoring

### 👥 Visitor Management

* Visitor Entry Records
* Entry/Exit Tracking
* Visitor History

### 📊 Student 360° Dashboard

A unified student profile displaying:

* Personal Details
* Attendance Records
* Fee Information
* Food Wastage History
* Complaint History
* Visitor Records

---

## 🏗️ System Workflow

### Student Registration

Admin → Add Student → Store in Database → Display in Dashboard

### Attendance Monitoring

Admin → Mark Attendance → Store Attendance → Calculate Percentage → Generate Reports

### Food Wastage Monitoring

Food Wastage Event → Store Record → Calculate Fine → Add to Student Account → Display in Dashboard

### Complaint Management

Complaint Registered → Store Complaint → Update Status → Resolve Complaint

### Visitor Management

Visitor Entry → Store Entry Details → Record Exit → Maintain History

---

## 🛠️ Technology Stack

| Component          | Technology  |
| ------------------ | ----------- |
| Backend            | Python      |
| Framework          | Flask       |
| Database           | SQLite      |
| Frontend           | HTML        |
| Styling            | CSS         |
| UI Framework       | Bootstrap 5 |
| Charts             | Chart.js    |
| Client-side Logic  | JavaScript  |
| Version Control    | Git         |
| Repository Hosting | GitHub      |

---

## 🗄️ Database Tables

* Students
* Rooms
* Attendance
* Fees
* Food Wastage
* Complaints
* Visitors

---

## 📂 Project Structure

```text
Hostel-Management-System/
│
├── app.py
├── database.py
├── requirements.txt
│
├── modules/
│   ├── student.py
│   ├── rooms.py
│   ├── attendance.py
│   ├── fees.py
│   ├── wastage.py
│   ├── complaints.py
│   └── visitors.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── students.html
│   ├── student_profile.html
│   ├── attendance.html
│   ├── rooms.html
│   ├── fees.html
│   ├── complaints.html
│   ├── visitors.html
│   └── wastage.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/aarif-ai/Hostel-Management-System.git
```

### Move into Project Directory

```bash
cd Hostel-Management-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

### Open Browser

```text
http://127.0.0.1:5000
```

---

## 🔮 Future Enhancements

* Student Login Portal
* Parent Dashboard
* Online Fee Payment Gateway
* Face Recognition Attendance
* QR-based Attendance System
* Mobile Application
* AI-powered Analytics Dashboard
* Email & SMS Notifications

---

## 👨‍💻 Team Members

* Aarif Mushtaq
* Suhaib Nazeer
* Abrar Javaid
* Syed Mishar

---

## ❤️ Developed With

Made with ❤️ by **Aarif Mushtaq & Team**

---

## 📜 Academic Information

**Department:** Artificial Intelligence & Data Science
**Project Type:** Minor Project
**Academic Year:** 2025–2026
