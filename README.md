# 🎫 TicketMate Backend

TicketMate is a backend ticket management system designed to handle support requests between clients and support teams within an organization.

It enables structured ticket handling, communication, and performance tracking across multiple projects and teams.

---

## 🧭 System Overview

TicketMate supports:

- Multiple projects  
- Multiple clients  
- Multiple support teams  
- Ticket assignment workflows  
- Ticket lifecycle management  
- Ticket discussions  
- File attachments  
- Email notifications  
- Performance analytics  

---

## 🛠 Tech Stack

- **Backend:** Django  
- **API:** Django REST Framework (DRF)  
- **Database:** PostgreSQL  

> ⚠️ Backend-only system (no frontend included)

---

## 👥 User Roles

### 🔑 Admin
- Manage users and roles  
- Create and manage projects  
- Assign teams  
- Monitor system performance  
- Access dashboards  

---

### 📌 Project Owner (PO)
- Receive ticket notifications  
- Assign tickets to employees  
- Communicate with clients  
- Review and close tickets  

---

### 🛠 Support Employee
- Investigate issues  
- Communicate with clients  
- Resolve tickets  
- Update ticket status  

> Employees can belong to multiple projects.

---

### 👤 Client User
- Create support tickets  
- Reply to discussions  
- Upload attachments  
- Track ticket progress  

---

## 🧱 Core Entities

- Users  
- Clients  
- Projects  
- Tickets  
- Messages  
- Attachments  
- Notifications  

---

## 🏢 Project Management

Projects represent service agreements between the company and clients.

### Fields
- Name  
- Client  
- Project Type  
- Project Owner  
- Team Members  

### Project Types
- Oracle Support  
- Software Support  
- Open-Source Support  

---

## 🎫 Ticket System

### Ticket Fields
- Title  
- Description  
- Type  
- Priority  
- Project  

---

### Ticket Types
- Problem  
- Inquiry  
- New Request  

---

### Priority Levels
- Low  
- Medium  
- High  
- Critical  

---

## 🔄 Ticket Lifecycle

### Status Flow
- Todo  
- In Progress  
- Resolved  
- Closed  

### Workflow
1. Client creates ticket  
2. Project Owner is notified  
3. PO assigns ticket  
4. Employee investigates and communicates  
5. Ticket marked as Resolved  
6. PO reviews solution  
7. Ticket is Closed  

> ❗ Closed tickets cannot be edited.

---

## 💬 Ticket Discussion

Each ticket includes a conversation thread:

- Client ↔ Employee communication  
- Internal notes (employees only)  
- Progress updates  
- Clarifications  

---

## 📎 Attachments

Supports file uploads:

- During ticket creation  
- During discussions  

### Examples
- Screenshots  
- Logs  
- Documents  

---

## 🔗 Linked Tickets

- Closed tickets cannot be reopened  
- New tickets can be linked to old ones  
- Helps track recurring issues  

---

## 🔔 Notifications

Triggered when:

- Ticket is created  
- Ticket is assigned  
- Message is added  
- Ticket is resolved  
- Ticket is closed  

### Delivery
- Email  
- System notifications  

---

## 📊 Dashboard & Reporting

### Metrics
- Total tickets  
- Open tickets  
- Resolved tickets  
- Closed tickets  
- Tickets by priority  
- Tickets by project  

---

### Reports
- Tickets per project  
- Tickets per employee  
- Distribution by priority  
- Distribution by type  

---

### Performance
- Average resolution time  
- Employee productivity  
- Ticket activity tracking  

---

## ⏱ Resolution Time

Resolution Time = Resolved Time - Creation Time

---

## 🔐 System Requirements

### Backend
- RESTful API architecture  
- Secure authentication  
- Role-based authorization  
- Scalable storage  
- High availability  
- Notification services  

---

### Security
- Authentication & authorization  
- Role-based access control  
- Data access restrictions  
- Attachment validation  
- Audit logging  

---

## 📌 Key Features

- Multi-project support  
- Multi-client support  
- Role-based access control  
- Ticket lifecycle management  
- Ticket assignment workflow  
- Messaging system  
- Attachment handling  
- Notifications  
- Analytics dashboard  
- Resolution tracking  
- Linked ticket history  

---

## 🚀 Future Enhancements

- SLA management  
- Automated ticket assignment  
- Knowledge base integration  
- Mobile notifications  
- AI-assisted ticket classification  
- Ticket escalation system  

---

## 🧪 User Stories (High Level)

### Admin
- Create and manage projects  
- Assign employees  
- Monitor system performance  

### Project Owner
- Assign tickets  
- Communicate with clients  
- Review and close tickets  

### Employee
- Handle assigned tickets  
- Communicate and resolve issues  

### Client
- Create tickets  
- Upload attachments  
- Track progress  

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/<your-username>/ticketmate.git
cd ticketmate

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
